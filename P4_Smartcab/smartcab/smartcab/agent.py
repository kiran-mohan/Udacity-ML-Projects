from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from random import choice, randint

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
	self.timeStep = 0
	self.actionList = [None,'forward','left','right']
	self.lightList = ['red','green']
	self.wpList = self.actionList[1:4]
	self.Q = {((x1,x2,x3,x4,x5),x6):0 for x1 in self.lightList for x2 in self.actionList for x3 in self.actionList for x4 in self.actionList for x5 in self.wpList for x6 in self.actionList}
	self.success = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
	self.timeStep = 0

    def update(self, t):
	if self.timeStep % 3 == 0:	
		self.timeStep += 1
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state=(inputs['light'],inputs['oncoming'],inputs['left'],inputs['right'],self.next_waypoint)

        # TODO: Select action according to your policy
	if(randint(1,10) <= 3): # This line simulates epsilon=0.3
		action = choice(self.actionList)
	else:
		qmax = self.Q[(self.state,None)]
		action = None
		for act in self.actionList:
			if qmax < self.Q[(self.state,act)]:
				qmax = self.Q[(self.state,act)]
				action = act

        # Execute action and get reward
        reward = self.env.act(self, action)

	# If goal is reached, increment success count
	if reward == 12:
		self.success += 1

	# TODO: Sense again to record new state
        self.next_next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        next_inputs = self.env.sense(self)
	self.next_state = (inputs['light'],inputs['oncoming'],inputs['left'],inputs['right'],self.next_waypoint)

	# TODO: Compute the next action that maximizes Q
	QNxtMax = self.Q[(self.next_state,None)]
	next_action = None
	for nxt_act in self.actionList:
		if QNxtMax < self.Q[(self.next_state,nxt_act)]:	
			QNxtMax = self.Q[(self.next_state,nxt_act)]
			next_action = nxt_act

        # TODO: Learn policy based on state, action, reward
	self.alpha = 0.1
	self.disc = 0.4
	self.Q[(self.state,action)] = (1-self.alpha)*self.Q[(self.state,action)] + self.alpha*(reward + self.disc*QNxtMax)
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
	print "Success rate : {}%".format(self.success)


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment(3)  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.1, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
