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
        self.passing_delay = 0
        
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

        # with new rule where an agent can move through an agent if it's seated
        position = grid.positions[self]
        target_row = position[0] + drow
        target_col = position[1] + dcol

        if (0 <= target_row < grid.shape[0]) and (0 <= target_col < grid.shape[1]):
            target_agents = grid.grid[target_row, target_col][0]

            if len(target_agents) == 0:  # target cell is free
                grid.move_by(self, (drow, dcol))
                return True
            else:
                # Added for interaction delay
                seated_blocking = [agent for agent in target_agents if agent.seated]
                if seated_blocking:
                    if self.passing_delay > 0:
                        return False
                    else:
                        grid.move_by(self, (drow, dcol))
                        return True
                else:
                    return False
        return False
