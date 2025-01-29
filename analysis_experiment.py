import pandas as pd
import matplotlib.pyplot as plt



def main():
    results_df = pd.read_csv("results/experiment/results.csv")
    print(plot_boarding_times_conformance())

def plot_boarding_times_conformance():
    # File mapping for specific strategies
    file_mapping = {
        "outside_in": "results/experiment/results_outside_in.csv",
        "segmented_random_3": "results/experiment/results_segmented_random_3.csv",
        "segmented_random_4": "results/experiment/results_segmented_random_4.csv",
        "steffen_perfect": "results/experiment/results_steffen_perfect.csv"
    }

    results_df = pd.read_csv("results/experiment/results.csv")

    for strategy, filepath in file_mapping.items():
        additional_df = pd.read_csv(filepath)
        results_df = pd.concat([results_df, additional_df], ignore_index=True)

    conformance_rates = results_df["conformance"]
    boarding_times = results_df["Time (s)"] / 60 
    strategies = results_df["seat_assignment_method"]

    strategy_data = {}

    # Group data by strategy and conformance
    for i, strategy in enumerate(strategies):
        if strategy not in strategy_data:
            strategy_data[strategy] = {}

        conf = conformance_rates.iloc[i]
        time = boarding_times.iloc[i]

        if conf not in strategy_data[strategy]:
            strategy_data[strategy][conf] = []

        strategy_data[strategy][conf].append(time)

    plt.figure(figsize=(10, 6))

    for strategy, conf_data in strategy_data.items():
        conf_list = sorted(conf_data.keys())  
        mean_times = [pd.Series(conf_data[conf]).mean() for conf in conf_list]
        std_times = [pd.Series(conf_data[conf]).std() for conf in conf_list]

        plt.plot(conf_list, mean_times, label=strategy, linewidth=2)

        # ±1 std deviation
        plt.fill_between(conf_list, 
                         [m - s for m, s in zip(mean_times, std_times)], 
                         [m + s for m, s in zip(mean_times, std_times)], 
                         alpha=0.2)

    plt.xlabel("Conformance Rate (%)")
    plt.ylabel("Boarding Time (min)")
    plt.title("Boarding Time vs Conformance Rate for Different Strategies")
    plt.legend(title="Seat Assignment Strategy")
    plt.grid(True, linestyle="--", linewidth=0.7)

    plt.show()



if __name__ == "__main__":
    main()


