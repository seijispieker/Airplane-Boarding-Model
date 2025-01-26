import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from airplane_boarding_model.boarding_model import BoardingModel


def main():
    results_df = pd.read_csv("results/batch_run_results.csv")
    plot_occupancy_boarding_time(results_df)
    plot_interarrival_distribution()


def simulate_boarding_time(passenger_count, runs=1, steps_per_second=2, adherence=85):
    """
    Simulates the boarding process and calculatess the average boarding time.

    Args:
        passenger_count: The number of passengers boarding the plane.
        runs: The number of simulation runs to average results.
        steps_per_second: The number of steps per second.
        adherence: The percentage of passengers adhering to the boarding method.

    Returns:
        A list of average boarding times for the simulation runs.
    """
    times = []

    for _ in range(runs):
        model = BoardingModel(
            seed=42,
            steps_per_second=steps_per_second,
            aisle_speed=0.8,
            occupancy=passenger_count / 180,
            seat_assignment_method="back_to_front",
            conformance=adherence
        )
        while model.running:
            model.step()
        
        # Collect boarding time
        time_s = model.datacollector.get_model_vars_dataframe()["Time (s)"].iloc[-1]
        times.append(time_s / 60) 

    return times
    
def plot_occupancy_boarding_time(results_df: pd.DataFrame):
    """
    Plots the boarding time versus the passenger occupancy of the plane, 
    running an amount of simulations for each occupancy level.
    """ 
    passenger_counts = range(29, 181, 1)
    all_times = []
    average_times = []

    for count in passenger_counts:
        print(f"Starting simulation for passenger count {count}")
        boarding_times = simulate_boarding_time(count, runs=1, adherence=85)      # 1 run per passenger count

        all_times.extend([(count, time) for time in boarding_times])
        average_times.append((count, sum(boarding_times) / len(boarding_times)))

        print(f"Completed boarding simulation for passenger count {count}. Time: {boarding_times}")

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

def plot_interarrival_distribution():
    """
    Generates inter-arrival times for passengers and compares them to an exponential distribution.
    """
    model = BoardingModel(
        seed=42,
        steps_per_second=2,
        aisle_speed=0.8,
        occupancy=0.85,
        seat_assignment_method="back_to_front",
        conformance=100
    )

    inter_arrival_times = [
        passenger.arrival_time - prev_passenger.arrival_time
        for prev_passenger, passenger in zip(model.passengers[:-1], model.passengers[1:])
    ]
    
    # Compute lambda for exponential distribution
    mean_rate = 1 / np.mean(inter_arrival_times)

    # Plot histogram of observed inter-arrival times
    bins = np.arange(0, max(inter_arrival_times) + 1, 1)
    bin_width = bins[1] - bins[0]

    counts, edges, _ = plt.hist(
        inter_arrival_times,
        bins=bins,
        alpha=0.7,
        label='Observed Inter-arrival Times',
        color='blue',
        density=False,
    )
    bin_centers = (edges[:-1] + edges[1:]) / 2

    # Plot theoretical exponential distribution
    y = len(inter_arrival_times) * bin_width * mean_rate * np.exp(-mean_rate * bin_centers)
    plt.plot(bin_centers, y, label='Exponential Distribution', linewidth=2, color='black')

    plt.xlabel('Inter-arrival Time (steps)')
    plt.ylabel('Number of Passengers')
    plt.title('Inter-arrival Time Distribution')
    plt.legend()
    plt.grid(True)
    plt.show()



if __name__ == "__main__":
    main()


