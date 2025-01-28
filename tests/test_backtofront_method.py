import unittest
from abc import ABC

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger

class BoardingMethodTestBase(unittest.TestCase, ABC):
    """Base class for boarding method tests."""
    seat_assignment_method = None

    def setUp(self):
        """Set up the model for the specified boarding method."""

        # Define the parameters
        parameters = {
            "seed": 42,  # Set a default or iterate later if needed
            "steps_per_second": 2,
            "aisle_speed": 0.8,
            "number_of_passengers": 148,  # Default or choose from the range
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
    
    #Do it for all methods
    def test_simulation_completion(self):
        """Ensure all passengers are seated by the end of the simulation."""
        seated_passengers = [passenger for passenger in self.model.passengers if passenger.seated]
        self.assertEqual(len(self.model.passengers), len(seated_passengers))

    #Do it for all methods
    def test_number_of_assigned_seats(self):
        """Ensure all passengers have assigned seats."""
        seated_passengers = [
        agent
        for pos in self.model.grid.coord_iter()
        for agent in self.model.grid.get_cell_list_contents([pos[1]])  # pos[1] gives the coordinates
        if isinstance(agent, Passenger) and agent.seated
        ]

        # Get the assigned seats
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.occupied]

        # Debugging output
        # print(f"Assigned seats: {len(assigned_seats)}, Seated passengers: {len(seated_passengers)}")

        # Assert that the number of seated passengers matches the number of assigned seats
        self.assertEqual(len(seated_passengers), len(assigned_seats))

    #Do it for all methods
    def test_unique_seat_assignments(self):
        """Ensure no two passengers are assigned to the same seat."""
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.assigned_passenger is not None]
        assigned_passengers = [seat.assigned_passenger for seat in assigned_seats]
        self.assertEqual(len(set(assigned_passengers)), len(assigned_passengers))

    def test_random_boarding_completeness(self):
        """Fix"""
        # passengers = simulate_boarding(method="random")
        
        # # Check all passengers are seated
        # seated_passengers = [p.assigned_seat for p in passengers]
        # self.assertEqual(len(seated_passengers), len(set(seated_passengers)),
        #     "Duplicate seats detected. Two passengers assigned the same seat.")
        # self.assertEqual(len(seated_passengers), total_passenger_count,
        #     "Not all passengers are seated.")
    
    # Do it for the back to front, Outside in, Steffen Perfect, Segmented
    def test_boarding_sequence(self):

        """Ensure the boarding sequence generally follows the back-to-front method."""
        print(f"{self.seat_assignment_method}")

        # Retrieve seated passengers
        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]

        # Debug: Print seated passengers
        print("\nSeated Passengers:")
        for passenger in seated_passengers:
            print(f"Passenger {passenger.unique_id}: Assigned Seat = {passenger.assigned_seat}, Arrival Time = {passenger.arrival_time}")

        # Sort passengers by boarding time
        sorted_seated_passengers = sorted(
            seated_passengers,
            key=lambda p: p.arrival_time
        )

        # Log seating order and times
        print("\nSeating Order (By Time Seated):")
        for passenger in sorted_seated_passengers:
            print(
                f"Passenger {passenger.unique_id} seated at {passenger.assigned_seat} "
                f"(Row {passenger.assigned_seat.grid_coordinate[0]}) at time {passenger.arrival_time}"
            )

        # Group passengers by row (back-to-front)
        seated_passengers_by_row = {}
        for passenger in sorted_seated_passengers:
            # Extract row from the Seat object
            row = int(passenger.assigned_seat.grid_coordinate[0])
            if row not in seated_passengers_by_row:
                seated_passengers_by_row[row] = []
            seated_passengers_by_row[row].append(passenger)

        # Check the general back-to-front trend
        sorted_rows = sorted(seated_passengers_by_row.keys(), reverse=True)  # Back-to-front: higher rows first
        

        # Validate overall back-to-front trend
        print("\nRow-by-Row Seating (General Back-to-Front Trend):")
        previous_row_latest_time = float("-inf")  # Track the latest seating time in previous rows
        for row in sorted_rows:
            row_passengers = seated_passengers_by_row[row]
            row_seating_times = [p.arrival_time for p in row_passengers]

            # Print row-specific data
            print(
                f"Row {row}: {[(p.assigned_seat, p.arrival_time) for p in row_passengers]} "
            )

            # Allow overlap but ensure the general trend of back-to-front
            if min(row_seating_times) < previous_row_latest_time:
                print(f"\nWarning: Row {row} passengers boarded earlier than expected!")
            previous_row_latest_time = max(row_seating_times)

        # Assert a general trend, not strict order
        for i, passenger in enumerate(sorted_seated_passengers):
            if i > 0:
                prev_passenger = sorted_seated_passengers[i - 1]
                if (
                    prev_passenger.assigned_seat.grid_coordinate[0] < passenger.assigned_seat.grid_coordinate[0]
                    and prev_passenger.arrival_time > passenger.arrival_time
                ):
                    self.fail(
                        f"Passenger {prev_passenger.unique_id} (Row {prev_passenger.assigned_seat.grid_coordinate[0]}) seated after "
                        f"Passenger {passenger.unique_id} (Row {passenger.assigned_seat.grid_coordinate[0]}), violating the back-to-front trend."
                    )


# Subclasses for each boarding method
class SeatsBackToFrontTestCase(BoardingMethodTestBase):
    seat_assignment_method = "back_to_front"


# class SeatsRandomTestCase(BoardingMethodTestBase):
#     seat_assignment_method = "random"


# class SeatsSegmentedRandomTestCase(BoardingMethodTestBase):
#     seat_assignment_method = "segmented_random"


# class SeatsOutsideInTestCase(BoardingMethodTestBase):
#     seat_assignment_method = "outside_in"


# class SeatsSteffenPerfectTestCase(BoardingMethodTestBase):
#     seat_assignment_method = "steffen_perfect"


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)