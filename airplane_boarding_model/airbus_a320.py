"""A module for modeling an airplane and its seats."""

from __future__ import annotations
from typing import TYPE_CHECKING

from itertools import chain
import mesa.agent

if TYPE_CHECKING:
    import mesa
    from .passenger import Passenger


class Seat:
    """A class for modeling a seat in an airplane.
    
    Attributes:
        seat_row: The row number of the seat starting from 1.
        seat_column: The column number of the seat starting from 1.
        grid_coordinate: The grid coordinate of the seat.
        assigned_passenger: The Passenger assigned to the seat.
        occupied: True if the seat is occupied, False otherwise.
    """
    
    def __init__(self,
                 seat_row: int,
                 seat_column: int,
                 grid_coordinate: int,
                 assigned_passenger: Passenger=None
        ):
        """Initialize a Seat object."""
        self.seat_row = seat_row
        self.seat_column = seat_column
        self.grid_coordinate = grid_coordinate
        self.assigned_passenger = assigned_passenger
        self.occupied = assigned_passenger is not None
    
    def __str__(self) -> str:
        return f"{self.seat_row + 1}{chr(self.seat_column + 65)}"

    def __repr__(self) -> str:
        return f"{self.seat_row + 1}{chr(self.seat_column + 65)}"


class AirbusA320:
    """A class for modeling an Airbus A320-200 airplane.
    
    Attributes:
        seat_rows: The number of rows of seats.
        columns: The number of columns of seats including the aisle.
        number_of_seats: The total number of seats.
        entrance_length: The number of grid cells for the entrance.
        aisle_length: The number of grid cells for the aisle.
        aisle_column: The column index (starting from 0) of the aisle.
        grid_width: The width of the grid map.
        grid_height: The height of the grid map.
        seat_map: A 2D list (seat_rows x columns) of Seat objects and None
            representing the aisle.
        grid_map: A 2D list (entrance_length + aisle_length x columns) mapping
            the seats to their grid coordinates.
        entrance: The grid coordinate of the entrance.
    """
    
    def __init__(self):
        """Initialize an Airbus A320-200 airplane."""
        self.seat_rows = 29
        self.columns = 7
        self.number_of_seats = self.seat_rows * (self.columns - 1)
        self.entrance_length = 6
        self.aisle_length = 2 * self.seat_rows
        self.aisle_column = 3 # Middle column
        self.grid_width = 2 * self.entrance_length + self.aisle_length
        self.grid_height = self.columns
        self.seat_map, self.grid_map,  = self.create_seat_grid_map()
        self.entrance = (0, self.aisle_column)

    def create_seat_grid_map(self) -> tuple[list[list[Seat | None]], list[list[Seat | None]]]:
        """Create seat and grid maps for the airplane."""
        seat_map = []
        grid_map = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        
        for row_index in range(self.seat_rows):
            seat_row = []
            for column in range(self.columns):
                if column != self.aisle_column:
                    seat_coordinate = (self.entrance_length + row_index * 2, column)
                    seat = Seat(
                        seat_row=row_index + 1,
                        seat_column=column + 1,
                        grid_coordinate=seat_coordinate
                    )
                    grid_map[seat_coordinate[0]][seat_coordinate[1]] = seat
                    seat_row.append(seat)
                else:
                    seat_row.append(None)
            
            seat_map.append(seat_row)
                    
        return seat_map, grid_map
    
    def assign_passengers(
        self,
        seats: list[Seat],
        passengers: mesa.agent.AgentSet[Passenger]
    ):
        """Assign passengers to seats."""
        for seat, passenger in zip(seats, passengers):
            seat.assigned_passenger = passenger
            passenger.assigned_seat = seat
            passenger.target_x = seat.grid_coordinate[0]
            passenger.target_y = seat.grid_coordinate[1]
            
    def seats_list(self) -> list[Seat]:
        """Return a list of all seats in the airplane."""
        flat_iter = chain.from_iterable(self.seat_map)
        return [seat for seat in flat_iter if seat is not None]