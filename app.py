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
    "passenger_count": {
        "type": "InputText",
        "value": 180,
        "label": "Passenger Count",
    },
    "steps_per_second": Slider(
        label="Steps per Second",
        value=1,
        min=1,
        max=100,
        step=1,
    ),
    "movement_speed": Slider(
        label="Movement Speed (Cells per Second)",
        value=1,
        min=1,
        max=10,
        step=1,
    ),
    "boarding_rate": Slider(
        label="Boarding Rate (Seconds)",
        value=2,
        min=1,
        max=10,
        step=1,
    ),
    "luggage_delay": Slider(
        label="Luggage Delay (Seconds)",
        value=2,
        min=1,
        max=10,
        step=1,
    ),
    "seat_assignment_method": {
        "type": "Select",
        "value": "back_to_front",
        "values": ["back_to_front", "random"],
        "label": "Seat Assignment Method",
    },
    "adherence": Slider(
        label="adherence",
        value=95,
        min=0,
        max=100,
        step=1,
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