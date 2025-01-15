from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

from airplane_boarding_model.boarding_model import BoardingModel


def passenger_potrayel(agent):
    if agent is None:
        return
    
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.5,
        "Layer": 1,
        "Color": "red",
    }
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