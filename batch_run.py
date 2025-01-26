from mesa.batchrunner import batch_run
import numpy as np
import pandas as pd
import os
from airplane_boarding_model.boarding_model import BoardingModel


parameters = {
    "seed": range(10),
    "steps_per_second": 2,
    "aisle_speed": 0.8,
    "occupancy": np.linspace(start=0.1, stop=1, num=10),
    "seat_assignment_method": "random",
    "conformance": 100
}

def save_seat_shuffle_times(model, run_id):
    """
    Extract the 'Seat shuffle times' table from the model's DataCollector.

    Args:
        model: A completed instance of BoardingModel.

    Returns:
        DataFrame containing the seat shuffle times table.
    """
    if "Seat shuffle times" in model.datacollector.tables:
        shuffle_data = model.datacollector.get_table_dataframe("Seat shuffle times")
        shuffle_data["RunId"] = run_id
        return shuffle_data
    else:
        print(f"No 'Seat shuffle times' data found for RunId {run_id}.")
        return pd.DataFrame()

def main():
    if not os.path.exists("results"):
        os.makedirs("results")
        
    results = batch_run(
        model_cls=BoardingModel,
        parameters=parameters,
        number_processes=4,
        data_collection_period=-1,
        iterations=1,
        max_steps=parameters["steps_per_second"] * 60 * 50,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)
    results_df.to_csv("results/batch_run_results.csv")

    # Save 'Seat shuffle times'
    shuffle_times_list = []
    for run_id, result in enumerate(results):
        if "datacollector" in result:
            shuffle_times = save_seat_shuffle_times(result["datacollector"], run_id)
            if not shuffle_times.empty:
                shuffle_times["occupancy"] = result["occupancy"]
                shuffle_times["seed"] = result["seed"]
                shuffle_times_list.append(shuffle_times)

    # Combine and save 'Seat shuffle times' to a CSV
    if shuffle_times_list:
        shuffle_times_df = pd.concat(shuffle_times_list, ignore_index=True)
        shuffle_times_df.to_csv("results/seat_shuffle_times.csv", index=False)
        print("Saved 'Seat shuffle times' to seat_shuffle_times.csv.")
    else:
        print("No 'Seat shuffle times' data found.")

    for result in results:
        print(result.keys())

if __name__ == '__main__':
    main()