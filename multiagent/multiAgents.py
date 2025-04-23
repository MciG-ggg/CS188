# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        capsules = successorGameState.getCapsules()

        # 获取基础分数
        score = successorGameState.getScore()
        
        # 计算到所有食物的距离
        foodList = newFood.asList()
        if len(foodList) > 0:
            # 找到最近的食物距离
            foodDistances = [manhattanDistance(newPos, food) for food in foodList]
            minFoodDist = min(foodDistances)
            # 直接使用最近食物的距离作为评分依据，而不是平均距离
            score -= minFoodDist * 2
            
            # 如果只剩下两个食物，额外增加向最近食物移动的倾向
            if len(foodList) == 2:
                score -= minFoodDist * 3

        # 处理胶囊
        for capsulePosition in capsules:
            capsuleDistance = manhattanDistance(newPos, capsulePosition)
            # 大幅提高胶囊的重要性
            score -= capsuleDistance * 10 
        
        # 处理幽灵
        for ghostState in newGhostStates:
            ghostPos = ghostState.getPosition()
            ghostDist = manhattanDistance(newPos, ghostPos)
            
            if ghostState.scaredTimer > 0:  # 如果幽灵处于害怕状态
                # 极大化追逐害怕幽灵的倾向
                if ghostDist == 0:  # 如果能直接吃到幽灵
                    score += 10
                else:
                    # 距离越近分数越高，使用指数函数来强化这种倾向
                    score += 50 / (ghostDist + 1)
            else:  # 幽灵不是害怕状态
                if ghostDist < 5:  # 如果幽灵太近
                    score -= 10/ ( ghostDist + 1 )  # 严重惩罚
                elif ghostDist < 9:  # 保持安全距离
                    score -= 10 / ( ghostDist + 1 )
                    
        # 停止动作的惩罚
        if action == Directions.STOP:
            score -= 2
            
        # 考虑剩余食物数量
        score -= len(foodList) * 100
            
        return score

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        bestAction = None
        bestValue = float("-inf")

        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)

            value = self.minimax(successor, self.depth, 1)
            if value > bestValue:
                bestValue = value
                bestAction = action

        return bestAction
    
    def minimax(self, gameState: GameState, depth, agentIndex):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)

        numAgents = gameState.getNumAgents()

        if agentIndex == 0:
            value = float("-inf")
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                successor = gameState.generateSuccessor(0, action)
                value = max(value, self.minimax(successor, depth, 1))
            return value
        
        else:
            value = float("inf")
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                successor = gameState.generateSuccessor(agentIndex, action)
                if agentIndex == numAgents - 1:
                    value = min(value, self.minimax(successor, depth - 1, 0))
                else:
                    value = min(value, self.minimax(successor, depth, agentIndex + 1))
            return value


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        bestAction = None
        bestValue = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)

            value = self.alphaBeta(successor, self.depth, 1, alpha, beta)
            if value > bestValue:
                bestValue = value
                bestAction = action
            alpha = max(alpha, bestValue)

        return bestAction
    
    def alphaBeta(self, gameState: GameState, depth, agentIndex, alpha, beta):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        
        numAgents = gameState.getNumAgents()
        if agentIndex == 0:
            value = float("-inf")
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                successor = gameState.generateSuccessor(0, action)
                value = max(value, self.alphaBeta(successor, depth, 1, alpha, beta))
                if value > beta:
                    return value
                alpha = max(alpha, value)
            return value
        else: 
            value = float("inf")
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                successor = gameState.generateSuccessor(agentIndex, action)
                if agentIndex == numAgents - 1:
                    value = min(value, self.alphaBeta(successor, depth - 1, 0, alpha, beta))
                else:
                    value = min(value, self.alphaBeta(successor, depth, agentIndex + 1, alpha, beta))
                if value < alpha:
                    return value
                beta = min(beta, value)
            return value

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
