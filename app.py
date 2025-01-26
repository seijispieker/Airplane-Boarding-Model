from __future__ import annotations
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import mesa

        
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "steps_per_second": Slider(
        label="Steps per Second",
        value=2,
        min=1,
        max=100,
        step=1,
        dtype=int
    ),
    "aisle_speed": Slider(
        label="Aisle Speed (m/s)",
        value=0.8,
        min=0,
        max=2,
        step=0.1,
        dtype=float
    ),
    "occupancy": Slider(
        label="Occupancy (0-1)",
        value=0.85,
        min=0,
        max=1,
        step=0.05,
        dtype=float
    ),
    "seat_assignment_method": {
        "type": "Select",
        "value": "back_to_front",
        "values": ["back_to_front", "random", "segmented_random", "outside_in", "steffen_perfect", "debug_B", "debug_C", "debug_D"],
        "label": "Seat Assignment Method",
    },
    "conformance": Slider(
        label="conformance (%)",
        value=95,
        min=0,
        max=100,
        step=1,
        dtype=int
    ),
}


model = BoardingModel()


def agent_portayal(agent: mesa.Agent):
    portrayal = {
        "size": 50,
        "alpha": 1.0,
    }
    
    if type(agent) is not Passenger:
        portrayal["color"] = "white"
        return portrayal
    
    colors = list(mcolors.TABLEAU_COLORS)
    # color_index = model.passengers.index(agent) % len(colors)
    color_index = agent.unique_id % len(colors)
    portrayal["color"] = colors[color_index]
    
    if agent.seated:
        portrayal["alpha"] = 0.3
    
    return portrayal


def post_process_space(ax: plt.Axes):
    pass


space_component = make_space_component(
    agent_portrayal=agent_portayal,
    post_process=post_process_space,
)


page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Airplane Boarding Model",
)