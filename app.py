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
    "luggage_delay_seconds": Slider(
        label="Luggage Delay (s)",
        value=2, # TODO: What value to fix to for this?
        min=1,
        max=10,
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
        "values": ["back_to_front", "random"],
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
    pass


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