from __future__ import annotations
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

from airplane_boarding_model.boarding_model import BoardingModel
from airplane_boarding_model.passenger import Passenger

if TYPE_CHECKING:
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
    # "occupancy": Slider(
    #     label="Occupancy (0-1)",
    #     value=0.85,
    #     min=0,
    #     max=1,
    #     step=0.05,
    #     dtype=float
    # ),
    "number_of_passengers": {
        "type": "InputText",
        "value": 174,
        "label": "Number of Passengers",
    },
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
        "size": 100,
        "alpha": 1.0,
    }
    
    if type(agent) is not Passenger:
        portrayal["color"] = "white"
        return portrayal
    
    colors = list(mcolors.XKCD_COLORS)
    color_index = agent.unique_id % len(colors)
    portrayal["color"] = colors[color_index]
    
    if agent.seated:
        portrayal["alpha"] = 0.6
    
    return portrayal


def post_process_space(ax: plt.Axes):
    airplane = model.airplane

    adjusted_grid_width = airplane.grid_width - 5
    
    for row_index in range(airplane.grid_height):  
        for col_index in range(adjusted_grid_width):  
            if col_index < 5 or col_index >= adjusted_grid_width - 2:
                if row_index in [0, 1, 2, 4, 5, 6]:
                    ax.add_patch(
                        plt.Rectangle(
                            (col_index - 0.5, row_index - 0.5),
                            1,
                            1,
                            color="white",
                            zorder=0,
                        )
                    )
                    continue
                elif row_index == 3:
                    # Entrance and back of the plane color
                    ax.add_patch(
                        plt.Rectangle(
                            (col_index - 0.5, row_index - 0.5),
                            1, 
                            1, 
                            color="green",
                            alpha=0.3,
                            zorder=0,
                        )
                    )

            # Space between the seats color
            if 5 <= col_index <= 61 and (col_index - 5) % 2 == 0:
                if row_index in [0, 1, 2, 4, 5, 6]:
                    # Left half
                    ax.add_patch(
                        plt.Rectangle(
                            (col_index - 0.5, row_index - 0.5), 
                            0.5,  
                            1, 
                            color="blue",
                            alpha=0.3,
                            zorder=0,
                        )
                    )
                    # Right half
                    ax.add_patch(
                        plt.Rectangle(
                            (col_index, row_index - 0.5),  
                            0.5,  
                            1, 
                            color="gray",
                            alpha=0.3,
                            zorder=0,
                        )
                    )
                    continue

            x_offset = -0.5
            y_offset = -0.5

            # Aisle row color
            if row_index == 3:
                ax.add_patch(
                    plt.Rectangle(
                        (col_index + x_offset, row_index + y_offset),
                        1,
                        1,
                        color="gray",
                        alpha=0.3,
                    )
                )
            # Seat rows color
            else:
                # Left half
                ax.add_patch(
                    plt.Rectangle(
                        (col_index - 0.5, row_index - 0.5),  
                        0.5, 
                        1, 
                        color="gray",
                        alpha=0.3,
                        zorder=0,
                    )
                )

                ax.add_patch(
                    plt.Rectangle(
                        (col_index, row_index - 0.5),  
                        0.5, 
                        1, 
                        color="blue",
                        alpha=0.3,
                        zorder=0,
                    )
                )

    # Visualization of row numbers
    row_number = 1
    for col_index in range(6, adjusted_grid_width - 2, 2):
        ax.text(
            col_index,
            -1,
            str(row_number),
            fontsize=10,
            ha="center",
            va="center",
            color="black",
            weight="bold",
        )
        row_number += 1

    # Specific changes for column 6 and the penultimate column
    for row_index in [0, 1, 2, 4, 5, 6]:
        # Left half
        ax.add_patch(
            plt.Rectangle(
                (5 - 0.5, row_index - 0.5), 
                0.5,  
                1,  
                color="gray",
                alpha=0.3,
                zorder=0,
            )
        )

        penultimate_col = adjusted_grid_width - 3  
        ax.add_patch(
            plt.Rectangle(
                (penultimate_col - 0.5, row_index - 0.5),  
                0.5,  
                1, 
                color="blue",
                alpha=0.3,
                zorder=0,
            )
        )

    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_xlim(-0.5, adjusted_grid_width - 0.5)
    ax.set_ylim(-0.5, airplane.grid_height - 0.5)
    ax.set_aspect("equal", adjustable="box")
    ax.figure.set_size_inches(20, 8)

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