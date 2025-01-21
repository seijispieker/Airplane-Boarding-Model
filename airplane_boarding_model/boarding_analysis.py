import matplotlib.pyplot as plt
import numpy as np
from .boarding_model import BoardingModel

def simulate_boarding_time(passenger_count, runs=10, steps_per_second=1, adherence=100):
    """
    Simulates the boarding process and calculates the average boarding time.
    
    Args:
        passenger_count: Number of passengers on the plane.
        runs: Number of simulation runs to average results.
        steps_per_second: Number of steps per second in the simulation.
        
    Returns:
        The average boarding time (in minutes) over the simulation runs.
    """
    times = []  

    for run in range(runs):
        model = BoardingModel(
            rows=30,
            columns=7,
            aisle_column=3,
            passenger_count=passenger_count,
            boarding_rate_seconds=1,
            luggage_delay_seconds=2,
            steps_per_second=steps_per_second,
            seat_assignment_method="back_to_front",
            adherence=adherence,
        )
        time = 0

        while model.queue or any(not p.seated for p in model.grid.agents):
            model.step()
            time += 1

        times.append((time / steps_per_second) / 60)  # Convert to minutes

        return times 
    
def plot_boarding_time_vs_occupancy():
    """
    Plots the boarding time versus the passenger occupancy of the plane, 
    running an amount of simulations for each occupancy level.
    """
    passenger_counts = range(29, 181, 10)
    all_times = []
    average_times = []
    steps_per_second = 1 # Can be adjusted for faster or slower simulations

    for count in passenger_counts:
        #changed 
        boarding_times = simulate_boarding_time(count, runs=10, steps_per_second=steps_per_second, adherence=100)      # 10 runs per passenger count
        all_times.extend([(count, time) for time in boarding_times])
        average_times.append((count, sum(boarding_times) / len(boarding_times)))

    x, y = zip(*all_times)
    x_avg, y_avg = zip(*average_times)
    
    # Fit a linear trend line
    linear_fit = np.polyfit(x_avg, y_avg, 1)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, label="Simulation Data", color="black", alpha=0.7)
    plt.plot(x_avg, np.polyval(linear_fit, x_avg), label="Best Fit Line", color="black")
    
    plt.title("Boarding Time vs. Passenger Occupancy")
    plt.xlabel("Passenger Occupancy")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_boarding_time_vs_occupancy()
