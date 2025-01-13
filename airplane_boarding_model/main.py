import agentpy as ap
from boarding_model import BoardingModel

# Define parameters
parameters = {
    'rows': 30,
    'seats_per_row': 7,
    'aisle_col': 3,
    'passenger_count': 180,
    'steps': 900,
    'boarding_rate': 2
}

# Run the model
model = BoardingModel(parameters)
results = model.run()

# Display airplane layout
print("\nAirplane Layout:")
model.airplane.display_layout()

# Display simulation results
print("\nSimulation Results:")
if 'Final boarded count' in results:
    print(f"Final boarded count: {results['Final boarded count']}")
if 'Total steps' in results:
    print(f"Total steps taken: {results['Total steps']}")
if 'Final boarding percentage' in results:
    print(f"Final boarding percentage: {results['Final boarding percentage']:.2f}%")

# Optional: Display detailed boarding data
if 'boarded' in model.data:
    print(f"Boarded passengers over time: {model.data['boarded']}")
if 'aisle_congestion' in model.data:
    print(f"Aisle congestion over time: {model.data['aisle_congestion']}")