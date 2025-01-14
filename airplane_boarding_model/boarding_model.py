import agentpy as ap

from .airplane import Airplane
from .passenger import Passenger


class BoardingModel(ap.Model):
    def setup(self):
        """
        Assign passengers to seats in a back-to-front order as the baseline model.
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
        if self.last_boarded == self.p.boarding_rate:
            if self.queue:
                self.grid.add_agents(
                    agents=[self.queue.pop(0)],
                    positions=[(0, self.airplane.aisle_column)]
                )
                self.last_boarded = 1
        else:
            self.last_boarded += 1

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