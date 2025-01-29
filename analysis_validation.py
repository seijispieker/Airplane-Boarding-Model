import matplotlib.pyplot as plt
import glob
import numpy as np
import pandas as pd
from scipy.stats import linregress

from analysis_temp import plot_graph_trend
from analysis_temp import check_model

def main():
    boarding_times_files = glob.glob("results/validation/boarding_times_*.csv")
    boarding_times_df = pd.concat(
        [pd.read_csv(file) for file in boarding_times_files], ignore_index=True
        )
    compare_df = pd.read_csv("comparison_data/scatter_soure.csv")

    slope = check_model(boarding_times_df, compare_df, n_iterations=1000)
    plot_number_of_passengers_boarding_time(boarding_times_df, compare_df)
    plt.title(f"Boarding Time vs Passenger Occupancy \n{slope}")
    plt.show()
    
def plot_number_of_passengers_boarding_time(boarding_times_df: pd.DataFrame, compare_df):
    """
    Plots the boarding time versus the passenger occupancy of the plane, 
    running an amount of simulations for each occupancy level.
    """

    #Field Comparison
    real_data_df = compare_df

    plt.figure(figsize=(8, 6))
    #Plot Real Data
    plt.scatter(
        real_data_df["people"],
        real_data_df["boarding time"],
        color="green",
        alpha=0.8,
        label="Field Data",
        s=10,
    )
    #Plot Boarding Time vs Occupancy
    plt.scatter(
        boarding_times_df["number_of_passengers"],
        boarding_times_df["Time (s)"] / 60,
        color="purple",
        alpha=0.060,
        label="Simulation Data",
        s=10,
    )

    plot_graph_trend(compare_df, "people", "boarding time", label=" Field Trials Trend line")

    boarding_times_df["Time"] = boarding_times_df["Time (s)"] /60
    plot_graph_trend(boarding_times_df, "number_of_passengers", "Time", label="Experiment Trend line")

    
    plt.xlabel("Passengers")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.legend()
    

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

def plot_shuffle_time_comparison(seat_shuffle_times_df: pd.DataFrame, real_data_path: str):
    """
    Plots a boxplot of seat shuffle times categorized by shuffle type (A, B, C, D).
    Moves the count and percentage data to the legend instead of the graph itself.
    """
    real_data_df = pd.read_csv(real_data_path)

    # Map seat shuffle numbers to shuffle types
    shuffle_type_mapping = {1: "A", 4: "B", 5: "C", 9: "D"}
    real_data_df["Shuffle Type"] = real_data_df["seat_shuffles"].map(shuffle_type_mapping)
    shuffle_types = ["A", "B", "C", "D"]

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    x_positions = range(1, len(shuffle_types) + 1)

    total_cases = len(seat_shuffle_times_df)

    type_counts = seat_shuffle_times_df["Seat shuffle type (A/B/C/D)"].value_counts()

    # Waiting time > 0
    nonzero_counts = seat_shuffle_times_df[seat_shuffle_times_df["Seat shuffle time (s)"] > 0] \
        .groupby("Seat shuffle type (A/B/C/D)")["Seat shuffle time (s)"].count()

    legend_entries = ["Counts & Percentages:"]

    # Plot simulated data boxplots
    for i, shuffle_type in enumerate(shuffle_types, start=1):
        simulated_data = seat_shuffle_times_df.loc[
            seat_shuffle_times_df["Seat shuffle type (A/B/C/D)"] == shuffle_type,
            "Seat shuffle time (s)"
        ]
        plt.boxplot(
            simulated_data,
            positions=[i - bar_width / 2],
            widths=0.3,
            notch=True,
            patch_artist=True,
            boxprops=dict(facecolor="lightblue", color="blue"),
            medianprops=dict(color="blue"),
            flierprops=dict(markerfacecolor="blue", markeredgecolor="blue", markersize=5),
        )

    # Plot field data boxplots
    for i, shuffle_type in enumerate(shuffle_types, start=1):
        if shuffle_type in real_data_df["Shuffle Type"].values:
            row = real_data_df[real_data_df["Shuffle Type"] == shuffle_type].iloc[0]
            field_data = [row["field 50% lower"], row["field 50% upper"]]
            plt.boxplot(
                field_data,
                positions=[i + bar_width / 2],
                widths=0.3,
                notch=True,
                patch_artist=True,
                boxprops=dict(facecolor="red", color="darkred"),
                medianprops=dict(color="darkred"),
                flierprops=dict(markerfacecolor="darkred", markeredgecolor="darkred", markersize=5),
            )

    for shuffle_type in shuffle_types:
        total = type_counts.get(shuffle_type, 0)
        nonzero = nonzero_counts.get(shuffle_type, 0)
        percentage = (nonzero / total_cases * 100) if total_cases > 0 else 0  
        legend_entries.append(f"{shuffle_type}: n={nonzero}, {percentage:.1f}%")

    plt.xticks(range(1, len(shuffle_types) + 1), shuffle_types)
    plt.title("Seat Shuffle Times by Type (Comparison)")
    plt.xlabel("Shuffle Type (A/B/C/D)")
    plt.ylabel("Time (s)")
    plt.legend(
        handles=[
            plt.Line2D([0], [0], color="blue", lw=2, label="Simulated Data"),
            plt.Line2D([0], [0], color="darkred", lw=2, label="Field Data"),
            plt.Line2D([0], [0], color="black", lw=0, label="\n".join(legend_entries))  
        ],
        loc="upper left",
        fontsize=9,
        framealpha=0.8,
    )
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.tight_layout()
    plt.show()


def plot_seat_shuffle_waiting_times(seat_shuffle_times_df: pd.DataFrame):
    """
    Plots a boxplot for seat shuffle waiting times categorized by shuffle type (B, C, D),
    excluding cases where waiting time is 0. The legend contains the amount and adjusted percentages.
    Also adds the total count and percentage of all seat shuffle cases > 0.
    """
    shuffle_types = ["B", "C", "D"]

    plt.figure(figsize=(10, 6))

    # Filter out A
    filtered_df = seat_shuffle_times_df[seat_shuffle_times_df["Seat shuffle type (A/B/C/D)"].isin(shuffle_types)]
    total_non_A_count = len(filtered_df)

    # Count cases where waiting time > 0 for each type
    waiting_counts = (
        filtered_df[filtered_df["Seat shuffle waiting time (s)"] > 0]
        .groupby("Seat shuffle type (A/B/C/D)")["Seat shuffle waiting time (s)"]
        .count()
    )

    legend_texts = []
    boxplot_data = []
    total_waiting_cases = 0 

    for shuffle_type in shuffle_types:
        waiting_data = filtered_df.loc[
            (filtered_df["Seat shuffle type (A/B/C/D)"] == shuffle_type) &
            (filtered_df["Seat shuffle waiting time (s)"] > 0),
            "Seat shuffle waiting time (s)"
        ]

        # Only for waiting time > 0
        boxplot_data.append(waiting_data.tolist())

        waiting_count = waiting_counts.get(shuffle_type, 0)
        total_waiting_cases += waiting_count  
        percentage = (waiting_count / total_non_A_count * 100) if total_non_A_count > 0 else 0

        legend_texts.append(f"{shuffle_type} > 0: n={waiting_count}, {percentage:.1f}%") 

    # Calculate total percentage
    total_percentage = (total_waiting_cases / total_non_A_count * 100) if total_non_A_count > 0 else 0

    legend_texts.append(f"Total > 0: n={total_waiting_cases}, {total_percentage:.1f}%")

    boxprops = dict(facecolor="lightblue", color="blue")
    medianprops = dict(color="blue", linewidth=2)
    flierprops = dict(marker="o", color="blue", markersize=5)

    plt.boxplot(boxplot_data, patch_artist=True, boxprops=boxprops, medianprops=medianprops, flierprops=flierprops)
    plt.xticks(range(1, len(shuffle_types) + 1), shuffle_types)
    plt.xlabel("Shuffle Type (B/C/D)")
    plt.ylabel("Waiting Time (s)")
    plt.title("Seat Shuffle Waiting Times by Type")

    plt.text(
        1.05, 0.95, "\n".join(legend_texts), transform=plt.gca().transAxes,
        fontsize=10, verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="black")
    )

    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.tight_layout()
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
    slopes_model = bootstrap_slopes(df1, "number_of_passengers", "Time (s)", y_multiplyer= 60, n_iterations= n_iterations)
    slopes_real = bootstrap_slopes(df2, "people", "boarding time", n_iterations= n_iterations)
    lower, upper = np.percentile(slopes_model, [2.5, 97.5])
    print(lower, upper)

    #checking range of bootstrapped slopes
    difference = slopes_model - slopes_real
    lower, upper = np.percentile(difference, [2.5, 97.5])

    #making print for graph
    if lower <= 0 <= upper:
        slope = f"slope of model is similar!, range: [{lower:.4f}, {upper:.4f}]"
    else:
        slope = f"slope of model is incorrect, range: [{lower:.4f}, {upper:.4f}]"
    return slope

if __name__ == "__main__":
    main()


