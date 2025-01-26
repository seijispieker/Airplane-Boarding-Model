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
    mean_boarding_times = grouped.values / 60 

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

    plt.plot(passenger_counts, mean_boarding_times, color="black", label="Mean Boarding Time")

    trend = np.polyfit(results_df["occupancy"] * 174, results_df["Time (s)"] / 60, 1)
    trendline = np.polyval(trend, passenger_counts)

    plt.plot(passenger_counts, trendline, linestyle="--", color="black", label="Trend Line")

    plt.title("Boarding Time vs Passenger Occupancy")
    plt.xlabel("Passengers")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()


