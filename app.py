from __future__ import annotations
from typing import TYPE_CHECKING

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

from airplane_boarding_model.boarding_model import BoardingModel

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    from airplane_boarding_model.passenger import Passenger

        
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "rows": 30,
    "columns": 7,
    "aisle_column": 3,
    "passenger_count": Slider(
        label="Passenger Count",
        value=180,
        min=0,
        max=180,
        step=1,
        dtype=int
    ),
    "steps_per_second": Slider(
        label="Steps per Second",
        value=1,
        min=1,
        max=100,
        step=1,
        dtype=int
    ),
    "movement_speed_cells_per_second": Slider(
        label="Movement Speed (Cells per Second)",
        value=1, # TODO: What value to fix to for this?
        min=0,
        max=5,
        step=0.1,
        dtype=float
    ),
    "boarding_rate_seconds": Slider(
        label="Boarding Rate (Seconds)",
        value=1, # TODO: What value to fix to for this?
        min=1,
        max=10,
        step=0.1,
        dtype=float
    ),
    "luggage_delay_seconds": Slider(
        label="Luggage Delay (Seconds)",
        value=2, # TODO: What value to fix to for this?
        min=1,
        max=10,
        step=0.1,
        dtype=float
    ),
    "seat_assignment_method": {
        "type": "Select",
        "value": "back_to_front",
        "values": ["back_to_front", "random"],
        "label": "Seat Assignment Method",
    },
    "adherence": Slider(
        label="adherence (%)",
        value=95,
        min=0,
        max=100,
        step=1,
        dtype=int
    ),
}


model = BoardingModel()


def passenger_potrayel(passenger: Passenger):
    if passenger is None:
        return
    
    portrayal = {
        "size": 50,
    }
    
    if passenger.seated:
        portrayal["color"] = "grey"
    
    return portrayal


def post_process_space(ax: plt.Axes):
    ax.set_xticks(range(model_params["rows"]))


space_component = make_space_component(
    agent_portrayal=passenger_potrayel,
    post_process=post_process_space,
)


page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Airplane Boarding Model",
)