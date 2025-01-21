"""A module for modeling the boarding process of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import mesa

from .airplane import Airplane
from .passenger import Passenger

if TYPE_CHECKING:
    from .airplane import Seat


class BoardingModel(mesa.Model):
    """A model for simulating the boarding process of an airplane.
    
    Attributes:
        seed: The random seed for the model.
        grid: SingleGrid object as an environment for the model.
        queue: Agentset of Passenger objects waiting to board.
        boarding_rate: The number of steps between boarding new passengers.
        entrance: The position of the entrance to the airplane.
        airplane: Airplane object containing the layout of the airplane.
        last_boarded: The number of steps since the last passenger was boarded.
        datacollector: DataCollector object for collecting data.
    """
    
    def __init__(
        self,
        seed: int = 42,
        rows: int = 30,
        columns: int = 7,
        aisle_column: int = 3,
        passenger_count: int = 180,
        steps_per_second: int = 1,
        movement_speed_cells_per_second: float = 1,
        boarding_rate_seconds: float = 1,
        luggage_delay_seconds: float = 2,
        seat_assignment_method: str = "back_to_front",
        adherence: int = 95,
    ):
        """Create a new boarding model with the given parameters.
        
        Args:
            seed: The random seed for the model.
            rows: The number of rows in the airplane.
            columns: The number of columns per row including aisle.
            aisle_column: The column number of the aisle.
            passenger_count: The number of passengers to board.
            movement_speed: The number of cells a passenger moves per second.
            boarding_rate: The number of seconds between boarding new passengers.
            luggage_delay: The number of seconds a passenger waits to store luggage.
            seat_assignment_method: The method used to assign passengers to
                seats given a queue of passengers.
        """
        print("Initializing new Boarding Model")
        super().__init__(seed=seed)
        
        self.grid = mesa.space.SingleGrid(
            width=rows,
            height=columns,
            torus=False,
        )
        
        self.steps_per_move = round(steps_per_second * movement_speed_cells_per_second)
        self.luggage_delay = round(steps_per_second * luggage_delay_seconds)
        self.boarding_rate = round(steps_per_second * boarding_rate_seconds)
        
        print(f"Steps per move: {self.steps_per_move}")
        print(f"Luggage delay: {self.luggage_delay} steps")
        print(f"Boarding rate: {self.boarding_rate} steps")
        
        self.adherence = adherence
        self.queue = Passenger.create_agents(
            model=self,
            n=int(passenger_count),
            luggage_delay=self.luggage_delay,
            steps_per_move=self.steps_per_move,
        )
        
        self.entrance = (0, aisle_column)
        
        # Create airplane and assign passengers seats
        self.airplane = Airplane(rows, columns, aisle_column)
        self.airplane.assign_passengers(
            seats=getattr(self, f"seats_{seat_assignment_method}")(),
            queue=self.queue
        )
        
        # Place first passenger in the entrance
        self.grid.place_agent(
            agent=self.queue.pop(),
            pos=self.entrance
        )
        self.last_boarded = 1
        
        self.datacollector = mesa.DataCollector(
            model_reporters={"Queue Size": lambda model: len(model.queue)},
        )

    def step(self):
        """Advance the model by one step.
        
        The model advances by boarding new passengers according to the boarding
        rate and moving all agents one step.
        """
        # Board new passengers according to boarding rate
        if self.last_boarded >= self.boarding_rate:
            # Check if there are passengers in the queue and the entrance is free
            if self.queue and self.grid.is_cell_empty(self.entrance):
                self.grid.place_agent(
                    agent=self.queue.pop(),
                    pos=self.entrance
                )
                self.last_boarded = 1
        else:
            self.last_boarded += 1
        
        self.grid.agents.shuffle_do("step")
        self.datacollector.collect(self)
                    
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
        back_to_front = self.padherence(back_to_front)
        return back_to_front
    
    def seats_random(self) -> list[Seat]:
        """Return a list of Seat objects in random order.
            
        Returns:
            A list of Seat objects in random order.
        """
        pass  # TODO: Implement this method

    def padherence(self, method_list):
        adherence= 100 - self.adherence
        amount_to_swap = round(len(method_list) * adherence / 100, 0)
        
        random_index_list = []
        while len(random_index_list) < amount_to_swap:
            i = self.random.randint(0, len(method_list)-1)
            if i not in random_index_list:
                random_index_list.append(i)
        
        if amount_to_swap % 2 == 0: # check if the list can be split into 2
            for j in range(int(amount_to_swap / 2)): 
                method_list[random_index_list[j]], method_list[random_index_list[-j]-1] = method_list[random_index_list[-j]-1], method_list[random_index_list[j]] # swapping first half of random indexes with second half of rng indexes
        else:
            for j in range(int((amount_to_swap-1) / 2)): # doing the same as before only the middle number of the list will be swapped with the first item in the random index list
                method_list[random_index_list[j]], method_list[random_index_list[-j]-1] = method_list[random_index_list[-j]-1], method_list[random_index_list[j]]
            method_list[random_index_list[int((amount_to_swap-1) / 2)]] , method_list[random_index_list[0]] = method_list[random_index_list[0]], method_list[random_index_list[int((amount_to_swap-1) / 2)]] 
        return method_list