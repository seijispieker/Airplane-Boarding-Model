import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    results_df = pd.read_csv("results/batch_run_results.csv")

    plot_occupancy_boarding_time(results_df)

    
def plot_occupancy_boarding_time(results_df: pd.DataFrame):
    """
    Plots the boarding time versus the passenger occupancy of the plane, 
    running an amount of simulations for each occupancy level.
    """
    grouped = results_df.groupby("occupancy")["Time (s)"].mean()

    passenger_counts = grouped.index * 174
    boarding_times = grouped.values / 60

    #Plot Boarding Time vs Occupancy
    plt.figure(figsize=(8, 6))
    plt.scatter(
        results_df["occupancy"] * 174,
        results_df["Time (s)"] / 60,
        color="black",
        alpha=0.5,
        label="Simulation Data",
        s=10,
    )

    plt.plot(passenger_counts, boarding_times, color="black", label="Mean Boarding Time")
    trend = np.polyfit(results_df["occupancy"] * 174, results_df["Time (s)"] / 60, 1)
    trendline = np.polyval(trend,passenger_counts)

    plt.plot(passenger_counts, trendline, linestyle="--", color="black", label="Trend Line")

    plt.title("Boarding Time vs Passenger Occupancy")
    plt.xlabel("Passengers")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.legend()
    plt.show()

def plot_interarrival_distribution(results_df: pd.DataFrame):
    """
    Plots the histogram of the generated inter-arrival times and the theoretical exponential PDF, 
    with the amount of passengers on the y-axis.
    """
    if "Inter_arrival_times" not in results_df.columns:
        print("Inter-arrival times not found in results.")
        return
    
    inter_arrival_times = []
    for times in results_df["Inter_arrival_times"]:
        try:
            inter_arrival_times.extend(eval(times))
        except:
            print("Error parsing inter-arrival times: {times}")
            continue

    inter_arrival_times = np.array(inter_arrival_times)

    mean_rate = inter_arrival_times.mean()
    bins = np.arange(0, max(inter_arrival_times) + 5, 5)
    bin_width = bins[1] - bins[0]

    counts, edges, _ = plt.hist(
        inter_arrival_times,
        bins=bins,
        alpha=0.7,
        label="Simulation Data",
        color="blue",
    )
    bin_centers = (edges[:-1] + edges[1:]) / 2

    y = len(inter_arrival_times) * bin_width * (1 / mean_rate) * np.exp(-bin_centers / mean_rate)

    plt.figure(figsize=(8, 6))
    plt.plot(bin_centers, y, 'k-', label="Exponential Distribution", linewidth=2)

    plt.title("Inter-Arrival Time Distribution")
    plt.xlabel("Arrival Time Intervals (s)")
    plt.ylabel("Amount of Passengers")
    plt.legend()
    plt.grid(True, linestyle=":")
    plt.show()


if __name__ == "__main__":
    main()


