"""A module for modeling a passenger of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import agentpy as ap

if TYPE_CHECKING:
    from .airplane import Seat
    from .boarding_model import BoardingModel


class Passenger(ap.Agent):
    """A passenger inheriting from agentpy.Agent.
    
    Attributes:
        assigned_seat: The Seat object assigned to the passenger.
        seated: Whether the passenger is seated.
    """
    
    def __init__(self, model: BoardingModel, assigned_seat: Seat=None):
        """Create a new passenger with the given assigned seat."""
        super().__init__(model)
        self.assigned_seat = assigned_seat
        self.seated = False