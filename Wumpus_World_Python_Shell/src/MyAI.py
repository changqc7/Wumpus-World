# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent
import dis

min_score = -200

class MyAI ( Agent ):

    def __init__ ( self ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        
        self._row = 0
        self._col = 0
        self._arrow = True
        self._wumpus = True
        self._gold = False
        self._back = False
        self._gohome = False
        self._lastAction = Agent.Action.CLIMB
        self._lastPostion = (0,0)
        self._score = 0
        self._turns = 0
        self._direction = 'E'
        
        self._map = {} # the value of dict should be (0 stemch , 1 breeze , 2 visited , 3 expanded , 4 wumpus? , 5 pit? , 6 distance )
        for row in range(7):
            for col in range(7):
                self._map[(row , col)] = ['unknow' , 'unknow' , False , False , 'unknow' , 'unknow' , row+col]
        self._map[(0,0)] = ['unknow' , 'unknow' , False , False , False , False , 0]

        self._myPath = [(0 , 0 , 'E')]
        self._allPath = {}
        for i in self._map:
            self._allPath[i] = []
        
        self._wumpus_pos = []
        self._home_path = []
        
        self._pit = {}
        for i in self._map:
            self._pit[i] = 0
            
        self._go_path = []
        

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================


    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        self._score -= 1
        self._turns += 1
        last_position = self._myPath[-1]
        
        
        if scream:
            self._wumpus = False
        elif self._lastAction == Agent.Action.SHOOT:
            self.arrow_miss()
        
        if bump:
            self.updaterow_col(self._lastAction , True)
            self.wall()
            self._myPath.pop(-1)   
        elif self.visited(self._row , self._col) == False:
            self.updateMap(stench , breeze)
        
        if glitter:
            self._gold = True
            nextAction =  Agent.Action.GRAB
        
        elif self._score < min_score:
            nextAction = self.come_back()
            
        elif self._gold:
            nextAction = self.come_back()
        
        elif breeze:
            if (stench and self._wumpus):
                self.find_monster()
#            way = self.findWay(stench , breeze)
#            if len(way) != 0:
#                way = way[0]
#                nextAction = self.goto(way)
#            else:
            nextAction = self.come_back()


        elif (stench and self._wumpus):
        
            if self._lastAction == Agent.Action.CLIMB:
                self._arrow = False
                nextAction = Agent.Action.SHOOT
                
            elif self._arrow:
                self.find_monster()
                if len(self._wumpus_pos) == 1:
                    wumpus_pos = self._wumpus_pos[0]
                    shoot_direction = self.go_direction(wumpus_pos[0], wumpus_pos[1])
                    nextAction = self.kill_monster(shoot_direction)
                else:
                    way = self.findWay(stench , breeze)
                    if len(way) != 0:
                        way = way[0]
                        nextAction = self.goto(way)
                    else:
                        nextAction = self.come_back()

            else:
                way = self.findWay(stench , breeze)
                if len(way) != 0:
                    way = way[0]
                    nextAction = self.goto(way)
                else:
                    nextAction = self.come_back()
                    
        elif not self.allexpanded():
            neighbors = self.getNeighbor(self._row, self._col)
            
            if not self.expanded(neighbors):
                way = self.findWay(stench , breeze)[0]
                nextAction = self.goto(way)
            
            else:
                nextAction = self.come_back()
        
        else:   
            if not self._gohome:
                self._gohome = True
                self._home_path = self.find_path((self._row , self._col), (0,0))
                
            if self._row == 0 and self._col == 0:
                nextAction = Agent.Action.CLIMB
            else:
                pos = self._home_path[self._home_path.index((self._row , self._col))+1]
                nextAction = self.goto(pos)
                    

        self._lastAction = nextAction
        self._lastPostion = (self._row , self._col)
        self._direction = self.getDirection(nextAction)
        self.updaterow_col(nextAction , False)
        self.update_path(nextAction)
        
        
#        print(self._myPath)
#        print()
#        print((self._row , self._col , self._direction))
        return nextAction
        
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================

    def come_back(self):
        self._back = True
        if self._row == 0 and self._col == 0:
            return Agent.Action.CLIMB
 
        last_position = self._myPath[-2]
        d = last_position[2]
        d = self.opposite_position(d)

        return self.direction_action(d)

        
    def goto(self , pos):
        pos_direction = self.go_direction(pos[0] , pos[1])
        return self.direction_action(pos_direction)

    def opposite_position(self , d):
        if d == 'N':
            return 'S'
        elif d == 'E':
            return 'W'
        elif d == 'W':
            return 'E'
        else:
            return 'N'

    def go_direction(self , row , col):
        if row > self._row:
            return 'N'
        elif row < self._row:
            return 'S'
        elif col > self._col:
            return 'E'
        else:
            return 'W'
        
    def getDirection(self , action):
        if action == Agent.Action.TURN_LEFT:
            if self._direction == 'N':
                return 'W'
            elif self._direction == 'W':
                return 'S'
            elif self._direction == 'S':
                return 'E'
            else:
                return 'N'

        elif action == Agent.Action.TURN_RIGHT:
            if self._direction == 'N':
                return 'E'
            elif self._direction == 'W':
                return 'N'
            elif self._direction == 'S':
                return 'W'
            else:
                return 'S'

        else:
            return self._direction

    def visited(self , row , col):
        return self._map[(row , col)][2]

    def expanded(self , neighbors):
        for i in range(len(neighbors)):
            if self._map[neighbors[i]][2] == False:
                return False
        return True

    def getNeighbor(self , row , col):
        neighbors = [(row , col+1) , (row + 1 , col) , (row - 1 , col) ,(row , col-1)]
        result = []
        for i in range(4):
            if neighbors[i] in self._map:
                result.append(neighbors[i])
        return result
                

    def updaterow_col(self , action , bump):
        if bump:
            if self._direction == 'N':
                self._row -= 1
            elif self._direction == 'E':
                self._col -= 1
        else:
            if action == Agent.Action.FORWARD:
                if self._direction == 'N':
                    self._row += 1
                elif self._direction == 'W':
                    self._col -= 1
                elif self._direction == 'S':
                    self._row -= 1
                else:
                    self._col += 1

    def wall(self):
        if self._direction == 'N' and self._row != 6:
            for i in range(self._row + 1 , 7):
                for j in range(7):
                    if (i ,j) in self._map:
                        self._map.pop((i,j))
        elif self._direction == 'E' and self._col != 6:
            for j in range(self._col+1 , 7):
                for i in range(7):
                    if (i ,j) in self._map:
                        self._map.pop((i,j))
                    
    def updateMap(self , s , b):
        self._map[(self._row , self._col)][0] = s
        self._map[(self._row , self._col)][1] = b
        self._map[(self._row , self._col)][2] = True
        self._map[(self._row , self._col)][4] = False
        self._map[(self._row , self._col)][5] = False
        self._pit[(self._row , self._col)]  = -100
        if (self._row , self._col) in self._wumpus_pos:
            self._wumpus_pos.remove((self._row , self._col))
        
        neighbors = self.getNeighbor(self._row, self._col)
        if not s:
            for i in neighbors:
                self._map[i][4] = False
                if i in self._wumpus_pos:
                    self._wumpus_pos.remove(i)
        if not b:
            for i in neighbors:
                self._map[i][5] = False     
                self._pit[i] = -100  
        self._map[(self._row , self._col)][3] = self.expanded(neighbors)
        
    
    def findWay(self , s ,b):
        neighbors = self.getNeighbor(self._row, self._col)
        ways = []
        if b:
            if self._lastAction == Agent.Action.FORWARD:
                for i in neighbors:
                    if self._map[i][5] != False:
                        self._pit[i] += 1
                dangerous = []
                for i in neighbors:
                    if self._pit[i] >= 3:
                        dangerous.append(i)
                if dangerous != []:
                    for i in neighbors:
                        if i not in dangerous and self._map[i][2] == False:
                            ways.append(i)
        elif s and self._wumpus:
            for i in range(len(neighbors)):
                if self._map[neighbors[i]][2] == False and self._map[neighbors[i]][4] == False:
                    ways.append(neighbors[i])  
        else:
            for i in range(len(neighbors)):
                if self._map[neighbors[i]][2] == False:
                    ways.append(neighbors[i])
        return ways
    
    
    def direction_action(self , d):
        if self._direction == d:
            return Agent.Action.FORWARD
        elif self._direction == self.opposite_position(d):
            return Agent.Action.TURN_LEFT
        else:
            if (self._direction == 'N' and d == 'E') or (self._direction == 'E' and d == 'S') or (self._direction == 'S' and d == 'W') or (self._direction == 'W' and d == 'N'):
                return Agent.Action.TURN_RIGHT
            else:
                return Agent.Action.TURN_LEFT
            
    def update_path(self , action):
        past = self._myPath[-1]
        if not self._back:
            if len(self._myPath) == 0:
                self._myPath.append((self._row , self._col , self._direction))
                self._allPath[(self._row , self._col)].append(self._lastPostion)
                self._allPath[self._lastPostion].append((self._row , self._col))
            else:
                if past[0] != self._row or past[1] != self._col:
                    self._myPath.append((self._row , self._col , self._direction))
                    self._allPath[(self._row , self._col)].append(self._lastPostion)
                    self._allPath[self._lastPostion].append((self._row , self._col))
                else:
                    self._myPath[-1] = (self._row , self._col , self._direction)
        else:
            if action == Agent.Action.FORWARD:
                self._myPath.remove(past)
                self._myPath[-1] = (self._row , self._col , self._direction)
                self._back = False
            
            else:
                self._myPath[-1] = (self._row , self._col , self._direction)
                
    def arrow_miss(self):
        if self._direction == 'N':
            for i in range(self._row + 1 , 7):
                if (i , self._col) in self._map:
                    self._map[(i , self._col)][4] = False
        elif self._direction == 'W':
            for i in range(self._col):
                self._map[(self._row , i)][4] = False
        elif self._direction == 'S':
            for i in range(self._row):
                self._map[(i , self._col)][4] = False
        else:
            for i in range(self._col + 1 , 7):
                if (self._row , i) in self._map:
                    self._map[(self._row , i)][4] = False
                    
    def find_monster(self):
        neighbors = self.getNeighbor(self._row, self._col)
        result = []
        if self._wumpus_pos == []:
            for i in range(len(neighbors)):
                if self._map[neighbors[i]][4] != False:
                    self._wumpus_pos.append(neighbors[i])
        else:
            for i in range(len(neighbors)):
                if self._map[neighbors[i]][4] != False:
                    result.append(neighbors[i])
            new = []
            for i in self._wumpus_pos:
                if i in result:
                    new.append(i)
            self._wumpus_pos = new
            
        dangerous = []
        dangerous += self._wumpus_pos
        for pos in self._wumpus_pos:
            r,c = pos[0],pos[1]
            neibor = self.getNeighbor(r, c)
            dangerous += neibor
        for i in self._map:
            if i not in dangerous:
                self._map[i][4] = False
                
    
    def kill_monster(self , d):
        if self._direction == d:
            self._arrow = False
            return Agent.Action.SHOOT
        elif self._direction == self.opposite_position(d):
            return Agent.Action.TURN_LEFT
        else:
            if (self._direction == 'N' and d == 'E') or (self._direction == 'E' and d == 'S') or (self._direction == 'S' and d == 'W') or (self._direction == 'W' and d == 'N'):
                return Agent.Action.TURN_RIGHT
            else:
                return Agent.Action.TURN_LEFT
    
    def allexpanded(self):
        path = []
        for i in self._myPath:
            path.append((i[0],i[1]))
        
        for i in path:
            neighbors = self.getNeighbor(i[0], i[1])
            if not self.expanded(neighbors):
                return False
        return True
    
    def BFS(self , s , e):
        visited = {}
        for i in self._allPath:
            visited[i] = False
            self._allPath[i] = list(set(self._allPath[i]))      #remove duplicates
        queue = [] 
        queue.append(e)
        visited[e] = True
        mother = {}
        while queue[0] != s: 
            e = queue.pop(0) 
            for i in self._allPath[e]: 
                if visited[i] == False: 
                    queue.append(i) 
                    visited[i] = True
                    mother[i] = e
        return mother
    
    def find_path(self , s , e):
        mother = self.BFS(s, e)
        current = s
        path = [s]
        while current != e:
            current = mother[current]
            path.append(current)
        return path

    
        
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================
