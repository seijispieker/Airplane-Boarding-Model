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
        seat_steps_per_move: The number of steps to move one cell in the seat
            row, out of the seat row or into the seat row.
        seat_reaction_time: The number of steps for the passenger to react
            before moving into the seat row, or starting a seat shuffle.
        luggage_time: The number of steps to store luggage.
        assigned_seat: The Seat assigned to the passenger.
        seated: True if the passenger is seated, False otherwise.
        last_move: The number of steps since the last move.
        arrival_time: The time step when the passenger will arrive at the queue.
        seat_shuffle: True if the passenger is in a seat shuffle situation,
            False otherwise. Does not count seat shufftle type A.
        shuffle_out_of_seat: If in a seat shuffle situation, True if the
            passenger is shuffling out of the seat, False otherwise.
        shuffle_into_seat: If in a seat shuffle situation, True if the passenger
            is shuffling into the seat, False otherwise.
        waiting_for_shuffling: If in a seat shuffle situation, True if the
            passenger is waiting for shuffling, False otherwise. In cases where
            the passenger is waiting for other passengers to shuffle out of the
            seats.
        shuffle_precedence: If in a seat shuffle situation, True if the
            passenger has precedence in shuffling over the other passengers.
        passengers_shuffling: If in a seat shuffle situation, a list of
            Passenger objects representing the other passengers who are in the
            seat shuffle situation.
        seat_shuffle_time: The number of steps it takes for the passenger to
            clear the aisle during a seat shuffle. Starts after the luggage and
            reaction time. And when the seat shuffle can start. Therefore, the
            aisle has space for the seat shuffle.
        seat_shuffle_waiting_time: The number of steps the passenger has waited
            for a seat shuffle to start because of the aisle being blocked.
            Therefore excluding the luggage and reaction time.
        seat_shuffle_type: The type of seat shuffle.
            - A: No passengers blocking the seat row, therefore no seat shuffle.
            - B: One passenger blocking the aisle seat.
            - C: One passenger blocking the middle seat.
            - D: Two passengers blocking the aisle and middle seat.
        target_x: The target x grid coordinate of the passenger is moving to.
        target_y: The target y grid coordinate of the passenger is moving to.
    """
    
    def __init__(
        self,
        model: BoardingModel,
        aisle_steps_per_move: int,
        assigned_seat: Seat = None,
        seated: bool = False,
    ):
        """Initialize a Passenger object."""
        super().__init__(model)
        self.aisle_steps_per_move = aisle_steps_per_move
        
        # Seat interaction depends on:
        #   - aisle is free for seat shuffle if needed
        #   - aisle movement speed
        #   - seat movement time
        #   - seat reaction time
        #   - luggage time x number of luggage items
        
        # Based on Schultz 2008/2013:
        seat_movement_time = self.model.random.triangular(
            low=1.8,
            high=3.0,
            mode=2.4
        )
        seat_steps_per_move = round(seat_movement_time * model.steps_per_second)
        self.seat_steps_per_move = seat_steps_per_move
        
        # Based on Schultz 2008/2013:
        seat_reaction_time = self.model.random.triangular(
            low=6,
            high=20, 
            mode=9
        )
        seat_reaction_time = round(seat_reaction_time * model.steps_per_second)
        self.seat_reaction_time = seat_reaction_time
        
        # Alpha and beta based on Schultz 2018:
        single_luggage_time = self.model.random.weibullvariate(
            alpha=16,
            beta=1.7
        )
        # Distribution of luggage items based on Schultz 2008/2013:
        luggage_items = self.model.random.choices(
            population=[1, 2, 3],
            weights=[0.6, 0.3, 0.1],
            k=1
        )[0]
        luggage_time = luggage_items * single_luggage_time
        self.luggage_time = round(luggage_time * model.steps_per_second)
        
        self.assigned_seat = assigned_seat
        self.seated = seated
        
        self.last_move = aisle_steps_per_move
        self.arrival_time = 0
        
        # For seat shuffle
        self.seat_shuffle = False
        self.shuffle_out_of_seat = False
        self.shuffle_into_seat = False
        self.waiting_for_shuffling = False
        self.shuffle_precedence = False
        self.passengers_shuffling = []
        
        # For data collection
        self.seat_shuffle_time = 0 
        self.seat_shuffle_waiting_time = 0
        self.seat_shuffle_type = "A"
        
        if assigned_seat is not None:
            self.target_x, self.target_y = assigned_seat.grid_coordinate
        else:
            self.target_x, self.target_y = (None, None)
        
    def step(self):
        """Advance the passenger by one step."""
        seat_x, seat_y = self.assigned_seat.grid_coordinate
        aisle_column = self.model.airplane.aisle_column
        
        if self.shuffle_out_of_seat:
            # If shuffled out of seat and at temporary position in aisle
            if self.at_target():
                # Set to waiting for shuffling and change target to seat
                self.shuffle_out_of_seat = False
                self.waiting_for_shuffling = True
                seat_coordinate = self.assigned_seat.grid_coordinate
                self.target_x, self.target_y = seat_coordinate
            else:
                self.move_to_target()
        elif self.shuffle_into_seat:
            # While aisle is blocked increment seat shuffle time
            if self.shuffle_precedence and self.seat_shuffle:
                self.seat_shuffle_time += 1
                                        
            if self.at_target():
                self.shuffle_into_seat = False
                self.seated = True
                self.assigned_seat.occupied = True
            else:                    
                self.move_to_target()
                
            if self.seat_shuffle and not self.shuffle_precedence:
                first_passenger = self.passengers_shuffling[0]
                
                # If passengers without precendence are out of the aisle
                if first_passenger.all_passengers_shuffling_out_of_aisle():
                    self.model.frozen_aisle_cells[seat_x] = False
                    
                    first_passenger.seat_shuffle = False
                    for passenger in first_passenger.passengers_shuffling:
                        passenger.seat_shuffle = False
        elif self.waiting_for_shuffling:
            if self.shuffle_precedence:
                self.seat_shuffle_time += 1
                
                # If blocking passengers are in the aisle, I can start moving
                # to my seat
                if self.all_passengers_shuffling_in_aisle():
                    self.waiting_for_shuffling = False
                    self.shuffle_into_seat = True
                    self.move_to_target()
            else:                
                if self.all_passengers_shuffling_out_of_aisle():
                    self.waiting_for_shuffling = False
                    self.shuffle_into_seat = True
                    self.move_to_target()
        # If at seat row - 1 and target seat row has blocking passengers
        elif (
            self.pos[1] == aisle_column
            and self.pos[0] == seat_x - 1
            and self.get_blocking_passengers() != []
        ):
            # If waiting to store luggage
            if self.luggage_time > 0:
                self.luggage_time -= 1
                return
            
            # If waiting for seat reaction time
            if self.seat_reaction_time > 0:
                self.seat_reaction_time -= 1
                return
            
            self.passengers_shuffling = self.get_blocking_passengers()
            
            # If enough space for seat shuffle in aisle
            if (
                (len(self.passengers_shuffling) == 1
                 and self.model.grid.is_cell_empty((seat_x, aisle_column))
                 and self.model.grid.is_cell_empty((seat_x + 1, aisle_column))
                 and not self.model.frozen_aisle_cells[seat_x]
                 and not self.model.frozen_aisle_cells[seat_x + 1])
                or
                (len(self.passengers_shuffling) == 2
                 and self.model.grid.is_cell_empty((seat_x, aisle_column))
                 and self.model.grid.is_cell_empty((seat_x + 1, aisle_column))
                 and self.model.grid.is_cell_empty((seat_x + 2, aisle_column))
                 and not self.model.frozen_aisle_cells[seat_x]
                 and not self.model.frozen_aisle_cells[seat_x + 1]
                 and not self.model.frozen_aisle_cells[seat_x + 1])
            ):
                shuffle_ordering = enumerate(
                    reversed(self.passengers_shuffling),
                    start=1
                )
                
                for x_offset, blocking_passenger in shuffle_ordering:
                    blocking_passenger.seated = False
                    blocking_passenger.assigned_seat.occupied = False
                    blocking_passenger.target_x += x_offset
                    blocking_passenger.target_y = aisle_column
                    blocking_passenger.seat_shuffle = True
                    blocking_passenger.shuffle_out_of_seat = True
                    blocking_passenger.shuffle_precedence = False
                    blocking_passenger.seat_steps_per_move = self.seat_steps_per_move
                    blocking_passenger.passengers_shuffling = []
                    blocking_passenger.passengers_shuffling.append(self)

                # Set Seat shuffle type                    
                if len(self.passengers_shuffling) == 2:
                    self.seat_shuffle_type = "D"
                if len(self.passengers_shuffling) == 1:
                    blocking_passenger = self.passengers_shuffling[0]
                    seat_col = blocking_passenger.assigned_seat.seat_column - 1
                    
                    if abs(seat_col - aisle_column) == 1:
                        self.seat_shuffle_type = "B"
                    else:
                         self.seat_shuffle_type = "C"
                
                self.seat_shuffle = True
                self.shuffle_precedence = True
                self.waiting_for_shuffling = True
                self.seat_shuffle_time = 1
                self.model.frozen_aisle_cells[self.pos[0] + 1] = True
            else:
                self.seat_shuffle_waiting_time += 1      
        # If at seat row
        elif self.pos[0] == seat_x:
            # If at seat column
            if self.at_target():
                self.seated = True
                self.assigned_seat.occupied = True
                
                # If precedence in seat shuffle situation
                if self.seat_shuffle and self.shuffle_precedence:
                    if not self.all_passengers_shuffling_out_of_aisle():
                        self.seat_shuffle_time += 1
                    else:
                        # To stop counting seat shuffle time
                        self.seat_shuffle = False
                        for passenger in self.passengers_shuffling:
                            passenger.seat_shuffle = False
                
                return
                
            # If waiting to store luggage
            if self.luggage_time > 0:
                self.luggage_time -= 1
                return
            
            # If waiting for seat reaction time
            if self.seat_reaction_time > 0:
                self.seat_reaction_time -= 1
                return
            
            if self.pos[1] == aisle_column:
                self.seat_shuffle_time += 1
                
            self.move_to_target()
        # Not at seat row
        else:
            self.move_to_target()
            
    def at_target(self) -> bool:
        """Check if the passenger is at the target position."""
        return self.pos == (self.target_x, self.target_y)
    
    def move_to_target(self):
        """Move to target. Movement is prioritized in x direction when in the
        aisle and in y direction when in the assigned seat row. Checks if the
        move is possible (cell is empty and not frozen).
        """
        aisle_column = self.model.airplane.aisle_column
        
        x_dir = 0
        # If not at row, calculate x direction
        if self.pos[0] != self.target_x:
            x_dir = 1 if self.target_x > self.pos[0] else -1
        y_dir = 0
        # If not at column, calculate y direction
        if self.pos[1] != self.target_y:
            y_dir = 1 if self.target_y > self.pos[1] else -1             
        
        target = None
        if x_dir != 0 and y_dir != 0:
            # If in aisle, move to row first
            if self.pos[1] == aisle_column:
                y_dir = 0
            # If in target row, move to column first
            else:
                x_dir = 0
        
        target = (self.pos[0] + x_dir, self.pos[1] + y_dir)
        
        # If moving in the aisle and next cell is frozen
        if (
            x_dir != 0
            and y_dir == 0
            and not self.shuffle_into_seat
            and self.model.frozen_aisle_cells[self.pos[0] + 1]
        ):   
            self.last_move += 1
            return
        
        # If not in seat shuffle situation
        if not (self.shuffle_into_seat
                or self.shuffle_out_of_seat
                or self.waiting_for_shuffling):
            self.last_move += 1
            
        if not self.model.grid.is_cell_empty(target):
            return
        
        if (
            (self.shuffle_into_seat or self.shuffle_out_of_seat)
            and not self.waiting_for_shuffling
        ):
            self.last_move += 1
        
        seat_x = self.assigned_seat.grid_coordinate[0]
        # If not in the aisle or in the aisle and moving into the seat row,
        # movement is a seat movement, otherwise it is an aisle movement
        if self.pos[1] != aisle_column or (self.pos[0] == seat_x == self.target_x):
            if self.last_move >= self.seat_steps_per_move:
                self.model.grid.move_agent(self, target)
                self.last_move = 0
        else:
            if self.last_move >= self.aisle_steps_per_move:
                self.model.grid.move_agent(self, target)
                self.last_move = 0
        
    def all_passengers_shuffling_out_of_aisle(self) -> bool:
        aisle_column = self.model.airplane.aisle_column
        return all(passenger.pos[1] != aisle_column for passenger in self.passengers_shuffling)
    
    def all_passengers_shuffling_in_aisle(self) -> bool:
        aisle_column = self.model.airplane.aisle_column
        return all(passenger.pos[1] == aisle_column for passenger in self.passengers_shuffling)
            
    def get_blocking_passengers(self) -> list[Passenger]:
        """Return a list of passengers blocking the row.
        
        Returns:
            A list of passengers blocking the row. Empty if no blocking
            passengers.
        """
        seat_x, seat_y = self.assigned_seat.grid_coordinate
        aisle_column = self.model.airplane.aisle_column
        
        y_dir = 1 if seat_y > aisle_column else -1
        
        blocking_y_coords = range(
            aisle_column + y_dir,
            seat_y,
            y_dir
        )
        blocking_positions = [(seat_x, y) for y in blocking_y_coords]
            
        return self.model.grid.get_cell_list_contents(blocking_positions)