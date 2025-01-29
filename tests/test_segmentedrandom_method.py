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
            seat_assignment_method=parameters["seat_assignment_method"],
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

    def test_simulation_completion(self):
        """Ensure all passengers are seated by the end of the simulation."""
        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]
        self.assertEqual(self.model.number_of_passengers, len(seated_passengers))

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

    def test_unique_seat_assignments(self):
        """Ensure no two passengers are assigned to the same seat."""
        assigned_seats = [seat for seat in self.model.airplane.seats_list() if seat.assigned_passenger is not None]
        assigned_passengers = [seat.assigned_passenger for seat in assigned_seats]
        self.assertEqual(len(set(assigned_passengers)), len(assigned_passengers))

    def test_boarding_sequence(self):
        """Validate Segmented Random boarding sequence."""
        print(f"{self.seat_assignment_method}")

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

        # Groups passengers into segments based on row ranges
        segment_ranges = [
            (62, 48),  # Back segment
            (47, 34),  # Middle-back segment
            (33, 20),  # Middle-front segment
            (19, 6),   # Front segment
        ]
        passengers_by_segment = {i: [] for i in range(len(segment_ranges))}

        for passenger in sorted_seated_passengers:
            row = passenger.assigned_seat.grid_coordinate[0]
            for i, (start_row, end_row) in enumerate(segment_ranges):
                if start_row >= row >= end_row:  # Adjusts for descending rows
                    passengers_by_segment[i].append(passenger)
                    break

        # Validates Segmented Random order within each segment
        for segment, passengers in passengers_by_segment.items():
            # print(f"\nSegment {segment} (Rows {segment_ranges[segment]}):")
            segment_passengers = sorted(
                passengers, key=lambda p: p.arrival_time
            )

            # # Logs segment data for debugging
            # for passenger in segment_passengers:
            #     seat_coords = passenger.assigned_seat.grid_coordinate
            #     print(
            #         f"Passenger {passenger.unique_id}: Row {seat_coords[0]}, "
            #         f"Column {seat_coords[1]}, Time {passenger.arrival_time} "
            #         f"({self.get_seat_type(seat_coords[1])} seat)"
            #     )

            # Checks for randomness within the segment
            previous_time = -1
            for passenger in segment_passengers:
                self.assertGreaterEqual(
                    passenger.arrival_time,
                    previous_time,
                    f"Passenger {passenger.unique_id} seated earlier than expected "
                    f"in Segment {segment} (Rows {segment_ranges[segment]})."
                )
                previous_time = passenger.arrival_time
                

class TestSeatsSegmentedRandom(BoardingMethodTestBase):
    seat_assignment_method = "segmented_random"

if __name__ == "__main__":
    unittest.main(verbosity=2)