def restricted_neighbors(n):   
    return [x for x in [n-4, n-1, n+1, n+4] if 0 <= x <= 11]

class Column:
    def __init__(self, column_num):
        self.num = column_num
        self.neighbors = restricted_neighbors(self.num)

        self.stack = [] * 5
    
    def size(self):
        return len(self.stack)

    def is_empty(self):
        return len(self.stack) == 0
    
    def push(self, piece):
        self.stack.append(piece)
    
    def peek(self):
        if self.is_empty():
            return ""
        return self.stack[-1]

class ColumnsGame:
    def __init__(self):
        self.board = []
        for i in range(0,12):
            col = Column(i)
            self.board.append(col)

        self.stack_height = 5

        self.players = ["Light", "Dark"]
        self.current_player = 0
        self.pieces = {
            "Light": {"roundels": 12, "blockers": 3, "d-blockers": 3, "l-blockers": 3},
            "Dark": {"roundels": 12, "blockers": 3, "d-blockers": 3, "l-blockers": 3}
        }
    
    def place_roundel(self, col):
        if (self.pieces[self.players[self.current_player]]["roundels"] < 1):
            print("You are out of roundels.")
            return 1
        
        piece = ""
        blocker = ""
        if (self.current_player):
            piece = "Dr"
            blocker = "Lb"
        else:
            piece = "Lr"
            blocker = "Db"
        
        if (self.board[col].peek() == blocker):
            print("That column is blocked!")
            return 1
            
        self.board[col].push(piece)
        self.pieces[self.players[self.current_player]]["roundels"] -= 1
        return 0

    def place_blocker(self, cols):
        if len(cols) == 1:
            piece_type = "blockers"
        elif len(cols) == 2:
            piece_type = "d-blockers"
        elif len(cols) == 3:
            piece_type = "l-blockers"
        if (self.pieces[self.players[self.current_player]][piece_type] < 1):
            print(f"You are out of {piece_type}.")
            return 1
        
        piece = ""
        if (self.current_player):
            piece = "Db"
        else:
            piece = "Lb"
        
        for col in cols:
            self.board[col].push(piece)
        self.pieces[self.players[self.current_player]][piece_type] -= 1
        return 0
    
    def ask_columns(self):
        while True:
            input_cols = input("Enter 1, 2, or 3 columns (space-separated, 1-12): ").strip()

            cols = input_cols.split()

            if len(cols) not in [1, 2, 3]:
                print("Invalid input! Please enter 1, 2, or 3 columns.")
                continue

            try:
                cols = [int(col) - 1 for col in cols]
                if any(col < 0 or col > 11 for col in cols):
                    raise ValueError
            except ValueError:
                print("Invalid input! Please enter integer values between 1 and 12.")
                continue

            if any(self.board[col].size() == 5 for col in cols):
                print("One or more columns are full! Please choose different columns.")
                continue

            if len(cols) == 1:
                break
            sizes = [self.board[col].size() for col in cols]
            if len(cols) == 2:
                if sizes[0] == sizes[1]:
                    break
            elif len(cols) == 3:
                # checks if columns are 2 stacked with 1 adjacent
                if (cols[0] == cols[1] and cols[0] in restricted_neighbors(cols[2])) or (cols[1] == cols[2] and cols[1] in restricted_neighbors(cols[0])) or (cols[2] == cols[0] and cols[2] in restricted_neighbors(cols[1])):
                    # checks columns aren't too high
                    if sum(sizes) < 11:
                        #checks columns sizes are within 1 of each other 
                        if all(abs(sizes[i] - sizes[j]) <= 1 for i in range(3) for j in range(i + 1, 3)):
                            break
            print("Invalid column selection.")
            continue

        return cols

    def display_board(self):
        print("")
        print("______ ______ ______ ______ ~|~ ______ |COLUMN GAME| ______ ~|~ ______ ______ ______ ______")
        for level in reversed(range(self.stack_height)):
            row = []
            for col_index, column in enumerate(self.board):
                if level < len(column.stack):
                    cell_content = column.stack[level]
                else:
                    cell_content = "--"

                row.append(f"[ {cell_content:^3}]")

                if (col_index + 1) % 4 == 0 and col_index != 11:
                    row.append("~|~")

            print(" ".join(row))

    def run(self):
        while True:
            print("")
            print(f"{self.players[self.current_player]}'s Turn")
            print(self.pieces[self.players[self.current_player]])
            while True: # get piece input
                piece = input("Do you want a roundel (r/R) or a blocker (b/B): ").strip().lower()
                if piece == 'q':
                    piece = input("Are you sure you want to quit (y/n): ").strip().lower()
                    if piece == 'y':
                        break
                    else:
                        continue

                if piece not in ['r', 'b']:
                    print("Invalid input! Please enter 'r' or 'R' for a roundel, or 'b' or 'B' for a blocker.")
                    continue
                break
            
            if piece == 'y':
                break
            elif piece == 'r':
                cols = self.ask_columns()
                if (len(cols) != 1):
                    print("Roundels can be played in only 1 column.")
                    continue
                if self.place_roundel(cols[0]):
                    continue
            elif piece == 'b':
                cols = self.ask_columns()
                if self.place_blocker(cols):
                    continue
            
            self.current_player = self.current_player ^ 1
            self.display_board()

def main():
    game = ColumnsGame()
    game.display_board()
    game.run()


if __name__ == '__main__':
    main()