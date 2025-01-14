"""A module for modeling a passenger of an airplane."""

import agentpy as ap


class Passenger(ap.Agent):
    """A passenger inheriting from agentpy.Agent.
    
    Attributes:
        assigned_seat: The Seat object assigned to the passenger.
        seated: Whether the passenger is seated.
    """
    
    def setup(self):
        """Initialize the passenger."""
        self.assigned_seat = None
        self.seated = False
        self.luggage_delay = self.p.luggage_delay
        
    def move_by(self, grid: ap.Grid, drow: int, dcol: int) -> bool:
        """Move the passenger by the given row and column offset if the target
        is free.
        
        Args:
            grid: The grid to move on.
            drow: The row offset.
            dcol: The column offset.
        Returns:
            Whether the move was successful.
        """
        position = grid.positions[self]
        
        if len(grid.grid[position[0] + drow, position[1] + dcol][0]) == 0:
            grid.move_by(self, (drow, dcol))
            return True
        else:
            return False