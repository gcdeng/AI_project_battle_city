'''version:
	ai_projectV5
'''
import random
import time
import multiprocessing
import heapq
import Queue

class ai_agent():
	mapinfo = []
	def __init__(self):
		self.mapinfo = []

	# rect:					[left, top, width, height]
	# rect_type:			0:empty 1:brick 2:steel 3:water 4:grass 5:froze
	# castle_rect:			[12*16, 24*16, 32, 32]
	# mapinfo[0]: 			bullets [rect, direction, speed]]
	# mapinfo[1]: 			enemies [rect, direction, speed, type]]
	# enemy_type:			0:TYPE_BASIC 1:TYPE_FAST 2:TYPE_POWER 3:TYPE_ARMOR
	# mapinfo[2]: 			tile 	[rect, type] (empty don't be stored to mapinfo[2])
	# mapinfo[3]: 			player 	[rect, direction, speed, Is_shielded]]
	# shoot:				0:none 1:shoot
	# move_dir:				0:Up 1:Right 2:Down 3:Left 4:None
	# keep_action:			0:The tank work only when you Update_Strategy. 	1:the tank keep do previous action until new Update_Strategy.

	# def Get_mapInfo:		fetch the map infomation
	# def Update_Strategy	Update your strategy

	def operations (self, p_mapinfo, c_control):
		(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT, DIR_NONE) = range(0, 5)
		self.unit = 16.0
		grid_unit = 26

		self.all_grid = []
		for i in range(grid_unit):
			for j in range(grid_unit):
				self.all_grid.append((i, j))

		while True:
		#-----your ai operation,This code is a random strategy,please design your ai !!-----------------------
			self.Get_mapInfo(p_mapinfo)
			# print "bullets: ", self.mapinfo[0]

			'''get player rect'''
			# print "player: ", self.mapinfo[3][0]
			# self.mapinfo[3][0][2] = 100
			self.player_x = 0
			self.player_y = 0
			self.get_player_rect()
			# print "player: ({}, {})".format(self.player_x, self.player_y)

			'''get enemy rect'''
			if self.mapinfo[1]:
				# print "enemies: ", self.mapinfo[1][0]
				self.enemy_x = 0
				self.enemy_y = 0
				self.get_enemy_rect()
				# print "enemy: ", self.enemy_x, self.enemy_y

			'''get tile rect'''
			# print "tile: ", self.mapinfo[2][0]
			self.walls = []
			self.get_walls()
			# print self.walls

			'''find path by A star'''
			path = []
			if self.mapinfo[1]:
				aStar = Astar()
				aStar.init_grid(grid_unit, grid_unit, self.walls, (self.player_x, self.player_y), (self.enemy_x, self.enemy_y))
				path = aStar.solve()
				# print "Path: ", path

			'''shoot'''
			shoot = 1
			# shoot enemy when parallel
			# if self.mapinfo[1]:
			# 	if self.player_x == self.enemy_x or self.player_y == self.enemy_y:
			# 		shoot = 1

			'''move direction'''
			move_dir = DIR_NONE
			if path:
				if self.player_y > path[1][1]:
					move_dir = DIR_UP
				if self.player_x < path[1][0]:
					move_dir = DIR_RIGHT
				if self.player_y < path[1][1]:
					move_dir = DIR_DOWN
				if self.player_x > path[1][0]:
					move_dir = DIR_LEFT

			'''dodge bullet'''
			bullet_distance = 100
			if self.mapinfo[0]:
				for i in range(len(self.mapinfo[0])):
					if (self.mapinfo[0][i][0].left in range(self.mapinfo[3][0][0].left, self.mapinfo[3][0][0].left+bullet_distance)) and self.mapinfo[0][i][1] == DIR_LEFT:
						move_dir = DIR_DOWN
						if self.player_y in range(21, 26) or (self.player_x, self.player_y+2) in self.walls:
							move_dir = DIR_UP
						elif self.mapinfo[0][i][0].top in range(self.mapinfo[3][0][0].top-5, self.mapinfo[3][0][0].top+5):
							move_dir = DIR_RIGHT
							# shoot = 1
						break

				# for i in range(len(self.mapinfo[0])):
					if (self.mapinfo[0][i][0].left in range(self.mapinfo[3][0][0].left-bullet_distance, self.mapinfo[3][0][0].left)) and self.mapinfo[0][i][1] == DIR_RIGHT:
						move_dir = DIR_DOWN
						if self.player_y in range(21, 26) or (self.player_x, self.player_y+2) in self.walls:
							move_dir = DIR_UP
						elif self.mapinfo[0][i][0].top in range(self.mapinfo[3][0][0].top-10, self.mapinfo[3][0][0].top+10):
							move_dir = DIR_LEFT
							# shoot = 1
						break

				# for i in range(len(self.mapinfo[0])):
					if (self.mapinfo[0][i][0].top in range(self.mapinfo[3][0][0].top, self.mapinfo[3][0][0].top+bullet_distance)) and self.mapinfo[0][i][1] == DIR_UP:
						move_dir = DIR_RIGHT
						if self.player_x in range(21, 26) or (self.player_x+2, self.player_y) in self.walls:
							move_dir = DIR_LEFT
						elif self.mapinfo[0][i][0].left in range(self.mapinfo[3][0][0].left-10, self.mapinfo[3][0][0].left+10):
							move_dir = DIR_DOWN
							# shoot = 1
						break

				# for i in range(len(self.mapinfo[0])):
					if (self.mapinfo[0][i][0].top in range(self.mapinfo[3][0][0].top-bullet_distance, self.mapinfo[3][0][0].top)) and self.mapinfo[0][i][1] == DIR_DOWN:
						move_dir = DIR_RIGHT
						if self.player_x in range(21, 26) or (self.player_x+2, self.player_y) in self.walls:
							move_dir = DIR_LEFT
						elif self.mapinfo[0][i][0].left in range(self.mapinfo[3][0][0].left-10, self.mapinfo[3][0][0].left+10):
							move_dir = DIR_UP
							# shoot = 1
						break

			'''protect castel'''
			# avoid player to shoot castle
			if (self.player_x in range(10, 16)) and (self.player_y in range(21, 26)) and (self.mapinfo[3][0][1] == DIR_DOWN):
				# move_dir = DIR_UP
				shoot = 0
			if (self.player_y in range(21, 26)) and (self.mapinfo[3][0][1] == DIR_RIGHT or self.mapinfo[3][0][1] == DIR_LEFT):
				# move_dir = DIR_UP
				shoot = 0

			'''action'''
			keep_action = 0

			'''delay time'''
			# time.sleep(0.1)
			# q=0
			# for i in range(1000):
			# 	q+=1

			#-----------
			self.Update_Strategy(c_control,shoot,move_dir,keep_action)
		#------------------------------------------------------------------------------------------------------

	def Get_mapInfo(self,p_mapinfo):
		if p_mapinfo.empty()!=True:
			try:
				self.mapinfo = p_mapinfo.get(False)
			except Queue.Empty:
				skip_this=True

	def Update_Strategy(self,c_control,shoot,move_dir,keep_action):
		if c_control.empty() ==True:
			c_control.put([shoot,move_dir,keep_action])
			return True
		else:
			return False

	def get_player_rect(self):
		self.player_x = int(self.mapinfo[3][0][0].left/self.unit)
		self.player_y = int(self.mapinfo[3][0][0].top/self.unit)
		# only move up or left need to fix bias
		if self.mapinfo[3][0][1] == 0 or self.mapinfo[3][0][1]==3:
			'''top'''
			if self.mapinfo[3][0][0].left % int(self.unit) > 6:
				self.player_x += 1 #fixed bias
			'''left'''
			if self.mapinfo[3][0][0].top % int(self.unit) > 6:
				self.player_y += 1 #fixed bias
		return

	def get_enemy_rect(self):
		self.enemy_x = int(round(self.mapinfo[1][0][0].left/self.unit))
		self.enemy_y = int(round(self.mapinfo[1][0][0].top/self.unit))
		for i in range(len(self.mapinfo[1])):
			'''enemy which near castle eliminating firstly'''
			if int(round(self.mapinfo[1][i][0].top/self.unit)) in range(18, 26):
				self.enemy_x = int(round(self.mapinfo[1][i][0].left/self.unit))
				self.enemy_y = int(round(self.mapinfo[1][i][0].top/self.unit))
				return
			'''attack nearby enemy'''
			if self.mapinfo[1][i][0].left in range(self.mapinfo[3][0][0].left-50, self.mapinfo[3][0][0].left+50) and self.mapinfo[1][i][0].top in range(self.mapinfo[3][0][0].top-50, self.mapinfo[3][0][0].top+50):
				self.enemy_x = int(round(self.mapinfo[1][i][0].left/self.unit))
				self.enemy_y = int(round(self.mapinfo[1][i][0].top/self.unit))
				return
		return

	def get_walls(self):
		self.reachable_grid = []

		for i in range(len(self.mapinfo[2])):
			if self.mapinfo[2][i][1] != 4:
				wall_x = int(self.mapinfo[2][i][0].left/self.unit)
				wall_y = int(self.mapinfo[2][i][0].top/self.unit)
				if (wall_x, wall_y) not in self.walls:
					self.walls.append((wall_x, wall_y))

		# castle also append into walls
		for i in range(11, 15):
			for j in range(23, 26):
				if(i, j) not in self.walls:
					self.walls.append((i, j))

		# get reachable cell
		for i in range(len(self.all_grid)):
			if self.all_grid[i] not in self.walls:
				self.reachable_grid.append(self.all_grid[i])

		# if beside the reachable_grid have wall, also see it as wall
		for i in range(len(self.reachable_grid)):
			if ((self.reachable_grid[i][0]+1, self.reachable_grid[i][1]) in self.walls) or ((self.reachable_grid[i][0], self.reachable_grid[i][1]+1) in self.walls) or ((self.reachable_grid[i][0]+1, self.reachable_grid[i][1]+1) in self.walls):
				self.walls.append(self.reachable_grid[i])
		return

class Cell(object):
    def __init__(self, x, y, reachable):
        '''Initialize new cell.
        @param reachable is cell reachable? not a wall?
        @param x cell x coordinate
        @param y cell y coordinate
        @param g cost to move from the starting cell to this cell.
        @param h estimation of the cost to move from this cell
                 to the ending cell.
        @param f f = g + h
        '''
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

class Astar(object):
	def __init__(self):
		self.opened = []
		heapq.heapify(self.opened)
		self.closed = set()
		self.cells = []
		self.grid_height = None
		self.grid_width = None

	def init_grid(self, width, height, walls, start, end):
		'''Prepare grid cells, walls.
		@param width grid's width.
		@param height grid's height.
		@param walls list of wall x,y tuples.
		@param start grid starting point x,y tuple.
		@param end grid ending point x,y tuple.
		'''
		self.grid_height = height
		self.grid_width = width
		for x in range(self.grid_width):
			for y in range(self.grid_height):
				if (x, y) in walls:
					reachable = False
				else:
					reachable = True
				self.cells.append(Cell(x, y, reachable))
		self.start = self.get_cell(*start)
		self.end = self.get_cell(*end)

	def get_heuristic(self, cell):
		'''Compute the heuristic value H for a cell.
		Distance between this cell and the ending cell multiply by 10.
		@returns heuristic value H
		'''
		return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

	def get_cell(self, x, y):
		'''Returns a cell from the cells list.
		@param x cell x coordinate
		@param y cell y coordinate
		@returns cell
		'''
		return self.cells[x * self.grid_height + y]

	def get_adjacent_cells(self, cell):
		'''Returns adjacent cells to a cell.
		Clockwise starting from the one on the right.
		@param cell get adjacent cells for this cell
		@returns adjacent cells list.
		'''
		cells = []
		if cell.x < self.grid_width-1:
			cells.append(self.get_cell(cell.x+1, cell.y))
		if cell.y > 0:
			cells.append(self.get_cell(cell.x, cell.y-1))
		if cell.x > 0:
			cells.append(self.get_cell(cell.x-1, cell.y))
		if cell.y < self.grid_height-1:
			cells.append(self.get_cell(cell.x, cell.y+1))
		return cells

	def get_path(self):
		cell = self.end
		path = [(cell.x, cell.y)]
		try:
			while cell.parent is not self.start:
				cell = cell.parent
				try:
					path.append((cell.x, cell.y))
				except AttributeError:
					# print "AttributeError"
					pass
		except AttributeError:
			# print "AttributeError"
			pass
		path.append((self.start.x, self.start.y))
		path.reverse()
		return path

	def update_cell(self, adj, cell):
		''''Update adjacent cell.
		@param adj adjacent cell to current cell
		@param cell current cell being processed
		'''
		adj.g = cell.g + 10
		adj.h = self.get_heuristic(adj)
		adj.parent = cell
		adj.f = adj.h + adj.g

	def solve(self):
		'''Solve maze, find path to ending cell.
		@returns path or None if not found.
		'''
		# add starting cell to open heap queue
		heapq.heappush(self.opened, (self.start.f, self.start))
		while len(self.opened):
			# pop cell from heap queue
			f, cell = heapq.heappop(self.opened)
			# add cell to closed list so we don't process it twice
			self.closed.add(cell)
			# if ending cell, return found path
			if cell is self.end:
				return self.get_path()
			# get adjacent cells for cell
			adj_cells = self.get_adjacent_cells(cell)
			for adj_cell in adj_cells:
				if adj_cell.reachable and adj_cell not in self.closed:
					if (adj_cell.f, adj_cell) in self.opened:
						# if adj cell in open list, check if current path is
						# better than the one previously found
						# for this adj cell.
						if adj_cell.g > cell.g + 10:
							self.update_cell(adj_cell, cell)
					else:
						self.update_cell(adj_cell, cell)
						# add adj cell to open list
						heapq.heappush(self.opened, (adj_cell.f, adj_cell))
