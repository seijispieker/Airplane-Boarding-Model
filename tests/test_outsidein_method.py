import unittest
from abc import ABC

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger


class BoardingMethodTestBase(unittest.TestCase, ABC):
    """Base class for boarding method tests."""
    seat_assignment_method = None

    @classmethod
    def setUpClass(cls):
        """Skip execution if this is the base class."""
        if cls is BoardingMethodTestBase:
            raise unittest.SkipTest("Skipping base test class")
        
    def setUp(self):
        """Set up the model for the specified boarding method."""
        parameters = {
            "seed": 42,
            "steps_per_second": 2,
            "aisle_speed": 0.8,
            "number_of_passengers": 148,
            "seat_assignment_method": self.seat_assignment_method,
            "conformance": 100,
        }
        if not self.seat_assignment_method:
            raise ValueError("seat_assignment_method is not set in the test subclass.")

        self.model = BoardingModel(
            seed=parameters["seed"],
            steps_per_second=parameters["steps_per_second"],
            aisle_speed=parameters["aisle_speed"],
            number_of_passengers=parameters["number_of_passengers"],
            seat_assignment_method=self.seat_assignment_method,
            conformance=parameters["conformance"],
        )

        self.model.running = True
        while self.model.running:
            self.model.step()

    def get_seat_type(self, column):
        """Determine seat type based on column index."""
        if column in [0, 6]:
            return "window"
        elif column in [1, 5]:
            return "middle"
        elif column in [2, 4]:
            return "aisle"
        else:
            raise ValueError(f"Invalid column index: {column}. Must be between 0 and 6.")

    # Common
    def test_simulation_completion(self):
        """Ensure all passengers are seated by the end of the simulation."""
        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]
        
        self.assertEqual(self.model.number_of_passengers, len(seated_passengers))

    # Common
    def test_number_of_assigned_seats(self):
        """Ensure all passengers have assigned seats."""
        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]

        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.occupied]
        self.assertEqual(len(seated_passengers), len(assigned_seats))

    # Common
    def test_unique_seat_assignments(self):
        """Ensure no two passengers are assigned to the same seat."""
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.assigned_passenger is not None]
        assigned_passengers = [seat.assigned_passenger for seat in assigned_seats]
        
        self.assertEqual(len(set(assigned_passengers)), len(assigned_passengers))

    # Tests the outside_in seat assignment
    def test_boarding_sequence(self):
        """Validate Outside-In boarding sequence."""

        # Retrieves seated passengers
        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]

        # Sorts passengers by seating time
        sorted_seated_passengers = sorted(seated_passengers, key=lambda p: p.arrival_time)

        # Logs seating order for debugging
        # print("\nSeating Order (By Time Seated):")
        # for passenger in sorted_seated_passengers:
        #     seat_coords = passenger.assigned_seat.grid_coordinate
        #     print(
        #         f"Passenger {passenger.unique_id} seated at {seat_coords} "
        #         f"(Row {seat_coords[0]}, Column {seat_coords[1]}) "
        #         f"at time {passenger.arrival_time} ({self.get_seat_type(seat_coords[1])} seat)"
        #     )

        # Groups passengers by row
        passengers_by_row = {}
        for passenger in sorted_seated_passengers:
            row = passenger.assigned_seat.grid_coordinate[0]
            if row not in passengers_by_row:
                passengers_by_row[row] = []
            passengers_by_row[row].append(passenger)

        # Validates Outside-In order for each row
        for row, passengers in passengers_by_row.items():
            # Sort passengers by seat type hierarchy: window → middle → aisle
            passengers_sorted_by_seat_type = sorted(
                passengers, key=lambda p: ["window", "middle", "aisle"].index(self.get_seat_type(p.assigned_seat.grid_coordinate[1]))
            )

            # Logs row data for debugging
            # print(f"\nRow {row}:")
            # for passenger in passengers_sorted_by_seat_type:
            #     seat_type = self.get_seat_type(passenger.assigned_seat.grid_coordinate[1])
            #     print(f"Passenger {passenger.unique_id}: {seat_type} seat, seated at time {passenger.arrival_time}")

            # Validates order within the row
            for i, passenger in enumerate(passengers_sorted_by_seat_type):
                if i > 0:
                    prev_passenger = passengers_sorted_by_seat_type[i - 1]
                    prev_seat_type = self.get_seat_type(prev_passenger.assigned_seat.grid_coordinate[1])
                    curr_seat_type = self.get_seat_type(passenger.assigned_seat.grid_coordinate[1])

                    # Convert seat types to an ordered index list for validation
                    prev_seat_index = ["window", "middle", "aisle"].index(prev_seat_type)
                    curr_seat_index = ["window", "middle", "aisle"].index(curr_seat_type)

                    # Assert that the current seat type is not placed before its expected hierarchy
                    self.assertLessEqual(
                        prev_seat_index,
                        curr_seat_index,
                        f"Passenger {passenger.unique_id} ({curr_seat_type}) seated before "
                        f"Passenger {prev_passenger.unique_id} ({prev_seat_type}) in Row {row}, "
                        f"violating the Outside-In method."
                    )


class TestSeatsOutsideIn(BoardingMethodTestBase):
    seat_assignment_method = "outside_in"


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)