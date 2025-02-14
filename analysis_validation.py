import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress


def main():
    boarding_times_files = glob.glob("results/validation/boarding_times_*.csv")
    boarding_times_df = pd.concat(
        [pd.read_csv(file) for file in boarding_times_files], ignore_index=True
        )
    compare_df = pd.read_csv("comparison_data/scatter_soure.csv")

    slope = check_model(boarding_times_df, compare_df, n_iterations=1000)
    plot_number_of_passengers_boarding_time(boarding_times_df, compare_df)
    plt.title(f"Boarding Time vs Passenger Occupancy \n{slope}")
    
    seat_shuffle_time_files = glob.glob("results/validation/seat_shuffle_times_*.csv")
    seat_shuffle_times_df = pd.concat(
        [pd.read_csv(file) for file in seat_shuffle_time_files], ignore_index=True
    )

    plot_shuffle_time_comparison(seat_shuffle_times_df)
    plot_seat_shuffle_waiting_times(seat_shuffle_times_df)


def plot_number_of_passengers_boarding_time(boarding_times_df: pd.DataFrame, compare_df):
    """
    Plots the boarding time versus the passenger occupancy of the plane, 
    running an amount of simulations for each occupancy level.
    """

    #Field Comparison
    real_data_df = compare_df

    plt.figure(figsize=(16, 8))
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
        alpha=0.2,
        label="Simulation Data",
        s=10,
    )

    plot_graph_trend(compare_df, "people", "boarding time", label=" Field Trials Trend line", color="black")

    boarding_times_df["Time"] = boarding_times_df["Time (s)"] /60
    plot_graph_trend(boarding_times_df, "number_of_passengers", "Time", label="Simulation Trend line", color="blue")

    
    plt.xlabel("Passengers")
    plt.ylabel("Boarding Time (min)")
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.title("Boarding Time vs Number of Passengers")
    plt.legend()
    plt.savefig("results/validation/boarding_time_vs_passenger_occupancy.png")
    # plt.show()
    

def plot_shuffle_time_comparison(seat_shuffle_times_df: pd.DataFrame):
    """
    Compares seat shuffle times from our simulation with real-world field data and a model from a research paper.
    """
    real_data_df = pd.read_csv("comparison_data/seat_shuffle_data.csv")

    # Mapping seat shuffle numbers to types
    shuffle_type_mapping = {1: "A", 4: "B", 5: "C", 9: "D"}
    real_data_df["Shuffle Type"] = real_data_df["seat_shuffles"].map(shuffle_type_mapping)
    shuffle_types = ["A", "B", "C", "D"]

    plt.figure(figsize=(10, 6))

    # Compute totals for percentage calculation
    total_cases = len(seat_shuffle_times_df)

    # Cases where shuffle time > 0
    nonzero_counts = seat_shuffle_times_df[seat_shuffle_times_df["Seat shuffle time (s)"] > 0] \
        .groupby("Seat shuffle type (A/B/C/D)")["Seat shuffle time (s)"].count()

    legend_entries = ["Our Model:"]

    # Plot simulated data as boxplots
    for i, shuffle_type in enumerate(shuffle_types, start=1):
        simulated_data = seat_shuffle_times_df.loc[
            seat_shuffle_times_df["Seat shuffle type (A/B/C/D)"] == shuffle_type,
            "Seat shuffle time (s)"
        ]
        plt.boxplot(
            simulated_data,
            positions=[i - 0.2],
            widths=0.2,
            notch=True,
            patch_artist=True,
            boxprops=dict(facecolor="lightblue", color="blue"),
            medianprops=dict(color="blue"),
            flierprops=dict(markerfacecolor="blue", markeredgecolor="blue", markersize=5),
        )

    # Plot field data as boxplots
    for i, shuffle_type in enumerate(shuffle_types, start=1):
        if shuffle_type in real_data_df["Shuffle Type"].values:
            row = real_data_df[real_data_df["Shuffle Type"] == shuffle_type].iloc[0]
            field_data = [row["field 50% lower"], row["field 50% upper"]]
            plt.boxplot(
                field_data,
                positions=[i],
                widths=0.2,
                notch=True,
                patch_artist=True,
                boxprops=dict(facecolor="red", color="darkred"),
                medianprops=dict(color="darkred"),
                flierprops=dict(markerfacecolor="darkred", markeredgecolor="darkred", markersize=5),
            )

    # Plot model data from the paper as boxplots
    for i, shuffle_type in enumerate(shuffle_types, start=1):
        if shuffle_type in real_data_df["Shuffle Type"].values:
            row = real_data_df[real_data_df["Shuffle Type"] == shuffle_type].iloc[0]
            model_data = [row["model 50% lower"], row["model 50% upper"]]
            plt.boxplot(
                model_data,
                positions=[i + 0.2],
                widths=0.2,
                notch=True,
                patch_artist=True,
                boxprops=dict(facecolor="green", color="darkgreen"),
                medianprops=dict(color="darkgreen"),
                flierprops=dict(markerfacecolor="darkgreen", markeredgecolor="darkgreen", markersize=5),
            )

    for shuffle_type in shuffle_types:
        nonzero = nonzero_counts.get(shuffle_type, 0)
        percentage = (nonzero / total_cases * 100) if total_cases > 0 else 0  
        legend_entries.append(f"{shuffle_type}: n={nonzero}, {percentage:.1f}%")

    plt.xticks(range(1, len(shuffle_types) + 1), shuffle_types)
    plt.title("Seat Shuffle Time Comparison")
    plt.xlabel("Shuffle Type (A/B/C/D)")
    plt.ylabel("Time (s)")
    plt.legend(
        handles=[
            plt.Line2D([0], [0], color="blue", lw=2, label="Our Model"),
            plt.Line2D([0], [0], color="darkred", lw=2, label="Field Data"),
            plt.Line2D([0], [0], color="darkgreen", lw=2, label="Calibrated Stochastic Aircraft Model"),
            plt.Line2D([0], [0], color="black", lw=0, label="\n".join(legend_entries))  
        ],
        loc="upper left",
        fontsize=9,
        framealpha=0.8,
    )
    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.tight_layout()
    plt.savefig("results/validation/seat_shuffle_time_comparison.png")
    # plt.show()
    

def plot_seat_shuffle_waiting_times(seat_shuffle_times_df):
    """
    Loads all seat shuffle time data from 'results/validation' and
    plots a boxplot for seat shuffle waiting times categorized by shuffle type (B, C, D),
    excluding cases where waiting time is 0. The legend contains the count and adjusted percentages.
    """
    shuffle_types = ["B", "C", "D"]
    
    plt.figure(figsize=(10, 6))

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

        # Only include waiting times > 0
        boxplot_data.append(waiting_data.tolist())

        waiting_count = waiting_counts.get(shuffle_type, 0)
        total_waiting_cases += waiting_count  
        percentage = (waiting_count / total_non_A_count * 100) if total_non_A_count > 0 else 0

        legend_texts.append(f"{shuffle_type} > 0: n={waiting_count}, {percentage:.1f}% of all") 

    # Calculate total percentage
    total_percentage = (total_waiting_cases / total_non_A_count * 100) if total_non_A_count > 0 else 0
    legend_texts.append(f"Total > 0: n={total_waiting_cases}, {total_percentage:.1f}% of all")

    boxprops = dict(facecolor="lightblue", color="blue")
    medianprops = dict(color="blue", linewidth=2)
    flierprops = dict(marker="o", color="blue", markersize=5)

    plt.boxplot(boxplot_data, patch_artist=True, boxprops=boxprops, medianprops=medianprops, flierprops=flierprops)
    plt.xticks(range(1, len(shuffle_types) + 1), shuffle_types)
    plt.xlabel("Shuffle Type (B/C/D)")
    plt.ylabel("Waiting Time (s)")
    plt.title("Seat Shuffle Waiting Time > 0 by Type")

    plt.text(
        1.05, 0.95, "\n".join(legend_texts), transform=plt.gca().transAxes,
        fontsize=10, verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="black")
    )

    plt.grid(True, linestyle=":", linewidth=0.7)
    plt.tight_layout()
    # plt.show()
    plt.savefig("results/validation/seat_shuffle_waiting_times.png")


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
        slope = f"Model Slope Matches Real Data - Slope Range ange: [{lower:.4f}, {upper:.4f}]"
    else:
        slope = f"Model Slope Does Not Match Real Data - Slope Range: [{lower:.4f}, {upper:.4f}]"
    return slope


def plot_graph_trend(df, x, y, show_all = "yes", linestyle="-", color="green", label="Trend line", marker="x", linewidth=2):
    """
    add a plot of wanted columns of a dataframe.
    show_all = "yes" for scatterplot of all datapoints
    """
    grouped = df.groupby(x)[y].mean()
    passenger_counts = grouped.index
    
    #trendline model data
    trend = np.polyfit(df[x], df[y], 1)
    trendline = np.polyval(trend, passenger_counts)

    plt.plot(passenger_counts, trendline, linestyle=linestyle, color=color, label=label, linewidth=linewidth)


if __name__ == "__main__":
    main()
