"""A module for modeling the boarding process of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import agentpy as ap

from .airplane import Airplane
from .passenger import Passenger

if TYPE_CHECKING:
    from .airplane import Seat


class BoardingModel(ap.Model):
    """A model inherinting from agentpy.Model for simulating the boarding
    process of an airplane.
    
    Attributes:
        airplane: An Airplane object.
        queue: A list of Passenger objects waiting to board.
        last_boarded: Number of steps since the last passenger boarded.
        grid: A agentpy.Grid object as environment for the model.
    """
    
    def setup(self):
        """Create the airplane, queue, and grid. Assign passengers to seats
        back to front.
        """
        self.airplane = Airplane(
            rows=self.p.rows,
            columns=self.p.columns,
            aisle_column=self.p.aisle_column,
        )
        self.queue = ap.AgentList(self, self.p.passenger_count, Passenger)
        self.last_boarded = self.p.boarding_rate
        
        self.airplane.assign_passengers(
            self[self.p.seat_assignment_method](),
            self.queue
        )
        
        self.grid = ap.Grid(self, shape=(self.airplane.rows, self.airplane.columns))

    def step(self):
        """Move passengers to their seats and board new passengers."""
        # Board new passengers according to boarding rate
        if self.last_boarded >= self.p.boarding_rate:
            # Check if there are passengers in the queue and the entrance is free
            if self.queue and len(self.grid.grid[0, self.airplane.aisle_column][0]) == 0:
                self.grid.add_agents(
                    agents=[self.queue.pop(0)],
                    positions=[(0, self.airplane.aisle_column)]
                )
                self.last_boarded = 1
        else:
            self.last_boarded += 1

        # Move passengers to their seats
        for passenger in self.grid.agents:
            position = self.grid.positions[passenger]
            
            if not passenger.seated:
                # If in the correct row
                if position[0] == passenger.assigned_seat.row:
                    if passenger.luggage_delay > 0:
                        passenger.luggage_delay -= 1
                    else:
                        # If in the correct column
                        if position[1] == passenger.assigned_seat.column:
                            passenger.seated = True
                        else:
                            direction = 1 if passenger.assigned_seat.column > position[1] else -1
                            passenger.move_by(self.grid, drow=0, dcol=direction)
                else:
                    passenger.move_by(self.grid, drow=1, dcol=0)
                    
    def seats_back_to_front(self) -> list[Seat]:
        """Return a list of Seat objects in back to front order.
            
        Returns:
            A list of Seat objects in back to front order.
        """
        layout = list(reversed(self.airplane.layout))
        left_columns = [row[:self.airplane.aisle_column] for row in layout]
        right_columns = [list(reversed(row[self.airplane.aisle_column + 1:])) for row in layout]
        back_to_front = []
        
        for left_row, right_row in zip(left_columns, right_columns):
            for left_seat, right_seat in zip(left_row, right_row):
                back_to_front.append(left_seat)
                back_to_front.append(right_seat)

        return back_to_front
    
    def seats_random(self) -> list[Seat]:
        """Return a list of Seat objects in random order.
            
        Returns:
            A list of Seat objects in random order.
        """
        pass  # TODO: Implement this method
