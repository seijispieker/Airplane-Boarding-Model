import pandas as pd
import matplotlib.pyplot as plt
import os



def main():
    print(plot_boarding_times_conformance())

def plot_boarding_times_conformance():
    results_dir = "results/experiment"

    # File mapping for specific strategies
    file_list = {
        "random": "results_random.csv",
        "back_to_front": "results_back_to_front.csv",
        "outside_in": "results_outside_in.csv",
        "steffen_perfect": "results_steffen_perfect.csv",
        "segmented_random_3": "results_segmented_random_3.csv",
        "segmented_random_4": "results_segmented_random_4.csv"
    }

    results_df = pd.DataFrame()
    
    # Load data
    for strategy, filename in file_list.items():
        file_path = os.path.join(results_dir, filename)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["strategy"] = strategy 
            results_df = pd.concat([results_df, df], ignore_index=True)

    if results_df.empty:
        print("No data found. Check the file paths.")
        return

    conformance_rates = results_df["conformance"]
    boarding_times = results_df["Time (s)"] / 60 
    strategies = results_df["strategy"]

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

    graph_1_strategies = ["random", "back_to_front", "outside_in", "steffen_perfect"]
    graph_2_strategies = ["random", "segmented_random_3", "segmented_random_4"]

    random_std_values = []
    if "random" in strategy_data:
        all_random_values = [time for conf in strategy_data["random"] for time in strategy_data["random"][conf]]
        if all_random_values:
            random_std = pd.Series(all_random_values).std()
            random_std_values.append(f"Random Std: {random_std:.2f} min")

    def plot_graph(selected_strategies, title):
        plt.figure(figsize=(10, 6))

        for strategy in selected_strategies:
            if strategy in strategy_data:
                conf_list = sorted(strategy_data[strategy].keys())  
                mean_times = [pd.Series(strategy_data[strategy][conf]).mean() for conf in conf_list]
                std_times = [pd.Series(strategy_data[strategy][conf]).std() for conf in conf_list]

                plt.plot(conf_list, mean_times, label=strategy, linewidth=2)

                if strategy != "random":
                    plt.fill_between(conf_list, 
                                     [m - s for m, s in zip(mean_times, std_times)], 
                                     [m + s for m, s in zip(mean_times, std_times)], 
                                     alpha=0.2)

        plt.xlabel("Conformance Rate (%)")
        plt.ylabel("Boarding Time (min)")
        plt.title(title)
        plt.legend(title="Seat Assignment Strategy")

        if random_std_values:
            plt.text(1.02, 0.95, "\n".join(random_std_values), transform=plt.gca().transAxes, fontsize=10,
                     verticalalignment="top", bbox=dict(facecolor="white", alpha=0.8, edgecolor="black"))

        plt.grid(True, linestyle="--", linewidth=0.7)
        plt.xlim(0, 100)
        plt.ylim(15, 35)
        plt.show()

    plot_graph(graph_1_strategies, "Boarding Time vs Conformance Rate (Graph 1)")
    plot_graph(graph_2_strategies, "Boarding Time vs Conformance Rate (Graph 2)")


if __name__ == "__main__":
    main()


