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
        luggage_time: The number of steps to store luggage.
        assigned_seat: The Seat assigned to the passenger.
        seated: True if the passenger is seated, False otherwise.
        last_move: The number of steps since the last move.
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
        # alpha and beta based on Schultz 2018:
        single_luggage_time = self.model.random.weibullvariate(alpha=16, beta=1.7)
        luggage_items = self.model.random.choices(
            population=[1, 2, 3],
            weights=[0.6, 0.3, 0.1],
            k=1
        )[0]
        self.luggage_time = round(luggage_items * single_luggage_time * model.steps_per_second)
        self.assigned_seat = assigned_seat
        self.seated = seated
        self.last_move = aisle_steps_per_move
        self.arrival_time = 0
        self.shuffle_out_of_seat = False
        self.shuffle_into_seat = False
        self.waiting_for_shuffling = False
        self.shuffle_precedence = False
        self.passengers_shuffling = []
        
        if assigned_seat is not None:
            self.target_x, self.target_y = assigned_seat.grid_coordinate
        else:
            self.target_x, self.target_y = (None, None)
        
    def step(self):
        """Advance the passenger by one step."""
        seat_x, seat_y = self.assigned_seat.grid_coordinate
        aisle_column = self.model.airplane.aisle_column
        
        self.last_move += 1
        
        if self.shuffle_out_of_seat:
            if self.at_target():
                self.shuffle_out_of_seat = False
                self.waiting_for_shuffling = True
                self.target_x, self.target_y = self.assigned_seat.grid_coordinate
            else:
                self.move_to_target()

        elif self.shuffle_into_seat:
            if self.at_target():
                self.shuffle_into_seat = False
                self.seated = True
                self.assigned_seat.occupied = True
                
                if self.all_passengers_shuffling_out_of_aisle():
                    self.model.frozen_aisle_cells[self.pos[0]] = False
            else:
                self.move_to_target()

        elif self.waiting_for_shuffling:
            if self.shuffle_precedence and self.all_passengers_shuffling_in_aisle():
                self.waiting_for_shuffling = False
                self.shuffle_into_seat = True
                self.move_to_target()
                
            elif not self.shuffle_precedence and self.all_passengers_shuffling_out_of_aisle():
                self.waiting_for_shuffling = False
                self.shuffle_into_seat = True
                self.move_to_target()

        #If at seat row - 1
        elif self.pos[0] == seat_x - 1 and self.get_blocking_passengers() != []:

            self.passengers_shuffling = self.get_blocking_passengers()

            # If waiting to store luggage
            if self.luggage_time > 0:
                self.luggage_time -= 1
                return

            for x_offset, passenger_shuffling in enumerate(reversed(self.passengers_shuffling), start=1):
                passenger_shuffling.seated = False
                passenger_shuffling.assigned_seat.occupied = False
                passenger_shuffling.target_x += x_offset
                passenger_shuffling.target_y = aisle_column
                passenger_shuffling.shuffle_out_of_seat = True
                passenger_shuffling.passengers_shuffling.append(self)
        
            self.shuffle_precedence = True
            self.waiting_for_shuffling = True
            self.model.frozen_aisle_cells[self.pos[0] + 1] = True
        
        # No seat shuffle situation
        # If at seat row
        elif self.pos[0] == seat_x:
            # If at seat column
            if self.at_target():
                self.seated = True
                self.assigned_seat.occupied = True
                return
                
            # If waiting to store luggage
            if self.luggage_time > 0:
                self.luggage_time -= 1
                return
            
            self.move_to_target()
        # Not at seat row and next aisle cell is free
        elif not self.model.frozen_aisle_cells[self.pos[0] + 1]:
            self.move_to_target()
            
    def at_target(self) -> bool:
        """Check if the passenger is at the target position."""
        return self.pos == (self.target_x, self.target_y)
    
    def move_to_target(self) -> bool:
        """Move to target. Movenment is prioritized in x direction when in the
        aisle and in y direction when in the assigned seat row.
        
        Returns:
            True if the passenger moved, False if move not possible.
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
                target = (self.pos[0] + x_dir, self.pos[1])
            # If in row, move to column first
            else:
                target = (self.pos[0], self.pos[1] + y_dir)
        else:
            target = (self.pos[0] + x_dir, self.pos[1] + y_dir)
        
        if self.model.grid.is_cell_empty(target) and self.last_move >= self.aisle_steps_per_move:
            self.model.grid.move_agent(self, target)
            self.last_move = 0
            return True
        else:
            return False
        
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
    
    #Removed
    def waiting_position(self) -> tuple[int, int]:
        _, seat_y = self.assigned_seat.grid_coordinate
        aisle_column = self.model.airplane.aisle_column
        y_dir = -1 if seat_y > aisle_column else 1
        
        target = (self.pos[0], self.pos[1] + y_dir)
        # If opposite side of aisle is free
        if self.model.grid.is_cell_empty(target):
            return target
        else:
            return (self.pos[0] - 1, self.pos[1])