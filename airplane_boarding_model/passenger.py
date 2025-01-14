"""A module for modeling a passenger of an airplane."""

from agentpy import Agent


class Passenger(Agent):
    """A passenger inheriting from agentpy.Agent.
    
    Attributes:
        group: The group of the passenger. #TODO has no meaning yet
        assigned_seat: The Seat object assigned to the passenger.
        seated: Whether the passenger is seated.
    """
    
    def __init__(self, model, assigned_seat=None):
        """Create a new passenger with the given assigned seat."""
        super().__init__(model)
        self.group = 1
        self.assigned_seat = assigned_seat
        self.seated = False