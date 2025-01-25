from manim import *
import ast

class ColumnsAnimation(Scene):
    def read_game_data(self, file_path):
        """Reads and parses the game data file."""
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        moves = []
        for line in lines:
            if line.startswith("Ply"):
                # Extract move information
                parts = line.split(":")
                move = parts[1].strip()
                move_parts = move.split(", ")
                piece_type = move_parts[0].strip()
                columns = list(map(int, move_parts[1:]))
                moves.append((piece_type, columns))
        return moves

    def construct(self):
        # Set up the 3D board with 12 pegs (4x3 grid, 5 pieces tall)
        columns = [VGroup() for _ in range(12)]  # 12 pegs on the board
        column_positions = [
            LEFT * 2 + RIGHT * (i % 4) + UP * (i // 4) * -1
            for i in range(12)
        ]  # 4 pegs width, 3 pegs length
        for i, column in enumerate(columns):
            for j in range(5):  # 5 pieces tall
                peg = Cylinder(radius=0.1, height=0.5, direction=UP)
                peg.set_fill(GRAY, opacity=1).set_stroke(width=0.5)
                peg.move_to(column_positions[i] + UP * (j * 0.5))
                column.add(peg)

        # Add the base peg shapes to the scene
        for column in columns:
            self.play(*[Create(peg) for peg in column], run_time=1)

        # Read and parse the game data
        game_data_path = "game_data.txt"  # Replace with your actual file path
        moves = self.read_game_data(game_data_path)

        # Animating the moves
        piece_colors = {"r": YELLOW, "b": RED}  # Roundel: Yellow, Blocker: Red

        for piece_type, columns_indices in moves:
            for col_idx in columns_indices:
                # Create a new piece and stack it on the column
                piece = Sphere(radius=0.2) if piece_type == "r" else Cube(side_length=0.3)
                piece.set_fill(piece_colors[piece_type], opacity=1)
                piece.set_stroke(width=2)

                # Determine the target position on the column
                target_column = columns[col_idx]
                height = len(target_column) - 5  # Existing pegs already in column
                target_position = target_column[0].get_center() + UP * (height * 0.5)
                piece.move_to(target_position)

                # Add the piece to the column and animate it
                target_column.add(piece)
                self.play(FadeIn(piece), run_time=0.5)

        self.wait(2)

anim = ColumnsAnimation()

anim.read_game_data(".support/game_data.txt")
anim.construct()