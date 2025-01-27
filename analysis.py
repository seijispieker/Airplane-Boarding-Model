import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    boarding_times_df = pd.read_csv("results/boarding_times.csv")
    seat_shuffle_times_df = pd.read_csv("results/seat_shuffle_times.csv")

    plot_occupancy_boarding_time(boarding_times_df)
    plot_shuffle_time_boxplot(seat_shuffle_times_df)

    
def plot_occupancy_boarding_time(boarding_times_df: pd.DataFrame):
    """
    Plots the boarding time versus the passenger occupancy of the plane, 
    running an amount of simulations for each occupancy level.
    """
    grouped = boarding_times_df.groupby("occupancy")["Time (s)"].mean()

    passenger_counts = grouped.index * 174 
    mean_boarding_times = grouped.values / 60 

    #Plot Boarding Time vs Occupancy
    plt.figure(figsize=(8, 6))
    plt.scatter(
        boarding_times_df["occupancy"] * 174,
        boarding_times_df["Time (s)"] / 60,
        color="black",
        alpha=0.5,
        label="Simulation Data",
        s=10,
    )

    plt.plot(passenger_counts, mean_boarding_times, color="black", label="Mean Boarding Time")

    trend = np.polyfit(boarding_times_df["occupancy"] * 174, boarding_times_df["Time (s)"] / 60, 1)
    trendline = np.polyval(trend, passenger_counts)

    plt.plot(passenger_counts, trendline, linestyle="--", color="black", label="Trend Line")

    plt.title("Boarding Time vs Passenger Occupancy")
    plt.xlabel("Passengers")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.legend()
    plt.show()

def plot_shuffle_time_boxplot(seat_shuffle_times_df: pd.DataFrame):
    """
    Plots a boxplot of seat shuffle times categorized by shuffle type (A, B, C, D).
    """
    # Ensure only unique rows are used to avoid duplicate entries
    unique_shuffle_df = seat_shuffle_times_df.drop_duplicates()

    # Create the boxplot
    plt.figure(figsize=(8, 6))
    unique_shuffle_df.boxplot(column="Seat shuffle time (s)", by="Seat shuffle type (A/B/C/D)", grid=False, notch=True)

    plt.title("Seat Shuffle Times by Type")
    plt.suptitle("")  # Remove default matplotlib boxplot title
    plt.xlabel("Shuffle Type (A/B/C/D)")
    plt.ylabel("Time (s)")
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.show()


if __name__ == "__main__":
    main()


