from mesa.batchrunner import batch_run
import pandas as pd
import os

from airplane_boarding_model.boarding_model import BoardingModel


# Seed 3: 438 iterations, took 4:48 minutes on Seiji's Laptop
parameters = {
    "seed": range(10),
    "steps_per_second": 2,
    "aisle_speed": 0.8,
    "number_of_passengers": range(29, 175),
    "seat_assignment_method": "random"
}


def main():
    if not os.path.exists("results"):
        os.makedirs("results")
    
    if not os.path.exists("results/validation"):
        os.makedirs("results/validation")
        
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
    
    seat_shuffle_times_df.to_csv("results/validation/seat_shuffle_times.csv")
    boarding_times_df.to_csv("results/validation/boarding_times.csv")


if __name__ == '__main__':
    main()