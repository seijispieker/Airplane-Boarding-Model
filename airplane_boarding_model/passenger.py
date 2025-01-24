"""A module for modeling a passenger of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import mesa

if TYPE_CHECKING:
    from .airbus_a320 import Seat
    from .boarding_model import BoardingModel


class Passenger(mesa.Agent):
    """A class for modeling a passenger of an airplane.
    
    Attributes:
        aisle_steps_per_move: The number of steps to move one cell in the aisle.
        luggage_time: The number of steps to store luggage.
        assigned_seat: The Seat assigned to the passenger.
        seated: True if the passenger is seated, False otherwise.
        last_move: The number of steps since the last move.
    """
    
    def __init__(
        self,
        model: BoardingModel,
        aisle_steps_per_move: int,
        luggage_items: int = 1,
        assigned_seat: Seat = None,
        seated: bool = False,
    ):
        """Initialize a Passenger object."""
        super().__init__(model)
        self.aisle_steps_per_move = aisle_steps_per_move
        # alpha and beta based on Schultz 2018:
        single_luggage_time = self.model.random.weibullvariate(alpha=16, beta=1.7)
        self.luggage_time = round(luggage_items * single_luggage_time * model.steps_per_second)
        self.assigned_seat = assigned_seat
        self.seated = seated
        self.last_move = aisle_steps_per_move
        self.arrival_time = 0
        
    def step(self):
        """Advance the passenger by one step."""
        self.last_move += 1
        
        if self.seated:
            return
        
        # If in the correct row
        if self.pos[0] == self.assigned_seat.grid_coordinate[0]:
            # If waiting to store luggage
            if self.luggage_time > 0:
                self.luggage_time -= 1
                return
            
            # If in the correct column
            if self.pos[1] == self.assigned_seat.grid_coordinate[1]:
                self.seated = True
                self.assigned_seat.occupied = True
            else:
                direction = 1 if self.assigned_seat.grid_coordinate[1] > self.pos[1] else -1
                self.move(drow=0, dcol=direction)
        else:
            self.move(drow=1, dcol=0)
        
    def move(self, drow: int, dcol: int) -> bool:
        """Move the passenger by the given row and column offsets.
        
        Args:
            drow: The row offset.
            dcol: The column offset.    
        Returns:
            True if the passenger moved, False if move not possible.
        """
        target = (self.pos[0] + drow, self.pos[1] + dcol)
        
        if self.model.grid.is_cell_empty(target) and self.last_move >= self.aisle_steps_per_move:
            self.model.grid.move_agent(self, target)
            self.last_move = 0
            return True
        else:
            return False