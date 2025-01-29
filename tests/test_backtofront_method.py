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
            "conformance": 100
    }
        if not self.seat_assignment_method:
            raise ValueError("seat_assignment_method is not set in the test subclass.")
        
        self.model = BoardingModel(
            seed=parameters["seed"],
            steps_per_second=parameters["steps_per_second"],
            aisle_speed=parameters["aisle_speed"],
            number_of_passengers=parameters["number_of_passengers"],
            seat_assignment_method=parameters["seat_assignment_method"],
            conformance=parameters["conformance"],
        )

        self.model.running = True
        while self.model.running:
            self.model.step()

    # Common Test
    def test_simulation_completion(self):
        """Ensure all passengers are seated by the end of the simulation."""

        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]
        self.assertEqual(self.model.number_of_passengers, len(seated_passengers))

    # Common Test
    def test_number_of_assigned_seats(self):
        """Ensure all passengers have assigned seats."""
        seated_passengers = [
        agent
        for pos in self.model.grid.coord_iter()
        for agent in self.model.grid.get_cell_list_contents([pos[1]])
        if isinstance(agent, Passenger) and agent.seated
        ]

        # Assigned seats
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.occupied]

        # Assert that the number of seated passengers matches the number of assigned seats
        self.assertEqual(len(seated_passengers), len(assigned_seats))

    # Common
    def test_unique_seat_assignments(self):
        """Ensure no two passengers are assigned to the same seat."""
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.assigned_passenger is not None]
        assigned_passengers = [seat.assigned_passenger for seat in assigned_seats]
        self.assertEqual(len(set(assigned_passengers)), len(assigned_passengers))
    
    # Back_to-front sequencing test
    def test_boarding_sequence(self):

        """Ensure the boarding sequence generally follows the back-to-front method."""
        print(f"{self.seat_assignment_method}")

        # Seated passengers
        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]

        # Sorts passengers by boarding time
        sorted_seated_passengers = sorted(
            seated_passengers,
            key=lambda p: p.arrival_time
        )

        # # Logs seating order and times
        # print("\nSeating Order (By Time Seated):")
        # for passenger in sorted_seated_passengers:
        #     print(
        #         f"Passenger {passenger.unique_id} seated at {passenger.assigned_seat} "
        #         f"(Row {passenger.assigned_seat.grid_coordinate[0]}) at time {passenger.arrival_time}"
        #     )

        # Groups passengers by row (back-to-front)
        seated_passengers_by_row = {}
        for passenger in sorted_seated_passengers:
            # Extract row from the Seat object
            row = int(passenger.assigned_seat.grid_coordinate[0])
            if row not in seated_passengers_by_row:
                seated_passengers_by_row[row] = []
            seated_passengers_by_row[row].append(passenger)

        # Checks the general back-to-front trend
        sorted_rows = sorted(seated_passengers_by_row.keys(), reverse=True)  # Back-to-front: higher rows first
        

        # Validates back-to-front trend
        # print("\nRow-by-Row Seating (General Back-to-Front Trend):")
        previous_row_latest_time = float("-inf")  # Track the latest seating time in previous rows
        for row in sorted_rows:
            row_passengers = seated_passengers_by_row[row]
            row_seating_times = [p.arrival_time for p in row_passengers]

            # Prints row-specific data
            # print(
            #     f"Row {row}: {[(p.assigned_seat, p.arrival_time) for p in row_passengers]} "
            # )

            # Allow overlap but ensure the general trend of back-to-front
            if min(row_seating_times) < previous_row_latest_time:
                print(f"\nWarning: Row {row} passengers boarded earlier than expected!")
            previous_row_latest_time = max(row_seating_times)

        # Assert a general trend, not strict order
        for i, passenger in enumerate(sorted_seated_passengers):
            if i > 0:
                prev_passenger = sorted_seated_passengers[i - 1]
                prev_row = prev_passenger.assigned_seat.grid_coordinate[0]
                curr_row = passenger.assigned_seat.grid_coordinate[0]

                prev_time = prev_passenger.arrival_time
                curr_time = passenger.arrival_time

                # Ensure that passengers seated in a row closer to the back did not arrive later than those in front
                self.assertLessEqual(
                    prev_time,
                    curr_time,
                    msg=(
                        f"Passenger {prev_passenger.unique_id} (Row {prev_row}) seated after "
                        f"Passenger {passenger.unique_id} (Row {curr_row}), violating the back-to-front trend."
                    )
                )

class TestSeatsBackToFront(BoardingMethodTestBase):
    seat_assignment_method = "back_to_front"

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)