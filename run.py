from airplane_boarding_model.boarding_model import BoardingModel


# Define parameters
parameters = {
    'rows': 30,
    'columns': 7,
    'aisle_column': 3,
    'passenger_count': 180,
    'steps': 200,
    'boarding_rate': 2,
}

model = BoardingModel(parameters)
model.run()
