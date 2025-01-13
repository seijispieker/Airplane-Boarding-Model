from agentpy import Agent

class Passenger(Agent):
    def __init__(self, model, seat=None):
        """
        Passenger agent.
        :param model: The simulation model.
        :param seat: Target seat for the passenger (e.g., "12A").
        """
        super().__init__(model)
        self.seat = seat
        self.boarded = False