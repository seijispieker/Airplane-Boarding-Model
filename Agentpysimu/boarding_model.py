import agentpy as ap
from airplane import Airplane
from passenger import Passenger

class BoardingModel(ap.Model):
    def setup(self):
        """
        Set up the airplane and passengers.
        """
        self.airplane = Airplane(rows=self.p.rows, seats_per_row=self.p.seats_per_row, aisle_col=self.p.aisle_col)
        self.passengers = ap.AgentList(self, self.p.passenger_count, Passenger)
        self.initialize_visualization()

        # Validate airplane layout
        assert len(self.airplane.layout) == self.p.rows, "Airplane layout rows mismatch"
        for row in self.airplane.layout:
            assert len(row) == self.p.seats_per_row, "Airplane layout column mismatch"

        # Assign passengers to valid seats
        seat_index = 0
        for passenger in self.passengers:
            while True:
                row = seat_index // self.airplane.seats_per_row
                col = seat_index % self.airplane.seats_per_row
                seat = self.airplane.layout[row][col]

                seat_index += 1  # Increment seat index

                if seat != "AISLE":  # Skip the aisle
                    passenger.seat = seat  # Assign valid seat
                    passenger.position = (row, self.airplane.aisle_col)  # Start in the aisle
                    break

        # Ensure all seats are covered
        total_seats = sum(1 for row in self.airplane.layout for col in row if col != "AISLE")
        assert total_seats == len(self.passengers), "Mismatch between passengers and available seats"

        # Initialize the data dictionary correctly
        self.data = ap.DataDict({
            'boarded': [],
            'aisle_congestion': [0]  # Initialize with 0 congestion
        })

        print(f"Initial data structure: {self.data}")
        print(f"Airplane layout: {self.airplane.layout}")


    def step(self):
        """
        Advance the simulation by one step. Handles row and column movements separately,
        with visualization updates after each movement to ensure step-by-step progression.
        """
        aisle_occupancy = {}  # Track passengers per row of the aisle for this step
        has_moved = False  # Track if any passenger moved this step

        for passenger in self.passengers:
            if not passenger.boarded:
                # Introduce delay for passenger
                if not hasattr(passenger, "delay"):
                    import random
                    passenger.delay = random.randint(0, 40)  # Random delay between 0 and 30 steps

                if passenger.delay > 0:
                    passenger.delay -= 1
                    continue  # Skip this passenger's movement for this step

                # Get current and target positions
                current_row, current_col = passenger.position
                target_row = int(passenger.seat[:-1]) - 1  # Extract row from seat label
                target_col = ord(passenger.seat[-1]) - ord('A')  # Convert seat letter to column index

                # Track aisle congestion
                aisle_occupancy[current_row] = aisle_occupancy.get(current_row, 0) + 1

                # Add a dynamic delay based on local congestion
                congestion_level = aisle_occupancy.get(current_row, 0)
                if congestion_level > 1:  # More than 1 passenger in the aisle row
                    passenger.delay += congestion_level - 1  # Increase delay proportional to congestion
                    continue

                # Handle row movement (prioritized)
                if current_row != target_row:
                    next_row = current_row + 1 if current_row < target_row else current_row - 1

                    # Check congestion in the next row
                    if aisle_occupancy.get(next_row, 0) < 2:  # Limit to 2 passengers per row
                        passenger.position = (next_row, current_col)  # Incremental row movement
                        aisle_occupancy[next_row] = aisle_occupancy.get(next_row, 0) + 1
                        has_moved = True
                        self.update_visualization()  # Visualize after row movement
                        continue  # Skip further processing for this passenger

                # Handle column movement (only if row is correct)
                elif current_col != target_col:
                    next_col = current_col + 1 if current_col < target_col else current_col - 1
                    passenger.position = (current_row, next_col)  # Incremental column movement
                    has_moved = True
                    self.update_visualization()  # Visualize after column movement
                    continue

                # Passenger successfully seated
                elif current_row == target_row and current_col == target_col:
                    passenger.boarded = True

        # Update visualization after all passengers are processed
        self.update_visualization()

        # Calculate and record aisle congestion
        aisle_congestion = sum(1 for row, count in aisle_occupancy.items() if count > 1)  # Count rows with >1 passenger
        self.data['aisle_congestion'].append(aisle_congestion)

        # Debugging: Aisle congestion information
        print(f"Step {self.t}: Aisle congestion = {aisle_congestion}")

        # Debugging: Print passenger states
        for passenger in self.passengers:
            print(f"Passenger {passenger}: Position = {passenger.position}, Boarded = {passenger.boarded}")

        # Termination condition: Stop if all passengers are seated or no one moved
        all_seated = all(passenger.boarded for passenger in self.passengers)
        if all_seated:
            print("All passengers are seated. Simulation ending.")
            self.stop()
        elif not has_moved:
            print("No passengers moved this step. Simulation stuck.")
            self.stop()

    def update(self):
        """
        Collect data during the simulation.
        """
        # Track the number of boarded passengers
        boarded_count = sum(1 for p in self.passengers if p.boarded)
        self.data['boarded'].append(boarded_count)

        # Debugging information
        print(f"Step {self.t}: Boarded passengers = {boarded_count}")
        print(f"Step {self.t}: Aisle congestion = {self.data['aisle_congestion'][-1]}")

    def end(self):
        """
        Finalize the simulation and report results.
        """
        # Report the final number of boarded passengers
        final_boarded_count = sum(1 for p in self.passengers if p.boarded)
        self.report('Final boarded count', final_boarded_count)

        # Report the total steps taken
        self.report('Total steps', self.t)

        # Report final boarding percentage
        self.report('Final boarding percentage', final_boarded_count / self.p.passenger_count * 100)

        if final_boarded_count == self.p.passenger_count:
            print("Simulation ended: All passengers are seated.")
        else:
            print("Simulation ended: Maximum steps reached.")

        self.finalize_visualization()
    
    def initialize_visualization(self):
        """
        Set up the visualization environment.
        """
        import matplotlib.pyplot as plt
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.im = None
        self.visual_data = []
        print("Visualization initialized.")

    def update_visualization(self):
        """
        Update the visualization after each step, ensuring the aisle is correctly represented in the middle.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # Create a grid representing the airplane
        grid = np.zeros((self.airplane.rows, self.airplane.seats_per_row))

        # Mark aisle cells explicitly
        grid[:, self.airplane.aisle_col] = -1  # Aisle cells

        # Update the grid with passenger positions
        for passenger in self.passengers:
            row, col = passenger.position
            if passenger.boarded:
                grid[row, col] = 1  # Seated passenger
            elif col == self.airplane.aisle_col:
                grid[row, col] = 0.5  # Passenger in aisle

        # Update the plot
        if self.im:
            self.im.set_data(grid)
        else:
            self.im = self.ax.imshow(grid, cmap="coolwarm", interpolation="nearest")
            self.ax.set_title("Airplane Boarding Visualization")
            self.ax.set_xlabel("Seats")
            self.ax.set_ylabel("Rows")

        plt.pause(0.1)  # Pause to allow visualization updates
        self.visual_data.append(grid.copy())
    
    def finalize_visualization(self):
        """
        Finalize and save the visualization.
        """
        import matplotlib.pyplot as plt
        self.fig.savefig("boarding_visualization.png")
        plt.close(self.fig)
        print("Visualization finalized and saved.")

    