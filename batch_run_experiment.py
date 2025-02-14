from mesa.batchrunner import batch_run
import pandas as pd
import os

from airplane_boarding_model.boarding_model import BoardingModel


parameters = {
    "seed": range(1),
    "steps_per_second": 2,
    "aisle_speed": 0.8,
    "number_of_passengers": range(round(0.71 * 174), round(0.81 * 174) + 1),
    "conformance": range(0,101, 10)
}


seat_assignment_methods = [
     "back_to_front",
     "random",
    #"segmented_random_3",
    #"segmented_random_4",
    #"outside_in",
    #"steffen_perfect"
]


def main():
    if not os.path.exists("results"):
        os.makedirs("results")
    
    for method in seat_assignment_methods:
        print(f"Running experiment for seat assignment method: {method}")
        seat_assignment_method(method)


def seat_assignment_method(method):
    if not os.path.exists("results/experiment"):
        os.makedirs("results/experiment")
        
    parameters["seat_assignment_method"] = method
        
    results = batch_run(
        model_cls=BoardingModel,
        parameters=parameters,
        number_processes=os.cpu_count(),
        data_collection_period=-1,
        iterations=1,
        max_steps=parameters["steps_per_second"] * 60 * 100,
        display_progress=True,
    )
    
    results_df = pd.DataFrame(results)
    results_df.drop(columns=["iteration"], inplace=True)
    results_df.drop_duplicates(subset=["RunId"], inplace=True)
    results_df.drop(
        columns=[
            "AgentID",
            "Seat shuffle time (s)",
            "Seat shuffle type (A/B/C/D)",
        ],
        inplace=True
    )
    
    results_df.to_csv(f"results/experiment/results_{method}.csv")


if __name__ == '__main__':
    main()