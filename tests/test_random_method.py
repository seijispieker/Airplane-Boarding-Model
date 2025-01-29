import unittest
from scipy.stats import chisquare 
import numpy

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger


class RandomTestCase(unittest.TestCase):
    """Base class for boarding method tests."""
    seat_assignment_method = "random"
        
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

    #  Common
    def test_number_of_assigned_seats(self):
        """Ensure all passengers have assigned seats."""

        seated_passengers = [
        agent
        for pos in self.model.grid.coord_iter()
        for agent in self.model.grid.get_cell_list_contents([pos[1]])
        if isinstance(agent, Passenger) and agent.seated
        ]

        # Gets the assigned seats
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.occupied]

        self.assertEqual(len(seated_passengers), len(assigned_seats))

    def test_unique_seat_assignments(self):
        """Ensure no two passengers are assigned to the same seat."""
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.assigned_passenger is not None]
        assigned_passengers = [seat.assigned_passenger for seat in assigned_seats]
        self.assertEqual(len(set(assigned_passengers)), len(assigned_passengers))

    def test_random_boarding_sequence(self):
        """Statistically test randomness of boarding sequence."""

        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]

        # # Debugging
        # print("\nSeated Passengers:")
        # for passenger in seated_passengers:
        #     print(f"Passenger {passenger.unique_id}: Assigned Seat = {passenger.assigned_seat}, Arrival Time = {passenger.arrival_time}")

        # Sorts passengers by boarding time
        sorted_seated_passengers = sorted(
            seated_passengers,
            key=lambda p: p.arrival_time
        )

        # Extracts boarding times
        boarding_times = [passenger.arrival_time for passenger in sorted_seated_passengers]
        max_time = max(boarding_times)
        
        # Bins the times into intervals to check uniformity
        num_bins = 10  # Divides into 10 intervals
        bin_edges = [i * (max_time / num_bins) for i in range(num_bins + 1)]
        counts, _ = numpy.histogram(boarding_times, bins=bin_edges)

        # Perform chi-squared goodness-of-fit test
        expected = [len(boarding_times) / num_bins] * num_bins  # Expects uniform distribution
        chi2_stat, p_value = chisquare(counts, expected)
        
        # Asserts p-value is high enough to not reject randomness
        self.assertGreater(
            p_value,
            0.05,
            f"Boarding sequence does not appear random (p = {p_value}). Chi2 = {chi2_stat}, Counts = {counts}"
        )


if __name__ == "__main__":
    unittest.main()