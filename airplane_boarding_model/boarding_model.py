"""A module for modeling the boarding process of an airplane."""

from __future__ import annotations
from typing import TYPE_CHECKING

import mesa

from .airplane import Airplane
from .passenger import Passenger
from random import randint
from random import shuffle
if TYPE_CHECKING:
    from .airplane import Seat


class BoardingModel(mesa.Model):
    """A model for simulating the boarding process of an airplane.
    
    Attributes:
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
        rows: int = 30,
        columns: int = 7,
        aisle_column: int = 3,
        passenger_count: int = 180,
        boarding_rate: int = 2,
        luggage_delay: int = 2,
        boarding_method: str = "back_to_front",
        seed: int = 42,
        adherence: int = 95,
    ):
        self.adherence = adherence
        self.rows = rows
        self.passenger_count = passenger_count
        """Create a new boarding model with the given parameters.
        
        Args:
            rows: The number of rows in the airplane.
            columns: The number of columns per row including aisle.
            aisle_column: The column number of the aisle.
            passenger_count: The number of passengers to board.
            boarding_rate: The number of steps between boarding new passengers.
            luggage_delay: The number of steps a passenger waits to store luggage.
            boarding_method: The method used to assign passengers to seats.
            seed: The random seed for the model.
        """
        super().__init__(seed=seed)
        
        self.grid = mesa.space.SingleGrid(
            width=rows,
            height=columns,
            torus=False,
        )
        
        self.queue = Passenger.create_agents(
            model=self,
            n=int(passenger_count),
            luggage_delay=luggage_delay,
        )
        
        self.boarding_rate = boarding_rate
        self.entrance = (0, aisle_column)
        
        # Create airplane and assign passengers seats
        self.airplane = Airplane(rows, columns, aisle_column)
        self.airplane.assign_passengers(
            seats=getattr(self, f"seats_{boarding_method}")(),
            passengers=self.queue
        )
        
        # Place first passenger in the entrance
        self.grid.place_agent(
            agent=self.queue.pop(),
            pos=self.entrance
        )
        self.last_boarded = 0
        
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
            i = randint(0, len(method_list)-1)
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
        segments = 3
        passengers = self.passenger_count
        rows = self.rows 
        passenger_count_per_segment = []

        #--first we determine the amount of passengers that will inhabit each segment
        if passengers % segments == 0: # equally devide the amount of passengers in the amount of segments
            seg_length = passengers / segments
            for _ in range(segments):
                passenger_count_per_segment.append(int(seg_length))

        else: #devide the amount of passengers in the amount of segments, and add the extra passengers to the first segments
            extra_passenger = 0 
            while passengers % segments != 0: #det amount of extra passengers
                extra_passenger += 1
                passengers -= 1 

            seg_length = passengers / segments
            for _ in range(segments): # adding extra passengers to the first segment,  and second if needed 
                if extra_passenger > 0:
                    passenger_count_per_segment.append(int(seg_length + 1))
                    extra_passenger -= 1
                else: 
                    passenger_count_per_segment.append(int(seg_length))
        
        #-- secondly we determine the length in rows of each segment
        rows = self.rows 
        extra_rows = 0
        rows_list = []

        #determening the amount of rows each segments holds
        if rows % segments == 0: 
            rows_per_segment = rows / segments
        else:  # if rows cant be equally segmented one row is added to the amount of needed segments
            while rows % segments != 0:
                rows - 1 
                extra_rows += 1 
            rows_per_segment = rows / segments

        for _ in range(segments): # adding the amount of rows to a list where each element is the amount of rows in the segment
                if extra_rows > 0:
                    rows_list.append([rows_per_segment + 1])
                    extra_rows -= 1
                else: 
                    rows_list.append([rows_per_segment])    
        
        #-- thirdly we split the airlplane layout into the respective segments
        layout = self.airplane.layout
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
            
            random_segmented_seats.append([])
            while seats_picked < passenger_count_per_segment[i]:
                random_seat = randint(0, segment - 1)
                if segmented_layout[i][random_seat] not in random_segmented_seats[i]:
                    random_segmented_seats[i].append(segmented_layout[i][random_seat])
                    seats_picked += 1                               
            i += 1
        
        flatten = lambda xss: [x for xs in xss for x in xs]
        method_list = flatten(random_segmented_seats)
        method_list = self.passenger_adherence(method_list)
        return reversed(method_list)

    def seats_outside_in(self) -> list[Seat]:
        segments = 3 # window, middle seat, aile seat
        passengers = self.passenger_count
        passenger_count_per_segment = []
        seats_per_segment = self.rows * self.columns / segments

        #determening how filled the segments are
        i = 0
        while passengers > 0:
            assigned_seats = 0
            while assigned_seats > seats_per_segment:
                passengers -= 1
                assigned_seats += 1
            passenger_count_per_segment.append([assigned_seats])
            i += 1

        #creating seat layout for the outside in method
        layout = self.airplane.layout
        segmented_layout = [[],[],[]]
        
        
        i = 0
        left = 0
        right = -1
        for _ in range(segments):
            for row in layout:
                segmented_layout[i].append(row[left], row[right])
            left += 1
            right -= 1
        print(segmented_layout)
                
        
        
        
        
        

            
            
            
        
        
        


