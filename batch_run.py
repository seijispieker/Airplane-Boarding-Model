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
    results_df = results_df.drop(columns=["iteration"], inplace=False)
    
    seat_shuffle_times_df = results_df.drop(
        columns=[
            "Step",
            "steps_per_second",
            "aisle_speed",
            "occupancy",
            "seat_assignment_method",
            "conformance",
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
            "Seat shuffle type (A/B/C/D)"
        ],
        inplace=False
    )
    
    seat_shuffle_times_df.to_csv("results/seat_shuffle_times.csv")
    boarding_times_df.to_csv("results/boarding_times.csv")


if __name__ == '__main__':
    main()