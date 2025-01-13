import agentpy as ap

from airplane_boarding_model.airplane import Airplane
from airplane_boarding_model.passenger import Passenger


class BoardingModel(ap.Model):
    def setup(self):
        """
        Assign passengers to seats in a back-to-front order as the baseline model.
        """
        self.airplane = Airplane(rows=self.p.rows, seats_per_row=self.p.seats_per_row, aisle_col=self.p.aisle_col)
        self.passengers = ap.AgentList(self, self.p.passenger_count, Passenger)
        self.initialize_visualization()

        # Print layout for verification
        print("Airplane Layout:")
        self.airplane.display_layout()

        # Assign seats in reverse row order
        rows = list(range(self.airplane.rows - 1, -1, -1))  # Back to front
        seat_index = 0

        print(f"rows{rows}")

        for idx, passenger in enumerate(self.passengers):
            while True:
                # Determine row and column based on seat index
                row = rows[seat_index // self.airplane.seats_per_row]
                col = seat_index % self.airplane.seats_per_row
                seat = self.airplane.layout[row][col]

                seat_index += 1

                # Skip if the seat is an aisle
                if seat == "AISLE":
                    print(f"Skipping aisle at row {row}, col {col}")
                    continue  # Go to the next iteration of the loop

                # Assign valid seat and exit the loop
                print(f"Assigning seat {seat} to Passenger {idx}")
                passenger.seat = seat
                passenger.position = None  # Passenger starts outside the plane
                passenger.boarding_delay = idx * self.p.boarding_rate  # Baseline: No delays
                break  # Exit the loop after assigning a valid seat

        total_seats = sum(1 for row in self.airplane.layout for col in row if col != "AISLE")
        assert total_seats == len(self.passengers)

        self.data = ap.DataDict({'boarded': [], 'aisle_congestion': []})

    def step(self):
        """
        Advance the simulation by one step. Handles row and column movements separately,
        ensuring passengers are seated only when fully in their assigned seat.
        """
        aisle_occupancy = {}  # Track passengers in the aisle
        has_moved = False  # Track if any passenger moved this step

        for passenger in self.passengers:
            if not passenger.boarded:
                # Handle boarding delay
                if passenger.boarding_delay > 0:
                    passenger.boarding_delay -= 1
                    continue  # Skip passengers not yet ready to enter the plane

                # Place passenger at the entrance if not yet in the plane
                if passenger.position is None:
                    passenger.position = (0, self.airplane.aisle_col)  # Entrance to the aisle
                    print(f"Passenger {passenger} enters the plane at step {self.t}")
                    has_moved = True
                    continue

                # Get current and target positions
                current_row, current_col = passenger.position
                target_row = int(passenger.seat[:-1]) - 1
                target_col = ord(passenger.seat[-1]) - ord('A')
                if target_col >= 3:
                    target_col = target_col + 1

                # Track aisle occupancy for congestion tracking
                aisle_occupancy[current_row] = aisle_occupancy.get(current_row, 0) + 1

                # Mark passenger as seated only if at both the correct row and column
                if current_row == target_row and current_col == target_col:
                    passenger.boarded = True
                    print(f"Passenger {passenger} seated at {passenger.seat} at step {self.t}")
                    has_moved = True
                    continue

                # Row movement: Move toward the target row
                if current_row != target_row:
                    next_row = current_row + 1 if current_row < target_row else current_row - 1

                    # Allow movement if there is no direct conflict in the next row
                    if aisle_occupancy.get(next_row, 0) < 1:  # Ensure no congestion in the aisle
                        passenger.position = (next_row, current_col)
                        aisle_occupancy[next_row] = aisle_occupancy.get(next_row, 0) + 1
                        print(f"Passenger {passenger} moves to row {next_row} at step {self.t}")
                        has_moved = True
                        continue

                # Column movement: Only move if at the correct row
                elif current_row == target_row and current_col != target_col:
                    next_col = current_col + 1 if current_col < target_col else current_col - 1

                    # Ensure the seat column is free
                    passenger.position = (current_row, next_col)
                    print(f"Passenger {passenger} moves to column {next_col} in row {current_row} at step {self.t}")
                    has_moved = True
                    continue

        # Debugging: Print aisle occupancy
        print(f"Aisle occupancy at step {self.t}: {aisle_occupancy}")

        # Calculate and record aisle congestion
        aisle_congestion = sum(1 for row, count in aisle_occupancy.items() if count > 1)
        self.data['aisle_congestion'].append(aisle_congestion)

        # Update visualization
        self.update_visualization()

        # Termination condition
        all_seated = all(passenger.boarded for passenger in self.passengers)
        if all_seated:
            print("All passengers are seated. Simulation ending.")
            self.stop()
        elif not has_moved:
            print("No passengers moved this step. Simulation stuck.")
            self.stop()

    def update(self):
        boarded_count = sum(1 for p in self.passengers if p.boarded)
        self.data['boarded'].append(boarded_count)

    def initialize_visualization(self):
        import matplotlib.pyplot as plt
        import numpy as np
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        layout_grid = np.zeros((self.airplane.rows, self.airplane.seats_per_row))
        layout_grid[:, self.airplane.aisle_col] = -1
        self.ax.imshow(layout_grid, cmap="Greys", interpolation="nearest", alpha=0.3)
        self.scatter = self.ax.scatter([], [], color='blue', s=50, label="Passengers")
        self.ax.set_title("Airplane Boarding Visualization")
        self.ax.set_xlabel("Seats")
        self.ax.set_ylabel("Rows")
        self.ax.legend()

    def update_visualization(self):
        import matplotlib.pyplot as plt
        x_positions = []
        y_positions = []
        colors = []

        for passenger in self.passengers:
            if passenger.position is None:
                continue

            row, col = passenger.position
            x_positions.append(col)
            y_positions.append(row)

            # Assign colors based on passenger status
            if passenger.boarded:
                colors.append("green")  # Boarded
            elif col == self.airplane.aisle_col:
                colors.append("red")  # In aisle
            else:
                colors.append("blue")  # Moving to seat

        self.scatter.set_offsets(list(zip(x_positions, y_positions)))
        self.scatter.set_color(colors)
        plt.pause(0.5)  # Slower updates for better visualization