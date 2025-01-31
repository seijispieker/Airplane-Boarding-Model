from mesa.batchrunner import batch_run
import pandas as pd
import os

from airplane_boarding_model.boarding_model import BoardingModel


parameters = {
    "steps_per_second": 2,
    "aisle_speed": 0.8,
    "number_of_passengers": range(29, 175),
    "seat_assignment_method": "random"
}


iterations_per_config = 100


def main():
    if not os.path.exists("results"):
        os.makedirs("results")
    
    if not os.path.exists("results/validation"):
        os.makedirs("results/validation")

    batches = []
    batch_size = iterations_per_config

    while batch_size > 10:
        batches.append(range(batch_size - 10, batch_size))
        batch_size -= 10
    if batch_size > 0:
        batches.append(range(batch_size))
    
    for batch in reversed(batches):
        print(f"Running batch {batch}")
        run_batch(batch)


def run_batch(batch):
    parameters["seed"] = batch
    
    results = batch_run(
        model_cls=BoardingModel,
        parameters=parameters,
        number_processes=os.cpu_count(),
        data_collection_period=-1,
        iterations=1,
        max_steps=parameters["steps_per_second"] * 60 * 50,
        display_progress=True,
    )
    
    results_df = pd.DataFrame(results)
    results_df = results_df.drop(columns=["iteration"], inplace=False)
    
    seat_shuffle_times_df = results_df.drop(
        columns=[
            "Step",
            "steps_per_second",
            "aisle_speed",
            "seat_assignment_method",
            "Time (s)",
            "Boarding completed",
        ],
        inplace=False
    )
    
    boarding_times_df = results_df.drop_duplicates(
        subset=["RunId"],
        inplace=False
    )
    boarding_times_df = boarding_times_df.drop(
        columns=[
            "AgentID",
            "Seat shuffle time (s)",
            "Seat shuffle type (A/B/C/D)",
        ],
        inplace=False
    )
    
    batch_nums = "".join([str(batch_num) for batch_num in batch])
    seat_shuffle_times_df.to_csv(f"results/validation/seat_shuffle_times_{batch_nums}.csv")
    boarding_times_df.to_csv(f"results/validation/boarding_times_{batch_nums}.csv")


if __name__ == '__main__':
    main()