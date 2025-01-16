from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger


def passenger_potrayel(passenger: Passenger):
    if passenger is None:
        return
    
    portrayal = {
        "size": 50,
    }
    
    if passenger.seated:
        portrayal["color"] = "grey"
    
    return portrayal
        
        
model_params = {
    "rows": 30,
    "columns": 7,
    "aisle_column": 3,
    "passenger_count": {
        "type": "InputText",
        "value": 180,
        "label": "Passenger Count",
    },
    "boarding_rate": Slider(
        label="Boarding Rate",
        value=2,
        min=1,
        max=10,
        step=1,
    ),
    "luggage_delay": Slider(
        label="Luggage Delay",
        value=2,
        min=1,
        max=10,
        step=1,
    ),
    "boarding_method": {
        "type": "Select",
        "value": "back_to_front",
        "values": ["back_to_front", "random"],
        "label": "Boarding Method",
    },
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    }
}


model = BoardingModel()
space_component = make_space_component(
    agent_portrayal=passenger_potrayel,
)

page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Airplane Boarding Model",
)