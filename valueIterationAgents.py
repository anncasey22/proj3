# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        #Write value iteration code here
        #takes mdp for the specified num of iterations b4 constructor returns\
        #for loop, iterate through k states, and add to self.values
        num_iterations = self.iterations
        for k in range(num_iterations):
            new_values = util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    new_values[state] = 0
                    continue
                max_q = -999999999
                for action in self.mdp.getPossibleActions(state):
                    q = self.computeQValueFromValues(state, action)
                    max_q = max(max_q, q)
                new_values[state] = max_q
            self.values = new_values


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        q = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            r = self.mdp.getReward(state, action, nextState)
            q += prob*(r + self.discount*self.values[nextState])
        return q

        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        #find all the values of the legal actions
        #return optimal action
        actions = self.mdp.getPossibleActions(state)
        if not actions:
            return None
        best_action = (actions[0], -999999999)
        for action in actions:
            curr = self.computeQValueFromValues(state, action)
            if curr > best_action[1]:
                best_action = (action, curr)
        return best_action[0]


    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


class PrioritizedSweepingValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        states = self.mdp.getStates()
        previous = {}
#find previous stateew
        for state in states:
            previous[state] = set()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            for action in self.mdp.getPossibleActions(state):
                for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    if prob > 0:
                        previous[nextState].add(state)
        pq = util.PriorityQueue()
        for state in states:
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            max_q = float('-inf')
            for action in actions:
                q_val = self.computeQValueFromValues(state, action)
                if q_val > max_q:
                    max_q = q_val
            diff = abs(self.values[state] - max_q)
            pq.push(state, -diff)
        for i in range(self.iterations):
            if pq.isEmpty():
                break
            state = pq.pop()
            if not self.mdp.isTerminal(state):
                actions = self.mdp.getPossibleActions(state)
                max_q = float('-inf')
                for action in actions:
                    q_val = self.computeQValueFromValues(state, action)
                    if q_val > max_q:
                        max_q = q_val
                self.values[state] = max_q
            for p in previous[state]:
                if self.mdp.isTerminal(p):
                    continue
                actions = self.mdp.getPossibleActions(p)
                max_q = float('-inf')
                for action in actions:
                    q_val = self.computeQValueFromValues(p, action)
                    if q_val > max_q:
                        max_q = q_val
                diff = abs(self.values[p] - max_q)
                if diff > self.theta:
                    pq.update(p, -diff)


