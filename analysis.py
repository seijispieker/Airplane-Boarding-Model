import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress


def main():
    boarding_times_df = pd.read_csv("results/boarding_times.csv")
    seat_shuffle_times_df = pd.read_csv("results/seat_shuffle_times.csv")
    compare_df = pd.read_csv("comparison_data/scatter_soure.csv")

    plot_occupancy_boarding_time(boarding_times_df)
    plot_shuffle_time_boxplot(seat_shuffle_times_df)
    check_model(boarding_times_df, compare_df, n_iterations= 1000)

    
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

def check_model(df1, df2, n_iterations=10000):
    '''
    df1 = model data
    df2 = real boarding time data from literature 
    n_iterations = amount of bootstrap iterations 

    checks wether the model data and the literature data have the same slope and makes a graph of both dataframes 
    '''
    

    def bootstrap_slopes(df, x_name, y_name , x_multiplyer = 1,  y_multiplyer= 1, n_iterations=1000):
        slopes = []
        for _ in range(n_iterations):
            sample = df.sample(frac=1, replace=True)
            slope, _, _, _, _ = linregress(sample[x_name] * x_multiplyer, sample[y_name] / y_multiplyer)
            slopes.append(slope)
        return np.array(slopes)

    #bootstrapping slope
    slopes_model = bootstrap_slopes(df1, "occupancy", "Time (s)", x_multiplyer = 174,  y_multiplyer= 60, n_iterations= n_iterations )
    slopes_real = bootstrap_slopes(df2, "people", "boarding time", n_iterations= n_iterations)

    #checking range of bootstrapped slopes
    difference = slopes_model - slopes_real
    lower, upper = np.percentile(difference, [2.5, 97.5])

    #making print for graph
    if lower <= 0 <= upper:
        slope = "slope of model is similar!"
    else:
        slope = f"slope of model is incorrect, difference: [{lower:.4f}, {upper:.4f}]"
    
    
    #--- plotting graphs
    grouped = df1.groupby("occupancy")["Time (s)"].mean()
    passenger_counts = grouped.index * 174 

    #scatter model data
    plt.figure(figsize=(8, 6))
    plt.scatter(
        df1["occupancy"] * 174,
        df1["Time (s)"] / 60,
        color="red",
        alpha=0.5,
        label="Simulation Data",
        s=10,
    )

    #trendline model data
    trend = np.polyfit(df1["occupancy"] * 174, df1["Time (s)"] / 60, 1)
    trendline = np.polyval(trend, passenger_counts)
    plt.plot(passenger_counts, trendline, linestyle="--", color="red", label="Trend model")

    #scatter real data
    plt.scatter(
        df2["people"],
        df2["boarding time"] ,
        color="black",
        alpha=0.5,
        label="real data",
        s=10,
        marker="x",
    )
    
    #trendline real data
    trend = np.polyfit(df2["people"], df2["boarding time"] , 1)
    trendline = np.polyval(trend, df2["people"])
    plt.plot(df2["people"], trendline, linestyle="--", color="black", label="Trend real")

    #graph visuals
    plt.title(f"combined graph. \n{slope}")
    plt.xlabel("Passengers")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True, linestyle="--", linewidth=0.7)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()


