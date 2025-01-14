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
        self.airplane.assign_passengers(self.queue)
        
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
                    #making a luggage delay for all agents before moving to correct column
                    if not hasattr(passenger, 'luggage_delay'):
                        passenger.luggage_delay = self.p.luggage_delay  #initializing luggage delay
                        
                    if passenger.luggage_delay > 0:
                        passenger.luggage_delay -= 1
                    else:
                        direction = 1 if passenger.assigned_seat.column > position[1] else -1
                        self.grid.move_by(passenger, (0, direction))
                else:
                    #move down the aisle if not at correct row
                    next_pos = (position[0] + 1, position[1])
                    self.grid.move_by(passenger, (1, 0))