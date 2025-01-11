class Airplane:
    def __init__(self, rows=30, seats_per_row=7, aisle_col=3):
        """
        Initialize an airplane layout.
        :param rows: Number of rows in the airplane.
        :param seats_per_row: Total seats per row (including aisle).
        :param aisle_col: Column index for the aisle.
        """
        self.rows = rows
        self.seats_per_row = seats_per_row
        self.aisle_col = aisle_col
        self.layout = self.create_layout()

    def create_layout(self):
        """
        Create a layout grid with seat labels and an aisle.
        """
        layout = []
        for row in range(self.rows):
            row_layout = []
            for col in range(self.seats_per_row):
                if col == self.aisle_col:
                    row_layout.append("AISLE")
                else:
                    seat_label = f"{row + 1}{chr(65 + (col if col < self.aisle_col else col - 1))}"
                    row_layout.append(seat_label)
            layout.append(row_layout)
        return layout

    def display_layout(self):
        """
        Print the airplane layout for debugging.
        """
        for row in self.layout:
            print(" | ".join(row))