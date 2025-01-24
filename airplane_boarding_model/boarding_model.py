"""A module for modeling the boarding process of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import mesa
import mesa.agent
import numpy as np

from .airbus_a320 import AirbusA320
from .passenger import Passenger

if TYPE_CHECKING:
    from .airbus_a320 import Seat


class BoardingModel(mesa.Model):
    """A class for modeling the boarding process of an airplane.
    
    Attributes:
        cell_width: The width of a grid cell in meters.
        steps_per_second: The number of simulation steps per second.
        aisle_steps_per_move: The number of steps to move one cell in the aisle.
        airplane: An AirbusA320 object representing the airplane.
        grid: A SingleGrid object representing the airplane grid.
        queue: A list of Passenger objects representing the queue of passengers.
        adherence: The percentage of passengers following the assigned order.
        assigned_seats: A list of Seat objects representing the assigned seats.
        datacollector: A DataCollector object for collecting data.
    """
    
    def __init__(
        self,
        seed: int = 42,
        steps_per_second: int = 2,
        aisle_speed: float = 0.8, # meters per second
        occupancy: float = 0.85,
        seat_assignment_method: str = "back_to_front",
        conformance: int = 100,
    ):
        """Initialize a BoardingModel object.
        
        Args:
            seed: The random seed for the model.
            steps_per_second: The number of simulation steps per second.
            aisle_speed: The speed of passengers in the aisle in meters per second.
            occupancy: The percentage of occupied seats.
            seat_assignment_method: The method for assigning seats to passengers.
            conformance: The percentage of passengers following the assigned order.
        """
        seed = int(seed)
        super().__init__(seed=seed)
        
        self.cell_width = 0.4 # meters
        self.steps_per_second = steps_per_second
        self.aisle_steps_per_move = round(aisle_speed / self.cell_width * steps_per_second)
        
        self.airplane = AirbusA320()
        self.grid = mesa.space.SingleGrid(
            width=self.airplane.grid_width,
            height=self.airplane.grid_height,
            torus=False,
        )    
        
        number_of_passengers = round(self.airplane.number_of_seats * occupancy)
        luggage_sample = self.random.choices(
            population=[1, 2, 3],
            weights=[0.6, 0.3, 0.1],
            k=number_of_passengers
        )
        single_luggage = Passenger.create_agents(
            model=self,
            n=luggage_sample.count(1),
            aisle_steps_per_move=self.aisle_steps_per_move,
            luggage_items=1
        )
        two_luggage = Passenger.create_agents(
            model=self,
            n=luggage_sample.count(2),
            aisle_steps_per_move=self.aisle_steps_per_move,
            luggage_items=2
        )
        three_luggage = Passenger.create_agents(
            model=self,
            n=luggage_sample.count(3),
            aisle_steps_per_move=self.aisle_steps_per_move,
            luggage_items=3
        )
        self.passengers = mesa.agent.AgentSet(single_luggage | two_luggage | three_luggage,
                                         random=self.random)   # Changed to self.passengers
        assert len(self.passengers) == number_of_passengers  

        self.current_time = 0 # Added

        # Generate inter-arrival times based on exponential distribution, 5 should be validated (3.7 with lambda = 1)
        inter_arrival_times = [self.random.expovariate(1 / (steps_per_second * 5)) for _ in range(number_of_passengers)]
        arrival_timestamps = list(map(int, np.cumsum(inter_arrival_times)))

        # Assign timestamps to passengers
        for passenger, timestamp in zip(self.passengers, arrival_timestamps):
            passenger.arrival_time = timestamp

        # Initialially empty queue
        self.queue = sorted(self.passengers, key=lambda p: p.arrival_time)   
          
        self.adherence = conformance
        # TODO: seat_assignment_method with input number of seats
        self.assigned_seats = getattr(self, f"seats_{seat_assignment_method}")()
        self.assigned_seats = self.assigned_seats[:number_of_passengers]
        assert len(self.assigned_seats) == len(self.queue)
        self.airplane.assign_passengers(
            seats=self.assigned_seats,
            queue=self.queue
        )

        # Place first passenger in the entrance
        self.grid.place_agent(
            agent=self.queue.pop(),
            pos=self.airplane.entrance
        )
        
        self.datacollector = mesa.DataCollector(
            model_reporters={"Time (s)": lambda model: model.steps * model.steps_per_second},
        )

    def step(self):
        """Advance the model by one step."""
        self.current_time += 1
        passengers_to_remove = []

        #Debug
        print('Step:', self.current_time)
        print('Queue size before:', len(self.queue), 'Passenger remaining:', len(self.passengers))

        # Add passengers to queue based on arrival time
        for passenger in self.passengers:
            if passenger.arrival_time <= self.current_time:
                self.queue.append(passenger)
                passengers_to_remove.append(passenger)

        for passenger in passengers_to_remove:
            self.passengers.remove(passenger)

        #Debug
        print('Queue size after:', len(self.queue), 'Passenger remaining:', len(self.passengers))

        # Check if there are passengers in the queue and the entrance is free
        # Original code:
        #if self.queue and self.grid.is_cell_empty(self.airplane.entrance):
            #self.grid.place_agent(
                #agent=self.queue.pop(0),
                #pos=self.airplane.entrance
            #)

        # New code
        if self.queue and self.grid.is_cell_empty(self.airplane.entrance):
            passenger = self.queue.pop(0)
            self.grid.place_agent(agent=passenger, pos=self.airplane.entrance)
            print(f"Passenger {passenger.unique_id} entered the plane at time {self.current_time}")

        # Debug
        occupied_seats = sum(seat.occupied for seat in self.assigned_seats)
        print(f'Occupied seats: {occupied_seats} / {len(self.assigned_seats)}')

        self.grid.agents.shuffle_do("step")
        self.datacollector.collect(self)

        if all(seat.occupied for seat in self.assigned_seats):
            self.running = False
            print('All seats occupied')
                    
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
        back_to_front = self.passenger_adherence(back_to_front)
        return back_to_front
    
    def seats_random(self) -> list[Seat]:
        """Return a list of Seat objects in random order.
            
        Returns:
            A list of Seat objects in random order.
        """
        pass  # TODO: Implement this method
    
    def passenger_adherence(self, method_list):
        '''
        function that randomizes a given percentage of the "method list" (queue), thus simulating people that do not follow the method rules.
        '''

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
    
    def seats_segmented_random(self) -> list[Seat]:
        '''
        method for filling the airplane (which has been segmented into 3 parts) with random assignment in each segment
        '''
        # using the back to front as a base
        layout = list(reversed(self.airplane.seat_map))
        left_columns = [row[:self.airplane.aisle_column] for row in layout]
        right_columns = [list(reversed(row[self.airplane.aisle_column + 1:])) for row in layout]
        back_to_front = []
        
        for left_row, right_row in zip(left_columns, right_columns):
            for left_seat, right_seat in zip(left_row, right_row):
                back_to_front.append(left_seat)
                back_to_front.append(right_seat)
    
        # splitting back to front into 3 segments
        segments = 3 

        
        method_list = []
        if self.airplane.seat_rows % segments == 0: 
            seg_length = len(back_to_front) / segments

            seats_count = 0
            list_counter = 0
            for _ in range(segments):
                method_list.append([])

                segment_counter = 0
                while segment_counter < seg_length:
                    method_list[list_counter].append(back_to_front[seats_count])
                    segment_counter += 1 
                    seats_count += 1

                list_counter += 1

            list_counter = 0
            for _ in range(segments):
                self.random.shuffle(method_list[list_counter])
                list_counter += 1
            
            flatten = lambda xss: [x for xs in xss for x in xs]
            method_list = flatten(method_list)
            method_list = self.passenger_adherence(method_list)
            return method_list
    
        else: 
            print("plane not able to be segmented (To implement)")


