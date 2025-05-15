import random
import time
from collections import deque
from copy import deepcopy

boardSize = 13
wallCount2Player = 20
wallCount4Player = 10
aiSearchDepth = 1

goalMap = {
    1: lambda pos: pos[1] == boardSize - 1,
    2: lambda pos: pos[1] == 0,
    3: lambda pos: pos[0] == boardSize - 1,
    4: lambda pos: pos[0] == 0,
}

startPositions = {
    1: (boardSize // 2, 0),
    2: (boardSize // 2, boardSize - 1),
    3: (0, boardSize // 2),
    4: (boardSize - 1, boardSize // 2),
}

class AlphaBetaAgent:
    def __init__(self, playerId, depth=aiSearchDepth):
        self.playerId = playerId
        self.depth = depth

    def getBestAction(self, gameRef):
        _, move = self.minimax(gameRef, self.depth, float('-inf'), float('inf'), True, self.playerId)
        return move

    def minimax(self, gameRef, depth, alpha, beta, isMaximizing, currentId):
        if depth == 0 or gameRef.checkWin(currentId):
            return self.evaluateState(gameRef), None

        actionList = [('move', pos) for pos in gameRef.getLegalMoves(currentId)]

        if gameRef.players[currentId]['walls'] > 0:
            wallOptions = []
            for orientation in ['h', 'v']:
                for row in range(boardSize - 1):
                    for col in range(boardSize - 1):
                        if gameRef.isWallValid(orientation, row, col):
                            wallOptions.append(('wall', (orientation, row, col)))
            if wallOptions:
                wallSample = random.sample(wallOptions, min(len(wallOptions), 10))
                actionList += wallSample

        if isMaximizing:
            bestVal, chosenAction = float('-inf'), None
            for act in actionList:
                gameCopy = deepcopy(gameRef)
                gameCopy.applyMove(currentId, act)
                nextId = (currentId % 4) + 1
                score, _ = self.minimax(gameCopy, depth - 1, alpha, beta, False, nextId)
                if score > bestVal:
                    bestVal, chosenAction = score, act
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return bestVal, chosenAction
        else:
            bestVal = float('inf')
            for act in actionList:
                gameCopy = deepcopy(gameRef)
                gameCopy.applyMove(currentId, act)
                nextId = (currentId % 4) + 1
                score, _ = self.minimax(gameCopy, depth - 1, alpha, beta, True, nextId)
                if score < bestVal:
                    bestVal = score
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return bestVal, None

    def evaluateState(self, gameRef):
        myPos = gameRef.players[self.playerId]['pos']
        myDistance = gameRef.getGoalDistance(myPos, self.playerId)
        return -myDistance

class QuoridorGame:
    def __init__(self, humanPlayers):
        wallLimit = wallCount2Player if len(humanPlayers) == 2 else wallCount4Player
        self.players = {i: {'pos': startPositions[i], 'walls': wallLimit, 'type': 'human' if i in humanPlayers else 'ai'} for i in range(1, 5)}
        self.horizontalWalls = set()
        self.verticalWalls = set()
        self.activeTurn = 1
        self.aiAgents = {i: AlphaBetaAgent(i) for i in range(1, 5) if self.players[i]['type'] == 'ai'}

    def getLegalMoves(self, pid):
        x, y = self.players[pid]['pos']
        moves = []
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < boardSize and 0 <= ny < boardSize):
                continue
            if self.isWallBlocking((x, y), (nx, ny)):
                continue
            target = self.getPlayerAt(nx, ny)
            if target:
                jx, jy = nx + dx, ny + dy
                if (0 <= jx < boardSize and 0 <= jy < boardSize and
                    not self.isWallBlocking((nx, ny), (jx, jy)) and
                    not self.getPlayerAt(jx, jy)):
                    moves.append((jx, jy))
                else:
                    for ddx, ddy in [(-dy, dx), (dy, -dx)]:
                        sideX, sideY = nx + ddx, ny + ddy
                        if (0 <= sideX < boardSize and 0 <= sideY < boardSize and
                            not self.isWallBlocking((nx, ny), (sideX, sideY)) and
                            not self.getPlayerAt(sideX, sideY)):
                            moves.append((sideX, sideY))
            else:
                moves.append((nx, ny))
        return moves

    def getPlayerAt(self, x, y):
        for pid, pdata in self.players.items():
            if pdata['pos'] == (x, y):
                return pid
        return None

    def isWallValid(self, ori, x, y):
        if x >= boardSize - 1 or y >= boardSize - 1:
            return False
        if self.players[self.activeTurn]['walls'] <= 0:
            return False
        tempGame = deepcopy(self)
        if ori == 'h':
            tempGame.horizontalWalls.add(('h', x, y))
            tempGame.horizontalWalls.add(('h', x + 1, y))
        else:
            tempGame.verticalWalls.add(('v', x, y))
            tempGame.verticalWalls.add(('v', x, y + 1))
        for pid in self.players:
            if tempGame.getGoalDistance(tempGame.players[pid]['pos'], pid) == 999:
                return False
        return True

    def applyMove(self, pid, action):
        if action[0] == 'move':
            self.players[pid]['pos'] = action[1]
        elif action[0] == 'wall':
            ori, x, y = action[1]
            if self.isWallValid(ori, x, y):
                if ori == 'h':
                    self.horizontalWalls.add(('h', x, y))
                    self.horizontalWalls.add(('h', x + 1, y))
                else:
                    self.verticalWalls.add(('v', x, y))
                    self.verticalWalls.add(('v', x, y + 1))
                self.players[pid]['walls'] -= 1

    def isWallBlocking(self, fromCell, toCell):
        fx, fy = fromCell
        tx, ty = toCell
        if abs(fx - tx) + abs(fy - ty) != 1:
            return True
        if fx == tx:
            minY = min(fy, ty)
            return ('h', fx, minY) in self.horizontalWalls
        elif fy == ty:
            minX = min(fx, tx)
            return ('v', minX, fy) in self.verticalWalls
        return False

    def checkOccupied(self, x, y):
        return any(p['pos'] == (x, y) for p in self.players.values())

    def checkWin(self, pid):
        return goalMap[pid](self.players[pid]['pos'])

    def getGoalDistance(self, startPos, pid):
        visited = set()
        queue = deque([(startPos, 0)])
        while queue:
            (x, y), d = queue.popleft()
            if goalMap[pid]((x, y)):
                return d
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < boardSize and 0 <= ny < boardSize:
                    if not self.isWallBlocking((x, y), (nx, ny)) and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), d + 1))
        return 999
