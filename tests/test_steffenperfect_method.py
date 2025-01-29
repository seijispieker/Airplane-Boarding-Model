import unittest

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger


class SteffenPerfectTestCase(unittest.TestCase):
    """Base class for boarding method tests."""
    seat_assignment_method = "steffen_perfect"
        
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

    #Seat type function 
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
        """Validate Steffen Perfect boarding sequence."""

        seated_passengers = [
            agent
            for pos in self.model.grid.coord_iter()
            for agent in self.model.grid.get_cell_list_contents([pos[1]])
            if isinstance(agent, Passenger) and agent.seated
        ]

        # print("\nSeating Order (By Time Seated):")
        sorted_seated_passengers = sorted(seated_passengers, key=lambda p: p.arrival_time)

        # for passenger in sorted_seated_passengers:
        #     seat_coords = passenger.assigned_seat.grid_coordinate
        #     print(
        #         f"Passenger {passenger.unique_id} seated at {seat_coords} "
        #         f"(Row {seat_coords[0]}, Column {seat_coords[1]}) "
        #         f"at time {passenger.arrival_time} ({self.get_seat_type(seat_coords[1])} seat)"
        #     )

        # Groups by row for Steffen Perfect validation
        seated_passengers_by_row = {}
        for passenger in sorted_seated_passengers:
            row = passenger.assigned_seat.grid_coordinate[0]
            if row not in seated_passengers_by_row:
                seated_passengers_by_row[row] = []
            seated_passengers_by_row[row].append(passenger)

        # Validates row-by-row seating order
        # print("\nRow-by-Row Seating (Steffen Perfect Validation):")
        # for row, passengers in sorted(seated_passengers_by_row.items(), reverse=True):
        #     print(
        #         f"Row {row}: {[(p.assigned_seat.grid_coordinate, p.arrival_time, self.get_seat_type(p.assigned_seat.grid_coordinate[1])) for p in passengers]}"
        #     )

        # Validate window passengers board first in each row
        for row, passengers in seated_passengers_by_row.items():
            earliest_window_time = None
            for passenger in passengers:
                seat_type = self.get_seat_type(passenger.assigned_seat.grid_coordinate[1])
                if seat_type == "window":
                    if earliest_window_time is None:
                        earliest_window_time = passenger.arrival_time
                    else:
                        self.assertGreaterEqual(
                            passenger.arrival_time,
                            earliest_window_time,
                            f"Window passenger {passenger.unique_id} in Row {row} boarded out of order."
                        )
                elif seat_type in ["middle", "aisle"]:
                    if earliest_window_time is not None:
                        self.assertLessEqual(
                            earliest_window_time,
                            passenger.arrival_time,
                            f"Middle/Aisle passenger {passenger.unique_id} boarded before a window passenger in Row {row}."
                        )
                        

if __name__ == "__main__":
    unittest.main()