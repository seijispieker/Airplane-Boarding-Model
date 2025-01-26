from mesa.batchrunner import batch_run
import numpy as np
import pandas as pd
import os
from airplane_boarding_model.boarding_model import BoardingModel


parameters = {
    "seed": 42,
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
        iterations=10,
        max_steps=parameters["steps_per_second"] * 60 * 30,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)
    results_df.to_csv("results/batch_run_results.csv")


if __name__ == '__main__':
    main()