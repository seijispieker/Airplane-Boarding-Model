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
        number_of_passengers: int = -1,
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
        self.aisle_steps_per_move = round(1 / (aisle_speed / self.cell_width / steps_per_second))
        
        self.adherence = conformance
        self.airplane = AirbusA320()
        
        if int(number_of_passengers) > 0:
            self.number_of_passengers = int(number_of_passengers)
        else:
            self.number_of_passengers = round(self.airplane.number_of_seats * occupancy)
        
        self.grid = mesa.space.SingleGrid(
            width=self.airplane.grid_width,
            height=self.airplane.grid_height,
            torus=False,
        )
        self.frozen_aisle_cells = [False] * self.airplane.grid_width
        
        self.passengers = Passenger.create_agents(
            model=self,
            n=self.number_of_passengers,
            aisle_steps_per_move=self.aisle_steps_per_move
        )
        
        # Schultz 2018:
        lambd = 1 / (self.steps_per_second * 3.7)
        inter_arrival_times = [self.random.expovariate(lambd) for _ in range(self.number_of_passengers - 1)]
        # TODO: does first passenger need to arrive at time 1?
        inter_arrival_times.insert(0, 1)
        self.inter_arrival_times = inter_arrival_times
        arrival_timestamps = list(map(round, np.cumsum(inter_arrival_times)))
        
        # Assign timestamps to passengers
        for passenger, timestamp in zip(self.passengers, arrival_timestamps):
            passenger.arrival_time = timestamp

        self.passengers.sort(key=lambda p: p.arrival_time)
        self.queue = []

        seat_assignment_method = getattr(self, f"seats_{seat_assignment_method}")
        self.assigned_seats = seat_assignment_method()
        self.assigned_seats = self.assigned_seats[:self.number_of_passengers]
        self.airplane.assign_passengers(
            seats=self.assigned_seats,
            passengers=self.passengers
        )
        
        # Place none passenger agent in grid, otherwise visualization will crash
        dull_agent = mesa.Agent(self)
        self.grid.place_agent(
            agent=dull_agent,
            pos=(0,0)
        )
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Time (s)": lambda model: model.steps / self.steps_per_second,
                "Boarding completed": lambda model: not model.running,
            },
            agent_reporters={
                "Seat shuffle time (s)": lambda passenger: passenger.seat_shuffle_time / self.steps_per_second,
                "Seat shuffle type (A/B/C/D)": "seat_shuffle_type",
            }
        )

    def step(self):
        """Advance the model by one step.""" 
        # Add passengers to queue based on arrival time
        arrived_at_queue = self.passengers.select(lambda p: p.arrival_time == self.steps)
        
        if arrived_at_queue:
            for passenger in arrived_at_queue:
                self.queue.append(passenger)
                self.passengers.remove(passenger)

        if self.queue and self.grid.is_cell_empty(self.airplane.entrance):
            passenger = self.queue.pop(0)
            self.grid.place_agent(agent=passenger, pos=self.airplane.entrance)
            
            if not self.grid.is_cell_empty((0,0)):
                dull_agent = self.grid.get_cell_list_contents((0,0))[0]
                self.grid.remove_agent(dull_agent)
                self.agents.remove(dull_agent)

        self.grid.agents.shuffle_do("step")

        all_seated = all(seat.occupied for seat in self.assigned_seats)

        if len(self.queue) == 0 and all_seated:
            self.running = False
            
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
        back_to_front = self.passenger_adherence(back_to_front)
        return back_to_front
    
    def seats_random(self) -> list[Seat]:
        """Return a list of Seat objects in random order.
            
        Returns:
            A list of Seat objects in random order.
        """
        all_seats = self.airplane.seats_list()
        self.random.shuffle(all_seats)
        return all_seats
    
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
        segments = 4
        passengers = self.number_of_passengers
        rows = len(self.airplane.seat_map)
        
        passenger_count_per_segment = []

        #-- first we determine the length in rows of each segment
        extra_rows = 0
        rows_list = []
        
        #determening the amount of rows each segments holds
        if rows % segments == 0: 
            rows_per_segment = rows / segments
        else:  # if rows cant be equally segmented one row is added to the amount of needed segments
            while rows % segments != 0:
                rows -= 1 
                extra_rows += 1 
            rows_per_segment = rows / segments

        for _ in range(segments): # adding the amount of rows to a list where each element is the amount of rows in the segment
                if extra_rows > 0:
                    rows_list.append([rows_per_segment + 1])
                    extra_rows -= 1
                else: 
                    rows_list.append([rows_per_segment])   
        
        
        #-- secondly we determine the amount of passengers that will inhabit each segment
        seg_length = passengers / segments
        if seg_length < 43:
            if passengers % segments == 0: # equally devide the amount of passengers in the amount of segments
                
                for _ in range(segments):
                    passenger_count_per_segment.append(int(seg_length))

            else: #devide the amount of passengers in the amount of segments, and add the extra passengers to the first segments
                extra_passenger = 0 
                while passengers % segments != 0: #det amount of extra passengers
                    extra_passenger += 1
                    passengers -= 1 

                
                for _ in range(segments): # adding extra passengers to the first segment,  and second if needed 
                    if extra_passenger > 0:
                        passenger_count_per_segment.append(int(seg_length + 1))
                        extra_passenger -= 1
                    else: 
                        passenger_count_per_segment.append(int(seg_length))
        else: 
            passenger_count_per_segment = [ 0, 0, 0, 0]
            passengers = self.number_of_passengers
            i = 0
            while passengers > 0:
                if i == 0:
                    passenger_count_per_segment[i] += 1
                    i += 1
                    passengers -= 1
                elif i == 1 and passenger_count_per_segment[i] < 42:
                    passenger_count_per_segment[i] += 1
                    i += 1
                    passengers -= 1
                elif i == 2 and passenger_count_per_segment[i] < 42:
                    passenger_count_per_segment[i] += 1
                    i += 1
                    passengers -= 1
                elif i == 3 and passenger_count_per_segment[i] < 42:
                    passenger_count_per_segment[i] += 1
                    i = 0
                    passengers -= 1
                else:
                    i = 0
        
        
         
        
        #-- thirdly we split the airlplane layout into the respective segments
        layout = self.airplane.seat_map
        
        segmented_layout = []
        i = 0
        row_i = 0
        for rows_per_segment in rows_list:
            segmented_layout.append([])
            for rows in rows_per_segment:
                rows = int(rows)
                for _ in range(rows):
                    j = -3
                    for _ in range(6):
                        segmented_layout[i].append(layout[row_i][j])
                        j += 1
                    row_i += 1
            i += 1 

        #for each segment take the passenger_count seats randomly
        random_segmented_seats = []
        i = 0
        for segment in passenger_count_per_segment:
            seats_picked = 0
            max_seats = [48, 42, 42, 42]
            
            random_segmented_seats.append([])
            while seats_picked < passenger_count_per_segment[i]:
                random_seat = self.random.randint(0, max_seats[i] - 1)
                
                if segmented_layout[i][random_seat] not in random_segmented_seats[i]:
                    random_segmented_seats[i].append(segmented_layout[i][random_seat])
                    seats_picked += 1                               
            i += 1
        
        flatten = lambda xss: [x for xs in xss for x in xs]
        method_list = flatten(random_segmented_seats)
        method_list = self.passenger_adherence(method_list)
        
        i = -1
        reversed_method_list= []
        for _ in range(len(method_list)):
            reversed_method_list.append(method_list[i])
            i -= 1
        return reversed_method_list
                
    def seats_outside_in(self) -> list[Seat]:
        segments = 3 # window, middle seat, aile seat
        passengers = self.number_of_passengers
        passenger_count_per_segment = []
        layout = self.airplane.seat_map

        total_seats = 0
        for row in layout:
            total_seats += len(row) - 1
        seats_per_segment = total_seats / segments

        #determening how filled the segments are
        i = 0
        while passengers > 0:
            assigned_seats = 0
            while assigned_seats < seats_per_segment and passengers > 0:
                passengers -= 1
                assigned_seats += 1
            passenger_count_per_segment.append(assigned_seats)
            i += 1

        #creating seat layout for the outside in method
        segmented_layout = [[],[],[]]
        i = 0
        left = 0
        right = -1
        for _ in range(segments):
            for row in layout:
                segmented_layout[i].append(row[left])
                segmented_layout[i].append(row[right])
            left += 1
            right -= 1
            i += 1
        
        for segment in segmented_layout:
            self.random.shuffle(segment)
        
        #for each passenger assign save a seat untill all passengers have a seat
        i = 0
        method_list = [[],[],[]]
        for passenger_count in passenger_count_per_segment:
            
            for j in range(passenger_count):
                method_list[i].append(segmented_layout[i][j])
                
            i += 1

        flatten = lambda xss: [x for xs in xss for x in xs]
        method_list = flatten(method_list)
        method_list = self.passenger_adherence(method_list)
        
        return method_list

    def seats_steffen_perfect(self) -> list[Seat]:
        #using outside in layout
        segments = 3
        layout = self.airplane.seat_map
        segmented_layout = [[],[],[]]
        i = 0
        left = 0
        right = -1
        for _ in range(segments):
            for row in layout:
                segmented_layout[i].append(row[left])
                segmented_layout[i].append(row[right])
            left += 1
            right -= 1
            i += 1
        
        #creating 12 segments where each segment is a "group" in the steffen method
        steffen_layout = []
        i = 0
        for _ in range(12): # steffen is done in 12 steps
            steffen_layout.append([])
        for segment in segmented_layout:
            seat = 4
            for element in segment: # using the defined steffen groups to seperate 
                if int(str(element)[:-1]) % 2 == 0:
                    if str(element)[-1:] in ["A", "B", "C"]:
                        steffen_layout[i].append(element)
                    else:
                        steffen_layout[i + 1].append(element)
                else:
                    if str(element)[-1:] in ["A", "B", "C"]:
                        steffen_layout[i + 2].append(element)
                    else:
                        steffen_layout[i + 3].append(element)
            i += 4 
        
        #reversing the groups to get the correct order
        i=0
        for steffen_group in steffen_layout:
            steffen_group = reversed(steffen_group)
            steffen_layout[i] = steffen_group
            i+=1
        
        #flattening the list of lists into a single big list
        flatten = lambda xss: [x for xs in xss for x in xs]
        method_list = flatten(steffen_layout)
        method_list = self.passenger_adherence(method_list)

        return method_list
    
    def seats_debug_B(self) -> list[Seat]:
        self.number_of_passengers = 10
        self.passengers = mesa.agent.AgentSet(self.passengers[:10], random=self.random)
        for i, passenger in enumerate(self.passengers):
            if i < 1:
                passenger.arrival_time = 1 + i * self.steps_per_second
            else:
                passenger.arrival_time = 1 + i * self.steps_per_second + 10 * self.steps_per_second
            
            passenger.luggage_time = 2 * self.steps_per_second
        return [self.airplane.seat_map[0][4], self.airplane.seat_map[0][5]] + self.airplane.seats_list()[-8:]
    
    def seats_debug_C(self) -> list[Seat]:
        self.number_of_passengers = 10
        self.passengers = mesa.agent.AgentSet(self.passengers[:10], random=self.random)
        for i, passenger in enumerate(self.passengers):
            if i < 1:
                passenger.arrival_time = 1 + i * self.steps_per_second
            else:
                passenger.arrival_time = 1 + i * self.steps_per_second + 10 * self.steps_per_second
            passenger.luggage_time = 2 * self.steps_per_second
        return [self.airplane.seat_map[0][5], self.airplane.seat_map[0][6]] + self.airplane.seats_list()[-8:]
    
    def seats_debug_D(self) -> list[Seat]:
        self.number_of_passengers = 10
        self.passengers = mesa.agent.AgentSet(self.passengers[:10], random=self.random)
        for i, passenger in enumerate(self.passengers):
            # print(passenger.unique_id)
            if i < 2:
                passenger.arrival_time = 1 + i * self.steps_per_second
            else:
                passenger.arrival_time = 1 +i * self.steps_per_second + 10 * self.steps_per_second
            passenger.luggage_time = 2 * self.steps_per_second
        return [self.airplane.seat_map[0][5], self.airplane.seat_map[0][4], self.airplane.seat_map[0][6]] + self.airplane.seats_list()[-7:]
        
        
        
        

            
            
            
        
        
        


