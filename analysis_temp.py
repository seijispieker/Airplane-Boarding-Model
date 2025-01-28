import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
import seaborn as sns


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


def plot_graph_trend(df, x, y, show_all = "yes", linestyle="--", color="red", label="trend", marker="x"):
    """
    add a plot of wanted columns of a dataframe.
    show_all = "yes" for scatterplot of all datapoints
    """
    grouped = df.groupby(x)[y].mean()
    passenger_counts = grouped.index
    #trendline model data
    trend = np.polyfit(df[x], df[y], 1)
    trendline = np.polyval(trend, passenger_counts)

    #plt.plot(passenger_counts, trendline, linestyle=linestyle, color=color, label=label)
    sns.regplot(data=df, scatter=False, x=x, y=y, label= label, color=color)

    if show_all == "yes":
        plt.scatter(
            df[x],
            df[y],
            color=color,
            alpha=0.5,
            label=f"all data {label}",
            s=10,
            marker=marker
        )

boarding_times_df_btf = pd.read_csv("results/validation/boarding_times.csv")
boarding_times_df = pd.read_csv("results/experiment/results.csv")
boarding_times_df["Time (min)"] = boarding_times_df["Time (s)"] / 60
boarding_times_df_btf["Time (min)"] = boarding_times_df["Time (s)"] / 60


compare_df = pd.read_csv("comparison_data/scatter_soure.csv")
boarding_times_df_seg = boarding_times_df[boarding_times_df.seat_assignment_method == "segmented_random"]
boarding_times_df_rand = boarding_times_df[boarding_times_df.seat_assignment_method == "random"]
boarding_times_df_btf = boarding_times_df[boarding_times_df.seat_assignment_method == "back_to_front"]
boarding_times_df_btf = boarding_times_df_btf[boarding_times_df_btf.conformance == 100]

plt.figure(figsize=(8, 6))
plot_graph_trend(compare_df, "people", "boarding time", color= "black", label="field data")
plot_graph_trend(boarding_times_df_seg, "number_of_passengers", "Time (min)", color= "red", label="sim segmented", marker="p")
plot_graph_trend(boarding_times_df_rand, "number_of_passengers", "Time (min)", color= "green", label="sim random", marker="*")
plot_graph_trend(boarding_times_df_btf, "number_of_passengers", "Time (min)", color= "black", label="sim btf", marker="+")

slope = check_model(boarding_times_df_seg, compare_df, n_iterations=  100)
print(slope)
slope = check_model(boarding_times_df_rand, compare_df, n_iterations=  100)
print(slope)
plt.legend()
plt.show()

"""
#--- plotting graphs
grouped = df1.groupby("number_of_passengers")["Time (s)"].mean()
passenger_counts = grouped.index

#scatter model data
plt.figure(figsize=(8, 6))
plt.scatter(
    df1["number_of_passengers"],
    df1["Time (s)"] / 60,
    color="red",
    alpha=0.5,
    label="Simulation Data",
    s=10,
)

#trendline model data
trend = np.polyfit(df1["number_of_passengers"], df1["Time (s)"] / 60, 1)
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
"""