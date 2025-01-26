import unittest

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger

class SeatsBackToFrontTestCase(unittest.TestCase):
    def setUp(self):
        self.model = BoardingModel(seat_assignment_method="back_to_front")
        
    def test_number_of_assigned_seats(self):
        all_seats = self.model.airplane.seats_list()
        assigned_seats = [seat for seat in all_seats if type(seat.assigned_passenger) is Passenger]
        self.assertEqual(len(self.model.passengers), len(assigned_seats))


class SeatsRandomTestCase(unittest.TestCase):
    def setUp(self):
        self.model = BoardingModel(seat_assignment_method="random")
        
    def test_number_of_assigned_seats(self):
        all_seats = self.model.airplane.seats_list()
        assigned_seats = [seat for seat in all_seats if type(seat.assigned_passenger) is Passenger]
        self.assertEqual(len(self.model.passengers), len(assigned_seats))
        
        
class SeatsSegmentedRandomTestCase(unittest.TestCase):
    def setUp(self):
        self.model = BoardingModel(seat_assignment_method="segmented_random")
        
    def test_number_of_assigned_seats(self):
        all_seats = self.model.airplane.seats_list()
        assigned_seats = [seat for seat in all_seats if type(seat.assigned_passenger) is Passenger]
        self.assertEqual(len(self.model.passengers), len(assigned_seats))
        

class SeatsOutSideInTestCase(unittest.TestCase):
    def setUp(self):
        self.model = BoardingModel(seat_assignment_method="outside_in")
        
    def test_number_of_assigned_seats(self):
        all_seats = self.model.airplane.seats_list()
        assigned_seats = [seat for seat in all_seats if type(seat.assigned_passenger) is Passenger]
        self.assertEqual(len(self.model.passengers), len(assigned_seats))
        
        
class SeatsSteffenPerfectTestCase(unittest.TestCase):
    def setUp(self):
        self.model = BoardingModel(seat_assignment_method="outside_in")
        
    def test_number_of_assigned_seats(self):
        all_seats = self.model.airplane.seats_list()
        assigned_seats = [seat for seat in all_seats if type(seat.assigned_passenger) is Passenger]
        self.assertEqual(len(self.model.passengers), len(assigned_seats))
        

if __name__ == '__main__':
    unittest.main()