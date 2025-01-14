"""A module for modeling an airplane and its seats."""

from .passenger import Passenger


class Seat:
    """A seat in an Airplane object.
    
    Attributes:
        row: The row of the seat starting from index 0.
        column: The column of the seat starting from index 0.
        assigned_passenger: Passenger object assigned to the seat.
        occupied: Whether the seat is occupied.
    """
    
    def __init__(self, row, column, assigned_passenger: Passenger=None):
        """Create a new seat with the given row and column.
        
        Args:
            row: The row of the seat.
            column: The column of the seat.
            assigned_passenger: Passenger object assigned to the seat.
        """
        self.row = row
        self.column = column
        self.assigned_passenger = assigned_passenger
        self.occupied = False
        
    def __str__(self):
        return f"{self.row + 1}{chr(self.column + 65)}"

    def __repr__(self):
        return f"{self.row + 1}{chr(self.column + 65)}"


class Airplane:
    """An airplane object with a layout containing seats.
    
    Attributes:
        rows: The number of rows in the airplane.
        columns: The number of columns per row including aisle.
        aisle_column: The column number of the aisle.
        layout: The layout of the airplane containing Seat objects or None if 
            aisle.
    """
    
    def __init__(self, rows=30, columns=7, aisle_column=3):
        """Create a new airplane with the given parameters.
        
        Args:
            rows: The number of rows in the airplane.
            columns: The number of columns per row including aisle.
            aisle_column: The column number of the aisle.
        """
        self.rows = rows
        self.columns = columns
        self.aisle_column = aisle_column
        self.layout = self.create_layout()

    def create_layout(self):
        """Create the layout of the airplane."""
        layout = []
        
        for row in range(self.rows):
            row_layout = []
            
            for column in range(self.columns):
                if column == self.aisle_column:
                    # Append Aisle
                    row_layout.append(None)
                else:
                    # Append Seat with corresponding row and column number
                    row_layout.append(Seat(row, column))
            
            layout.append(row_layout)
            
        return layout
    
    def assign_passengers(self, seats, passengers):
        """Assign passengers to seats.
        
        Args:
            seats: A list of Seat objects in order of assignment.
            passengers: A list of Passenger objects in order of assignment.
        """
        for seat, passenger in zip(seats, passengers):
            seat.assigned_passenger = passenger
            passenger.assigned_seat = seat
    
    def __str__(self):
        for row in self.layout:
            print(" | ".join(str(seat) if seat is not None else " " for seat in row))

    def __repr__(self):
        for row in self.layout:
            print(" | ".join(str(seat) if seat is not None else " " for seat in row))