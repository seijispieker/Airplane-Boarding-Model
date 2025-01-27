import unittest
from airplane_boarding_model.boarding_model import BoardingModel

class PassengerAdherenceTestCase(unittest.TestCase):
    def setUp(self):
        self.model_high_adherence = BoardingModel(seat_assignment_method="back_to_front", conformance=100)
        self.model_low_adherence = BoardingModel(seat_assignment_method="back_to_front", conformance=50)
        
    def test_high_adherence(self):
        method_seats = self.model_high_adherence.airplane.seats_back_to_front()
        assigned_seats = self.model_high_adherence.assigned_seats

        self.assertEqual(method_seats[:len(self.model_high_adherence.passengers)], assigned_seats)

    def test_low_adherence(self):
        method_seats = self.model_low_adherence.airplane.seats_back_to_front()
        assigned_seats = self.model_low_adherence.assigned_seats

        adherence_count = sum(
            [1 for i, seat in enumerate(assigned_seats) if seat == method_seats[i]]
        )

        self.assertGreaterEqual(adherence_count, len(self.model_low_adherence.passengers) * 0.5)

if __name__ == '__main__':
    unittest.main()

    