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


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
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
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
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

        currentPos = currentGameState.getPacmanPosition()
        foodPosition = newFood.asList()
        closeGhost = min([manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates])
        if foodPosition:
            closeFood = min([manhattanDistance(newPos, foodPos) for foodPos in foodPosition])
        else:
            closeFood = -1

        if closeGhost == 0 and newScaredTimes[0] == 0:
            closeGhost -= 1000
        if newScaredTimes[0]:
            closeGhost += newScaredTimes[0]

        return successorGameState.getScore()+(1/closeFood)-(1/closeGhost)
        "*** YOUR CODE HERE ***"
        # return successorGameState.getScore()


def scoreEvaluationFunction(currentGameState):
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

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
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
        def maxValue(agent, state, depth):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            v = float('-inf')
            for a in state.getLegalActions(agent):
                v = max(v, minValue(agent+1, state.generateSuccessor(agent,a),depth))
            return v


        def minValue(agent, state, depth):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            v = float('inf')
            nextAgent= agent+1
            if not nextAgent == state.getNumAgents()-1:
                for a in state.getLegalActions(agent):
                    v = min(v, maxValue(0, state.generateSuccessor(agent, a), depth+1))
            else:
                for a in state.getLegalActions(agent):
                    v = min(v, minValue(nextAgent, state.generateSuccessor(agent, a),depth))
            return v

        act = Directions.STOP
        score = float('-inf')
        for a in gameState.getLegalActions(0):
            nextS = gameState.generateSuccessor(0, a)
            temp = minValue(1, nextS, 0)
            if score < temp:
                score = temp
                act = a
        return act
        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """

        def maxValue(agent, state, depth, maxA, minB):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            v = float('-inf')
            for a in state.getLegalActions(agent):
                v = max(v, minValue(agent + 1, state.generateSuccessor(agent, a), depth, maxA, minB))
                if v > minB:
                    return v
                maxA = max(maxA, v)
            return v

        def minValue(agent, state, depth, maxA, minB):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            v = float('inf')
            nextAgent = agent + 1
            if not nextAgent == state.getNumAgents() - 1:
                for a in state.getLegalActions(agent):
                    v = min(v, maxValue(0, state.generateSuccessor(agent, a), depth + 1, maxA, minB))
                    if v < maxA:
                        return v
                    minB = min(v, minB)
            else:
                for a in state.getLegalActions(agent):
                    v = min(v, minValue(nextAgent, state.generateSuccessor(agent, a), depth, maxA, minB))
                    if v < maxA:
                        return v
                    minB = min(v, minB)
            return v

        alpha = float("-inf")
        beta = float("inf")
        act = Directions.STOP
        score = float('-inf')
        for a in gameState.getLegalActions(0):
            nextS = gameState.generateSuccessor(0, a)
            temp = minValue(1, nextS, 0, alpha, beta)
            if score < temp:
                score = temp
                act = a
                alpha = max(score, alpha)
        return act

        "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """

        def maxValue(agent, state, depth):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            v = float('-inf')
            for a in state.getLegalActions(agent):
                v = max(v, expectValue(agent + 1, state.generateSuccessor(agent, a), depth))
            return v

        def expectValue(agent, state, depth):
            actions = state.getLegalActions(agent)
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            v = 0
            nextAgent = agent+1
            prob = 1.0/len(actions)
            if not nextAgent == state.getNumAgents()-1:
                for a in actions:
                    v += maxValue(0, state.generateSuccessor(agent, a), depth+1)*prob
            else:
                for a in actions:
                    v += expectValue(nextAgent, state.generateSuccessor(agent, a),depth)*prob
            return v

        act = Directions.STOP
        score = float('-inf')
        for a in gameState.getLegalActions(0):
            nextS = gameState.generateSuccessor(0, a)
            temp = expectValue(1, nextS, 0)
            if score < temp:
                score = temp
                act = a
        return act
        "*** YOUR CODE HERE ***"

        # util.raiseNotDefined()


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    foodList = currentGameState.getFood().asList()
    newPos = currentGameState.getPacmanPosition()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    closeGhost = min([manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates])
    if foodList:
        closeFood = min([manhattanDistance(newPos, foodPos) for foodPos in foodList])
    else:
        closeFood = -0.5

    if closeGhost == 0 and newScaredTimes[0] == 0:
        closeGhost -= 1000
    if newScaredTimes[0]:
        closeGhost += newScaredTimes[0]

    score = currentGameState.getScore() - closeFood*1.5 + closeGhost
    return score

    "*** YOUR CODE HERE ***"
    # util.raiseNotDefined()



# Abbreviation
better = betterEvaluationFunction
