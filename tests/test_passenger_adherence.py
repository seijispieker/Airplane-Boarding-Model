import unittest

from airplane_boarding_model.boarding_model import BoardingModel


class PassengerAdherenceTestCase(unittest.TestCase):
    def setUp(self):
        self.model_high_adherence = BoardingModel(seed=42, seat_assignment_method="back_to_front", conformance=100)
        self.model_low_adherence = BoardingModel(seed=42, seat_assignment_method="back_to_front", conformance=50)

    def test_high_adherence(self):
        method_seats = self.model_high_adherence.seats_back_to_front()
        adherence_seats = self.model_high_adherence.passenger_adherence(method_seats.copy())

        self.assertEqual(method_seats, adherence_seats)

    def test_low_adherence(self):
        method_seats = self.model_low_adherence.seats_back_to_front()
        adherence_seats = self.model_low_adherence.passenger_adherence(method_seats.copy())

        self.assertNotEqual(method_seats, adherence_seats)
        self.assertCountEqual(method_seats, adherence_seats) # order doesn't matter


if __name__ == '__main__':
    unittest.main()

    