class ColumnsGame:
    def __init__(self):
        # Initialize a 3x4 grid of 12 columns
        self.board = [[[] for _ in range(4)] for _ in range(3)]
        self.players = ["Light", "Dark"]
        self.current_player = 0
        self.pieces = {
            "Light": {"roundels": 12, "1x1x1": 3, "1x2x1": 3, "1x2x2": 3},
            "Dark": {"roundels": 12, "1x1x1": 3, "1x2x1": 3, "1x2x2": 3},
        }
        self.max_height = 6  # Maximum stack height per column

    def display_board(self):
        print("\nCurrent Board State:")
        for row in range(3):
            for col in range(4):
                column = self.board[row][col]
                print(f"({row + 1},{col + 1}): {''.join(column) if column else '[Empty]'}", end=" | ")
            print("\n")
        print("\n")

    def check_valid_move(self, row, col, piece_type):
        # Check if the selected column exists
        if not (0 <= row < 3 and 0 <= col < 4):
            return False
        column = self.board[row][col]
        if len(column) >= self.max_height:
            return False  # Column is full

        # Additional checks for larger pieces
        if piece_type == "1x2x1" and len(column) + 2 > self.max_height:
            return False
        if piece_type == "1x2x2":
            # Check adjacent columns and ensure there's space
            if col == 3 or len(column) + 2 > self.max_height or len(self.board[row][col + 1]) + 2 > self.max_height:
                return False
        return True

    def place_piece(self, row, col, piece_type, symbol):
        column = self.board[row][col]

        if piece_type == "1x1x1":
            column.append(symbol)
        elif piece_type == "1x2x1":
            column.extend([symbol] * 2)
        elif piece_type == "1x2x2":
            column.extend([symbol] * 2)
            self.board[row][col + 1].extend([symbol] * 2)

    def switch_player(self):
        self.current_player = 1 - self.current_player

    def get_winner(self):
        light_score = sum(1 for row in self.board for col in row if col and col[-1] == "L")
        dark_score = sum(1 for row in self.board for col in row if col and col[-1] == "D")
        print(f"\nFinal Scores - Light: {light_score}, Dark: {dark_score}")
        if light_score > dark_score:
            return "Light wins!"
        elif dark_score > light_score:
            return "Dark wins!"
        else:
            return "It's a tie!"

    def play(self):
        print("Welcome to the Columns Wooden Stacking Game!")
        print("Take turns placing your pieces. Use the grid coordinates (row,column) to choose a column.")
        print("Game ends when no valid moves can be made.")

        while any(piece > 0 for piece in self.pieces["Light"].values()) or \
              any(piece > 0 for piece in self.pieces["Dark"].values()):
            self.display_board()
            player_name = self.players[self.current_player]
            print(f"{player_name}'s Turn!")
            print(f"Available pieces: {self.pieces[player_name]}")

            move = input("Enter 'roundels', '1x1x1', '1x2x1', or '1x2x2': ").strip()
            if move not in self.pieces[player_name] or self.pieces[player_name][move] <= 0:
                print("Invalid move or no pieces left. Try again.")
                continue

            try:
                row, col = map(int, input("Enter row and column (e.g., 1 2): ").split())
                row -= 1
                col -= 1
                if not self.check_valid_move(row, col, move):
                    print("Invalid move: Cannot place the piece there.")
                    continue
            except ValueError:
                print("Invalid input. Please enter row and column as numbers (e.g., 1 2).")
                continue

            piece_symbol = "L" if player_name == "Light" else "D"
            self.place_piece(row, col, move, piece_symbol)
            self.pieces[player_name][move] -= 1
            self.switch_player()

        self.display_board()
        print(self.get_winner())


if __name__ == "__main__":
    game = ColumnsGame()
    game.play()
