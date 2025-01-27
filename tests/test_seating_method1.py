import unittest
from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger

class BoardingMethodTestBase(unittest.TestCase):
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

    def test_unique_seat_assignments(self):
        """Ensure no two passengers are assigned to the same seat."""
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.assigned_passenger is not None]
        assigned_passengers = [seat.assigned_passenger for seat in assigned_seats]
        self.assertEqual(len(set(assigned_passengers)), len(assigned_passengers))

    def test_simulation_completion(self):
        """Ensure all passengers are seated by the end of the simulation."""
        seated_passengers = [passenger for passenger in self.model.passengers if passenger.seated]
        self.assertEqual(len(self.model.passengers), len(seated_passengers))

    def test_boarding_sequence(self):
        """Ensure the boarding sequence matches the intended method."""
        # Define the expected order
        expected_order = self.model.assigned_seats

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

        sorted_seated_passengers = sorted(
            seated_passengers,
            key=lambda p: (p.arrival_time, str(p.assigned_seat))  # Tie-breaking by assigned_seat
        )
        # Debug: Print sorted seated passengers
        print("\nSorted Seated Passengers (By Arrival Time):")
        for passenger in sorted_seated_passengers:
            print(f"Passenger {passenger.unique_id}: Assigned Seat = {passenger.assigned_seat}, Arrival Time = {passenger.arrival_time}")

        # Extract the assigned seats of these seated passengers
        actual_order = [passenger.assigned_seat for passenger in sorted_seated_passengers]

        # Debug: Print expected and actual orders
        print("\nExpected Order (Assigned Seats):")
        print(expected_order)
        print("\nActual Order (Seated by Arrival Time):")
        print(actual_order)

        # Identify first mismatch
        for idx, (expected, actual) in enumerate(zip(expected_order, actual_order)):
            if expected != actual:
                print(f"Mismatch at index {idx}: Expected {expected}, Got {actual}")
                break

        # Assert that actual order matches expected order
        self.assertEqual(
            actual_order,
            expected_order,
            "The boarding process does not align with the assigned seat order based on arrival times."
        )


# Subclasses for each boarding method
class SeatsBackToFrontTestCase(BoardingMethodTestBase):
    seat_assignment_method = "back_to_front"


class SeatsRandomTestCase(BoardingMethodTestBase):
    seat_assignment_method = "random"


class SeatsSegmentedRandomTestCase(BoardingMethodTestBase):
    seat_assignment_method = "segmented_random"


class SeatsOutsideInTestCase(BoardingMethodTestBase):
    seat_assignment_method = "outside_in"


class SeatsSteffenPerfectTestCase(BoardingMethodTestBase):
    seat_assignment_method = "steffen_perfect"


if __name__ == "__main__":
    unittest.main()