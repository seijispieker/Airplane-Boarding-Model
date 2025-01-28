from mesa.batchrunner import batch_run
import pandas as pd
import os

from airplane_boarding_model.boarding_model import BoardingModel

parameters = {
    # TODO: more seeds
    "seed": range(1),
    "steps_per_second": 2,
    "aisle_speed": 0.8,
    "number_of_passengers": range(round(0.71 * 174), round(0.81 * 174) + 1),
    "seat_assignment_method": [
        "random",
        "back_to_front",
        "segmented_random",
        "outside_in",
        "steffen_perfect"
    ],
    # TODO: change steps to 1
    "conformance": range(0, 101, 10)
}


def main():
    if not os.path.exists("results"):
        os.makedirs("results")
    
    if not os.path.exists("results/experiment"):
        os.makedirs("results/experiment")
        
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
    
    results_df = results_df.drop_duplicates(
        subset=["RunId"],
        inplace=False
    )
    results_df = results_df.drop(
        columns=[
            "AgentID",
            "Seat shuffle time (s)",
            "Seat shuffle type (A/B/C/D)",
        ],
        inplace=False
    )
    
    results_df.to_csv("results/experiment/results.csv")


if __name__ == '__main__':
    main()