from mesa.batchrunner import batch_run
import numpy as np
import pandas as pd
import os
from airplane_boarding_model.boarding_model import BoardingModel

# Define parameters for the simulation
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
        run_id: The ID of the run.

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

    # Replace batch_run with a custom loop for full access
    results_list = []
    shuffle_times_list = []
    run_id = 0

    for seed in parameters["seed"]:
        for occupancy in parameters["occupancy"]:
            # Initialize and run the model
            model = BoardingModel(
                seed=seed,
                steps_per_second=parameters["steps_per_second"],
                aisle_speed=parameters["aisle_speed"],
                occupancy=occupancy,
                seat_assignment_method=parameters["seat_assignment_method"],
                conformance=parameters["conformance"]
            )

            while model.running:
                model.step()

            # Save overall results (like batch_run)
            results_list.append({
                "RunId": run_id,
                "seed": seed,
                "occupancy": occupancy,
                "steps_per_second": parameters["steps_per_second"],
                "aisle_speed": parameters["aisle_speed"],
                "seat_assignment_method": parameters["seat_assignment_method"],
                "conformance": parameters["conformance"],
                "Steps": model.steps,  # Fixed here
                "Boarding completed": not model.running,
                "Time (s)": model.steps / parameters["steps_per_second"]  # Fixed here
            })

            # Save 'Seat shuffle times'
            shuffle_times = save_seat_shuffle_times(model, run_id)
            if not shuffle_times.empty:
                shuffle_times_list.append(shuffle_times)

            run_id += 1

    # Save overall results
    results_df = pd.DataFrame(results_list)
    results_df.to_csv("results/batch_run_results.csv", index=False)

    # Save seat shuffle times
    if shuffle_times_list:
        shuffle_times_df = pd.concat(shuffle_times_list, ignore_index=True)
        shuffle_times_df.to_csv("results/seat_shuffle_times.csv", index=False)
        print("Saved 'Seat shuffle times' to seat_shuffle_times.csv.")
    else:
        print("No 'Seat shuffle times' data found.")

if __name__ == "__main__":
    main()