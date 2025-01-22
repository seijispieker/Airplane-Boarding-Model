"""A module for modeling the boarding process of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import mesa

from .airbus_a320 import AirbusA320
from .passenger import Passenger

if TYPE_CHECKING:
    from .airbus_a320 import Seat


class BoardingModel(mesa.Model):
    """A class for modeling the boarding process of an airplane.
    
    Attributes:
        cell_width: The width of a grid cell in meters.
        aisle_steps_per_move: The number of steps to move one cell in the aisle.
        luggage_delay: The number of steps to wait for storing luggage.
        airplane: An AirbusA320 object representing the airplane.
        grid: A SingleGrid object representing the airplane grid.
        queue: A list of Passenger objects representing the queue of passengers.
        adherence: The percentage of passengers following the assigned order.
        datacollector: A DataCollector object for collecting data.
    """
    
    def __init__(
        self,
        seed: int = 42,
        steps_per_second: int = 2,
        aisle_speed: float = 0.8, # meters per second
        luggage_delay_seconds: float = 2,
        occupancy: float = 0.85,
        seat_assignment_method: str = "back_to_front",
        conformance: int = 95,
    ):
        """Initialize a BoardingModel object.
        
        Args:
            seed: The random seed for the model.
            steps_per_second: The number of simulation steps per second.
            aisle_speed: The speed of passengers in the aisle in meters per second.
            luggage_delay_seconds: The number of seconds to wait for storing luggage.
            occupancy: The percentage of occupied seats.
            seat_assignment_method: The method for assigning seats to passengers.
            conformance: The percentage of passengers following the assigned order.
        """
        super().__init__(seed=seed)
        
        self.cell_width = 0.4 # meters
        self.aisle_steps_per_move = round(aisle_speed / self.cell_width * steps_per_second)
        self.luggage_delay = round(steps_per_second * luggage_delay_seconds)
        
        self.airplane = AirbusA320()
        self.grid = mesa.space.SingleGrid(
            width=self.airplane.grid_width,
            height=self.airplane.grid_height,
            torus=False,
        )      
          
        self.queue = Passenger.create_agents(
            model=self,
            n=round(self.airplane.number_of_seats * occupancy),
            aisle_steps_per_move=self.aisle_steps_per_move,
            luggage_delay=self.luggage_delay,
        )    
            
        self.adherence = conformance
        self.airplane.assign_passengers(
            seats=getattr(self, f"seats_{seat_assignment_method}")(),
            queue=self.queue
        )

        # Place first passenger in the entrance
        self.grid.place_agent(
            agent=self.queue.pop(),
            pos=self.airplane.entrance
        )
        
        self.datacollector = mesa.DataCollector(
            model_reporters={"Queue Size": lambda model: len(model.queue)},
        )

    def step(self):
        # Check if there are passengers in the queue and the entrance is free
        if self.queue and self.grid.is_cell_empty(self.airplane.entrance):
            self.grid.place_agent(
                agent=self.queue.pop(),
                pos=self.airplane.entrance
            )

        self.grid.agents.shuffle_do("step")
        self.datacollector.collect(self)
                    
    def seats_back_to_front(self) -> list[Seat]:
        """Return a list of Seat objects in back to front order.
            
        Returns:
            A list of Seat objects in back to front order.
        """
        layout = list(reversed(self.airplane.seat_map))
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