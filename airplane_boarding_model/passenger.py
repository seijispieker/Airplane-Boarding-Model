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

        #Initialize blocking_agents as an empty list
        self.blocking_agents = []
        
    def step(self):
        """Advance the passenger by one step."""
    
        row, col = self.assigned_seat.seat_row, self.assigned_seat.seat_column
        aisle_col = self.model.airplane.aisle_column
        temp_positions = [(row - 1, aisle_col), (row, aisle_col + 1)] if col < aisle_col else [(row - 1, aisle_col), (row, aisle_col - 1)]

        self.last_move += 1

        # If the passenger is seated, nothing happens
        if self.seated:
            return

        # If the passenger is waiting to be seated, do nothing
        if hasattr(self, "waiting_to_be_seated") and self.waiting_to_be_seated:

            #Checks if the relevant blocking agents have reached their final temporary positions down the aisle.
            if hasattr(self, "blocking_agents"):
                relevant_agents_done = all(agent.pos == (agent.target_temp_pos[0], aisle_col) for agent in self.blocking_agents)
                
                if relevant_agents_done:
                    self.waiting_to_be_seated = False #Unflag as waiting to be seated
                    self.blocking_agents.clear() #Clear the list of blocking agents
            return

        # If the passenger is still moving to a temporary position
        if hasattr(self, "blocking") and self.blocking:
            #Determines a target temporary position (row is 1 or 2 down)
            target_row = row + (2 if self.blocking == "further" else 1)
            
            #Move vertically (across row) toward the temporary position
            if self.pos[0] < target_row and self.pos[1] > aisle_col:
                self.move(drow = 0, dcol = -1)
            elif self.pos[0] < target_row and self.pos[1] < aisle_col:
                self.move(drow = 0, dcol= +1)
            elif self.pos[0] < target_row and self.pos[1] == aisle_col:
                self.move(drow = 1, dcol = 0)
            
            if self.pos == (target_row, aisle_col):
                self.blocking = False #Unflag current agent as blocking

        # If in the correct row
        if self.pos[0] == row:
            # Check for blocking agents
            columns_to_verify = range(col + 1, aisle_col) if col < aisle_col else range(aisle_col + 1, col)
            is_blocked = any(
                not self.model.grid.is_cell_empty((row, c)) for c in columns_to_verify
            )

            if is_blocked:
                # Flag blocking agents
                blocking_agents = []
                for c in columns_to_verify:
                    if not self.model.grid.is_cell_empty((row, c)):
                        blocking_agent = self.model.grid.get_cell_list_contents([(row, c)])[0]
                        blocking_agent.blocking = "further" if len(self.blocking_agents) == 0 else "closer"
                        blocking_agent.target_temp_pos = (row + (2 if len(self.blocking_agents) == 0 else 1), aisle_col)
                        blocking_agents.append(blocking_agent)

                # Move the passenger to a temporary position
                for temp_pos in temp_positions:
                    if self.model.grid.is_cell_empty(temp_pos):
                        self.move(drow=temp_pos[0] - self.pos[0], dcol=temp_pos[1] - self.pos[1])
                        self.waiting_to_be_seated = True  # Flag as waiting to be seated
                        return
            else:
                # If waiting to store luggage
                if self.luggage_time > 0:
                    self.luggage_time -= 1
                    return

                # If in the correct column
                if self.pos[1] == col:
                    self.seated = True
                    self.assigned_seat.occupied = True
                else:
                    direction = 1 if col > self.pos[1] else -1
                    self.move(drow=0, dcol=direction)
        else:
            # Move closer to the correct row
            self.move(drow=row - self.pos[0], dcol=0)
        
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