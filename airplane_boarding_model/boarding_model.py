"""A module for modeling the boarding process of an airplane."""

import agentpy as ap

from .airplane import Airplane
from .passenger import Passenger


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
        if self.last_boarded == self.p.boarding_rate:
            if self.queue:
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
                if position[0] == passenger.assigned_seat.row:
                    if position[1] == passenger.assigned_seat.column:
                        passenger.seated = True
                    else:
                        direction = 1 if passenger.assigned_seat.column > position[1] else -1
                        self.grid.move_by(passenger, (0, direction))
                else:
                    self.grid.move_by(passenger, (1, 0))
                    
    def seats_back_to_front(self):
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
    
    def seats_random(self):
        """Return a list of Seat objects in random order.
            
        Returns:
            A list of Seat objects in random order.
        """
        pass  # TODO: Implement this method