from agentpy import Agent

class Passenger(Agent):
    def __init__(self, model, assigned_seat=None):
        super().__init__(model)
        self.group = 1
        self.assigned_seat = assigned_seat
        self.seated = False