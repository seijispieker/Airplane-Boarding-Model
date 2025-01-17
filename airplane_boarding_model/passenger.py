"""A module for modeling a passenger of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import mesa

if TYPE_CHECKING:
    from .airplane import Seat
    from .boarding_model import BoardingModel


class Passenger(mesa.Agent):
    """A passenger of an airplane.
    
    Attributes:
        assigned_seat: The Seat object assigned to the passenger.
        steps_per_move: The number of steps it takes for the passenger to move.
        luggage_delay: The number of steps a passenger waits to store luggage.
        seated: Whether the passenger is seated.
        last_move: The number of steps since the passenger last moved.
    """
    
    def __init__(
        self,
        model: BoardingModel,
        luggage_delay: int,
        steps_per_move: int,
        assigned_seat: Seat = None,
        seated: bool = False,
    ):
        """Create a new passenger with the given parameters.
        
        Args:
            model: The BoardingModel object containing the passenger.
            luggage_delay: The number of steps a passenger waits to store luggage.
            steps_per_move: The number of steps it takes for the passenger to move.
            assigned_seat: The Seat object assigned to the passenger.
            seated: Whether the passenger is seated.
        """
        super().__init__(model)
        self.luggage_delay = luggage_delay
        self.steps_per_move = steps_per_move
        self.assigned_seat = assigned_seat
        self.seated = seated
        self.last_move = steps_per_move
        
    def step(self):
        """Advance the passenger by one step."""
        self.last_move += 1
        
        if self.seated:
            return
        
        # If in the correct row
        if self.pos[0] == self.assigned_seat.row:
            # If waiting to store luggage
            if self.luggage_delay > 0:
                self.luggage_delay -= 1
                return
            
            # If in the correct column
            if self.pos[1] == self.assigned_seat.column:
                self.seated = True
            else:
                direction = 1 if self.assigned_seat.column > self.pos[1] else -1
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
        
        if self.model.grid.is_cell_empty(target) and self.last_move >= self.steps_per_move:
            self.model.grid.move_agent(self, target)
            self.last_move = 0
            return True
        else:
            return False