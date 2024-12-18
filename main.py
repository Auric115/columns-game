import itertools
import neat
import numpy as np
import os
import pickle
from datetime import datetime

def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum(axis=0)

def restricted_neighbors(n):
    neighbors = [n-4, n+4, n-1, n+1]
    
    valid_neighbors = [
        neighbor for neighbor in neighbors 
        if 0 <= neighbor <= 11 and (neighbor % 4 != 0 or (n % 4 != 3 and n % 4 != 7))
    ]
    
    return valid_neighbors

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
        self.board = [Column(i) for i in range(12)]
        self.stack_height = 5
        self.players = ["Light", "Dark"]
        self.score = [0, 0]
        self.current_player = 0
        self.pieces = {
            "Light": {"roundels": 12, "blockers": 3, "d-blockers": 3, "l-blockers": 3},
            "Dark": {"roundels": 12, "blockers": 3, "d-blockers": 3, "l-blockers": 3}
        }

    def calc_score(self):
        for c in self.board:
            if (c.size() == 5):
                if (c.peek() == "Lr"):
                    self.score[0] += 1
                elif (c.peek() == "Dr"):
                    self.score[1] += 1
    
    def update_score(self, piece, col):
        if (self.board[col].size() == 5):
            if (piece == "Lr"):
                self.score[0] += 1
            elif (piece == "Dr"):
                self.score[1] += 1

    def process_move(self, move_str):
        """
        Process a single move string of format: 'r, col' or 'b, col1, col2, col3'.
        Returns 1 if the move is accepted, otherwise returns 0.
        """
        try:
            # Split move into parts
            parts = move_str.split(",")
            move_type = parts[0].strip().lower()
            cols = [int(col.strip()) - 1 for col in parts[1:]]

            # Validate input type
            if move_type not in ['r', 'b']:
                return 0

            # Check validity of column numbers
            if any(col < 0 or col > 11 for col in cols):
                return 0
            
            if any(self.board[col].size() >= 5 for col in cols):
                return 0

            # Process the move
            if move_type == 'r':  # Place a roundel
                if len(cols) != 1:
                    return 0  # Invalid input format for roundel
                return 1 if self.place_roundel(cols[0]) else 0
            elif move_type == 'b':  # Place a blocker
                if len(cols) not in [1, 2, 3]:
                    return 0  # Invalid input format for blockers
                return 1 if self.place_blocker(cols) else 0

        except (ValueError, IndexError):
            return 0  # Invalid format or out-of-range values

    def place_roundel(self, col):
        if self.pieces[self.players[self.current_player]]["roundels"] < 1:
            return 0  # Out of roundels
        piece = "Dr" if self.current_player else "Lr"
        blocker = "Lb" if self.current_player else "Db"
        if self.board[col].peek() == blocker:
            return 0  # Column is blocked
        self.board[col].push(piece)
        self.pieces[self.players[self.current_player]]["roundels"] -= 1
        self.update_score(piece, col)
        return 1

    def place_blocker(self, cols):
        if len(cols) == 1:
            piece_type = "blockers"

        elif len(cols) == 2:
            piece_type = "d-blockers"

            if cols[0] == cols[1]:
                return 0 #Invalid columns for d-blocker

            if self.board[cols[0]].size() != self.board[cols[1]].size():
                return 0 #Invalid columns for d-blocker
            
            if cols[0] not in restricted_neighbors(cols[1]):
                return 0 #Non adjacent columns
            
        elif len(cols) == 3:
            piece_type = "l-blockers"
            sizes = [self.board[col].size() for col in cols]

            # Check if the total column heights are within allowable limits
            if sum(sizes) >= 11:
                return 0  # Combined stack height exceeds allowed limit

            # Validate if columns form 2-stacked with 1 adjacent configuration
            if not ( #FUTURE BJ: remove same column checker for actual implementation... should not be required with a C3 0, 1, 2 value as output representation
                (cols[0] == cols[1] and cols[0] in restricted_neighbors(cols[2]) and ((sizes[2] - sizes[0]) == 0 or (sizes[2] - sizes[0]) == 1)) or
                (cols[1] == cols[2] and cols[1] in restricted_neighbors(cols[0]) and ((sizes[0] - sizes[1]) == 0 or (sizes[0] - sizes[1]) == 1)) or
                (cols[2] == cols[0] and cols[2] in restricted_neighbors(cols[1]) and ((sizes[1] - sizes[2]) == 0 or (sizes[1] - sizes[2]) == 1))
            ):
                return 0  # Invalid column arrangement for triple-blockers
            
        else:
            return 0  # Invalid blocker type

        if self.pieces[self.players[self.current_player]][piece_type] < 1:
            return 0  # Out of blockers
        piece = "Db" if self.current_player else "Lb"
        for col in cols:
            self.board[col].push(piece)
        self.pieces[self.players[self.current_player]][piece_type] -= 1

        # print(f"{self.pieces[self.players[self.current_player]]} {piece_type}")
        # print(self.pieces[self.players[self.current_player]][piece_type])

        return 1

    def display_board(self):
        print("\n______ ______ ______ ______ ~|~ ______ |COLUMN GAME| ______ ~|~ ______ ______ ______ ______")
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
        print("")  # Add spacing for readability

    def append_board(self, file):
        with open(file, "a") as log_file:  # Open the file in append mode
            log_file.write("\n______ ______ ______ ______ ~|~ ______ |COLUMN GAME| ______ ~|~ ______ ______ ______ ______\n")
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
                log_file.write(" ".join(row) + "\n")  # Write each row to the file
            log_file.write("\n")  # Add spacing for readability

    def run(self):
        while True:
            self.display_board()
            print(f"{self.players[self.current_player]}'s Turn")
            print(self.pieces[self.players[self.current_player]])

            # Get move string from AI (simulate input)
            move = input("Enter move as 'r, col' or 'b, col1, col2, col3': ").strip()

            # Process the move
            feedback = self.process_move(move)
            print(f"Feedback: {'Accepted' if feedback else 'Invalid'}")

            # If move is accepted, switch players
            if feedback == 1:
                self.current_player ^= 1

class AiEngine:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.config_file
        )
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.population.add_reporter(self.stats)

        self.generation = 0

    def next_nearest_move(self, move):
        """
        Finds the move in moves.txt and returns an array of moves radiating out
        from the found move's position.

        Args:
            move (str): The move string to find, e.g., "r, 5".

        Returns:
            list: A list of moves radiating out from the found move.
        """
        # Read all moves from moves.txt
        with open("moves.txt", "r") as file:
            all_moves = [line.strip() for line in file.readlines()]
        
        # Find the index of the given move
        if move not in all_moves:
            raise ValueError(f"Move '{move}' not found in moves.txt.")
        
        move_index = all_moves.index(move)
        nearest_moves = [move]  # Start with the given move
        
        # Alternating above and below indices
        offset = 1
        while True:
            added_any = False  # Track if we added any moves this iteration

            # Check move above
            if move_index - offset >= 0:
                nearest_moves.append(all_moves[move_index - offset])
                added_any = True

            # Check move below
            if move_index + offset < len(all_moves):
                nearest_moves.append(all_moves[move_index + offset])
                added_any = True

            # Break if no moves are added (bounds reached)
            if not added_any:
                break
            
            offset += 1  # Increment offset for the next iteration

        return nearest_moves

    def encode_state(self, game):
        """
        Encodes the game state into a 68-input array for the NEAT network.
        """
        input_data = []

        # Encode board (12 columns, 5 rows per column)
        for column in game.board:
            for level in range(game.stack_height):
                if level < len(column.stack):
                    piece = column.stack[level]
                    if piece == "Lr":
                        input_data.append(1)
                    elif piece == "Lb":
                        input_data.append(2)
                    elif piece == "Dr":
                        input_data.append(3)
                    elif piece == "Db":
                        input_data.append(4)
                else:
                    input_data.append(0)

        # Encode unplaced pieces
        for player in game.players:
            input_data.append(game.pieces[player]["roundels"])
            input_data.append(game.pieces[player]["blockers"])
            input_data.append(game.pieces[player]["d-blockers"])
            input_data.append(game.pieces[player]["l-blockers"])

        return np.array(input_data)

    def decode_output(self, output):
        """
        Decodes the NEAT network's output into a game move based on the highest-probability softmax output.
        
        Args:
            output: The raw output array of 75 values from the NEAT network.
            
        Returns:
            The corresponding move string from moves.txt.
        """
        # Apply softmax to the output
        probabilities = softmax(output)
        
        # Find the index of the highest probability
        move_index = np.argmax(probabilities)
        
        # Read the move string from moves.txt at the corresponding line
        with open("moves.txt", "r") as file:
            moves = file.readlines()
            if 0 <= move_index < len(moves):
                move_str = moves[move_index].strip()  # Strip to remove newlines
            else:
                raise ValueError(f"Invalid move index {move_index}. Ensure moves.txt has enough entries.")
        
        return move_str

    def write_generation_report(self, genomes, generation, results):
        """
        Writes a report of the current generation's genome performance.
        """
        os.makedirs("reports/", exist_ok=True)
        filename = f"reports/generation_{generation}.txt"

        with open(filename, "w") as report:
            report.write(f"GENERATION {generation}\n\n")
            report.write("Genome ID | Fitness | Invalid | Wins | Draws | Losses\n")
            report.write("-" * 50 + "\n")

            for genome_id, data in results.items():
                report.write(
                    f"{genome_id:9} | {data['fitness']:5.3f} | {data['invalid_moves']:9} | {data['wins']:9} | {data['draws']:9} | {data['losses']:9}\n"
                )
    
    def save_genome(self, genome, genome_id, generation):
        """
        Saves a genome to a file for later use.
        """
        os.makedirs(f"genomes/generation_{generation}/", exist_ok=True)
        filename = f"genomes/generation_{generation}/genome_{genome_id}.pkl"

        with open(filename, "wb") as genome_file:
            pickle.dump(genome, genome_file)
    
    def log_game(self, generation, game_number, genome1, genome2, log_data):
        """
        Logs the details of a single game.
        """
        os.makedirs(f"reports/generation_{generation}/", exist_ok=True)
        filename = f"reports/generation_{generation}/g{game_number} ({genome1.key},{genome2.key}).txt"

        with open(filename, "w") as log:
            log.write(f"GENERATION {generation}\n")
            log.write(f"GAME {game_number} - {genome1.key} vs {genome2.key}\n\n")
            for ply, ply_data in enumerate(log_data["moves"], start=1):
                log.write(
                    f"Ply {ply} ({ply_data['invalid']}, {ply_data['alt_moves']}): {ply_data['move']}\n"
                )
            log.write("\n")
            log.write(f"Game Over. {log_data['result']}.\n")
            log.write(f"\t Light: {log_data['light']} ({log_data['fitness_1']}).\n")
            log.write(f"\t Dark: {log_data['dark']} ({log_data['fitness_2']}).\n")

            log.write("\n______ ______ ______ ______ ~|~ ______ |COLUMN GAME| ______ ~|~ ______ ______ ______ ______\n")
            for level in reversed(range(log_data['game'].stack_height)):
                row = []
                for col_index, column in enumerate(log_data['game'].board):
                    if level < len(column.stack):
                        cell_content = column.stack[level]
                    else:
                        cell_content = "--"
                    row.append(f"[ {cell_content:^3}]")
                    if (col_index + 1) % 4 == 0 and col_index != 11:
                        row.append("~|~")
                log.write(" ".join(row) + "\n")  # Write each row to the file
            log.write("\n")  # Add spacing for readability

    def play_game(self, genome1, net1, genome2, net2, generation, game_number, log_data):
        """
        Plays a single game and logs details.
        """
        game = ColumnsGame()
        current_nets = [net1, net2]
        current_genomes = [genome1, genome2]
        invalid_moves = [0, 0]
        fits = [0, 0]
        turn = 0
        last_move_pass = 0

        with open("log.txt", 'a') as log:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{current_time}] Game #: {game_number}\n")

            while True:
                current_player = game.current_player
                net = current_nets[current_player]
                genome = current_genomes[current_player]

                # Encode game state and get AI's move
                inputs = self.encode_state(game)
                output = net.activate(inputs)

                move_str = self.decode_output(output)

                # Process the move
                valid_move = game.process_move(move_str)
                alt_moves = 0

                if valid_move:
                    fits[current_player] += 0.10
                else:
                    fits[current_player] -= 0.10  # Penalize invalid moves
                    invalid_moves[current_player] += 1

                    # Try alternative moves
                    alts = self.next_nearest_move(move_str)
                    for a in alts:
                        move_str = a
                        res = game.process_move(move_str)
                        alt_moves += 1
                        if res:
                            break
                        else: 
                            move_str = "Pass"
                        fits[current_player] -= 0.001  # Penalize further invalid moves

                log_data["moves"].append({
                    "move": move_str,
                    "invalid": int(not valid_move),
                    "alt_moves": alt_moves,
                })

                log.write(f"\t{turn} ({int(not valid_move)}, {alt_moves}): {move_str}\n")

                if move_str == "Pass":
                    if last_move_pass:
                        break
                    else:
                        last_move_pass = 1
                else:
                    last_move_pass = 0

                if all(value == 0 for value in game.pieces[game.players[game.current_player]].values()):
                    break

                game.current_player ^= 1
                turn += 1

                if turn >= 100:
                    break

        isDraw = False

        # Determine game results
        light_score, dark_score = game.score
        if light_score > dark_score:
            winner = genome1
            loser = genome2
            fits[0] += 1
            fits[1] += 0
        elif light_score < dark_score:
            winner = genome2
            loser = genome1
            fits[0] += 0
            fits[1] += 1
        else:
            isDraw = True
            winner = genome1
            loser = genome2
            fits[0] += 0.5
            fits[1] += 0.5
            
        genome1.fitness += fits[0]
        genome2.fitness += fits[1]

        # Record final game details
        log_data.update({
            "generation": generation,
            "game_number": game_number,
            "result": "Draw" if isDraw else "Light Won" if winner == genome1 else "Dark Won",
            "winner": winner.key,
            "loser": loser.key,
            "light": genome1.key,
            "dark": genome2.key,
            "fitness_1": fits[0],
            "fitness_2": fits[1],
            "invalid_moves_1": invalid_moves[0],
            "invalid_moves_2": invalid_moves[1],
            "game": game
        })

        return log_data

    def evaluate_genomes(self, genomes, config):
        results = {
            genome_id: {"fitness": 0, "invalid_moves": 0, "wins": 0, "draws": 0, "losses": 0} for genome_id, _ in genomes
        }

        for genome_id, genome in genomes:
            genome.fitness = 0  # Reset fitness
        
        with open("log.txt", 'a') as log:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"\n[{current_time}] GENERATION: {self.generation} ##### ##### ##### ##### #####\n\n")

        j = 0
        for i, (genome_id1, genome1) in enumerate(genomes):
            for genome_id2, genome2 in genomes[i + 1:]:
                net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
                net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

                game_log = {"moves": []}
                result = self.play_game(
                    genome1,
                    net1,
                    genome2,
                    net2,
                    generation=self.generation,
                    game_number= j,
                    log_data=game_log,
                )

                # Update results
                if result["result"] == "Light Won":
                    results[genome_id1]["wins"] += 1
                    results[genome_id2]["losses"] += 1
                elif result["result"] == "Dark Won":
                    results[genome_id2]["wins"] += 1
                    results[genome_id1]["losses"] += 1
                else:
                    results[genome_id1]["draws"] += 1
                    results[genome_id2]["draws"] += 1

                results[genome_id1]["fitness"] += result["fitness_1"]
                results[genome_id2]["fitness"] += result["fitness_2"]

                results[genome_id1]["invalid_moves"] += result["invalid_moves_1"]
                results[genome_id2]["invalid_moves"] += result["invalid_moves_2"]

                # Log the game details
                self.log_game(self.generation, j, genome1, genome2, game_log)
                j += 1


        # Write the generation report
        self.write_generation_report(genomes, self.generation, results)

        # Save genomes for later use
        for genome_id, genome in genomes:
            self.save_genome(genome, genome_id, self.generation)
        
        self.generation += 1
    
    def train(self, generations=25):
        """
        Trains the population over the specified number of generations.
        """
        winner = self.population.run(self.evaluate_genomes, generations)
        print("\nBest genome:\n", winner)

    def play(self, game):
        """
        Plays a single game using the best-trained genome.
        """
        # Load the best genome
        best_genome = self.population.best_genome()
        net = neat.nn.FeedForwardNetwork.create(best_genome, self.config)

        while True:
            # Display the board
            game.display_board()

            # Encode the current game state
            inputs = self.encode_state(game)

            # Get the network's output
            output = net.activate(inputs)

            # Decode the output into a move
            move_str = self.decode_output(output)
            print(f"AI Move: {move_str}")

            # Process the move
            if not game.process_move(move_str):
                print("Invalid move by AI.")
                break

            # Check if the game has ended
            if all(value == 0 for value in game.pieces[game.players[game.current_player]].values()):
                print("Game Over.")
                break

def main():
    ai = AiEngine('C:\\Users\\brayd\\Builds\\Games\\columns-game\\config_file.txt')
    ai.train(generations=100)

if __name__ == '__main__':
    main()