import agentpy as ap
from airplane import Airplane
from passenger import Passenger

class BoardingModel(ap.Model):
    def setup(self):
        self.airplane = Airplane(rows=self.p.rows, seats_per_row=self.p.seats_per_row, aisle_col=self.p.aisle_col)
        self.passengers = ap.AgentList(self, self.p.passenger_count, Passenger)
        self.initialize_visualization()

        seat_index = 0
        for idx, passenger in enumerate(self.passengers):
            while True:
                row = seat_index // self.airplane.seats_per_row
                col = seat_index % self.airplane.seats_per_row
                seat = self.airplane.layout[row][col]
                seat_index += 1
                if seat != "AISLE":
                    passenger.seat = seat
                    passenger.position = None
                    passenger.boarding_delay = idx * self.p.boarding_rate
                    break

        total_seats = sum(1 for row in self.airplane.layout for col in row if col != "AISLE")
        assert total_seats == len(self.passengers)

        self.data = ap.DataDict({'boarded': [], 'aisle_congestion': [0]})

    def step(self):
        aisle_occupancy = {}  # Track passengers per row of the aisle for this step
        has_moved = False  # Track if any passenger moved this step

        for passenger in self.passengers:
            if not passenger.boarded:
                # Handle boarding delay
                if passenger.boarding_delay > 0:
                    passenger.boarding_delay -= 1
                    continue  # Skip passengers not yet ready to enter the plane

                # If position is None (outside the plane), place them at the entrance
                if passenger.position is None:
                    passenger.position = (0, self.airplane.aisle_col)  # Start at the entrance
                    has_moved = True
                    continue

                # Get current and target positions
                current_row, current_col = passenger.position
                target_row = int(passenger.seat[:-1]) - 1  # Extract row from seat label
                target_col = ord(passenger.seat[-1]) - ord('A')  # Convert seat letter to column index

                # Track aisle occupancy
                aisle_occupancy[current_row] = aisle_occupancy.get(current_row, 0) + 1

                # Mark as boarded if passenger has reached the target
                if current_row == target_row and current_col == target_col:
                    passenger.boarded = True
                    continue

                # Handle aisle (row) movement: Move toward the target row
                if current_row != target_row:
                    next_row = current_row + 1 if current_row < target_row else current_row - 1

                    # Ensure the next row is not congested and allows movement
                    if aisle_occupancy.get(next_row, 0) == 0:  # Only move if the next row is free
                        passenger.position = (next_row, current_col)
                        has_moved = True
                        aisle_occupancy[next_row] = aisle_occupancy.get(next_row, 0) + 1
                        continue

                # Handle column movement: Only if passenger is at the correct row
                elif current_row == target_row and current_col != target_col:
                    next_col = current_col + 1 if current_col < target_col else current_col - 1

                    # Ensure the seat column is free
                    passenger.position = (current_row, next_col)
                    has_moved = True
                    continue

        # Debugging: Print aisle occupancy
        print(f"Aisle occupancy at step {self.t}: {aisle_occupancy}")

        # Calculate and record aisle congestion
        aisle_congestion = sum(1 for row, count in aisle_occupancy.items() if count > 1)
        self.data['aisle_congestion'].append(aisle_congestion)

        # Update visualization
        self.update_visualization()

        # Termination condition: Stop if all passengers are seated or no one moved
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
        """
        Update the visualization after each step, showing agents (passengers) moving in real time.
        """
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
            colors.append("green" if passenger.boarded else "red" if col == self.airplane.aisle_col else "blue")

        self.scatter.set_offsets(list(zip(x_positions, y_positions)))
        self.scatter.set_color(colors)
        plt.pause(0.2)  # Slower updates to visualize movements better
    