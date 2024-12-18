import itertools

def binary_to_num(bits):
    return sum(bit * (2 ** idx) for idx, bit in enumerate(reversed(bits)))

def restricted_neighbors(n):   
    neighbors = [n-4, n+4, n-1, n+1]
    
    valid_neighbors = [
        neighbor for neighbor in neighbors 
        if 0 <= neighbor <= 11 and (neighbor % 4 != 0 or (n % 4 != 3 and n % 4 != 7))
    ]
    
    return valid_neighbors



all_moves = []

# Generate all possible candidate moves
for candidate in itertools.product(
    [0, 1],  # 0 or 1 for r (roundel) or b (blocker)
    [0, 1], [0, 1],  # 00: 1 column, 01: 2 columns, 10 or 11: 3 columns copying C1 or C2 respectively
    [0, 1], [0, 1], [0, 1], [0, 1],  # Column 1
    [0, 1], [0, 1], [0, 1], [0, 1],  # Column 2
):
    # Skip invalid combinations
    if candidate[0] == 0 and (candidate[1] == 1 or candidate[2] == 1):
        continue                                    # Roundels only have 1 candidate move
    if candidate[0] == 0 and any(candidate[7:11]):  # candidate[7:11] checks Column 2
        continue                                    # Roundels don't use Column 2
    if candidate[0] == 1 and all(c == 0 for c in candidate[1:3]) and any(candidate[7:11]):
        continue                                    # Single blockers don't use Column 2 if columns are inactive
    if candidate[3] == 1 and candidate[4] == 1:
        continue                                    # Column 1 ranges from 0 to 11
    if candidate[7] == 1 and candidate[8] == 1:
        continue                                    # Column 2 ranges from 0 to 11                              # Column 1 and 2 are different
    
    if any(candidate[1:3]):
        # Convert Column 1 and Column 2 to their numerical values
        col1_val = binary_to_num(candidate[3:7])
        col2_val = binary_to_num(candidate[7:11])

        # Ensure Column 2 is a restricted neighbor of Column 1
        if col2_val not in restricted_neighbors(col1_val):
            continue  # Skip if Column 2 is not a restricted neighbor of Column 1
        if col2_val <= col1_val:
            continue

        # Add valid candidate moves to the list
    all_moves.append(candidate)

# Decode output function
def decode_output(output):
    """
    Decodes the NEAT network's output into a game move based on the new representation.
    Output structure:
    - [0]: Binary (0 = roundel, 1 = blocker)
    - [1-2]: Column type (00 = one column, 01 = two columns, 10 = three columns copying col1, 11 = three columns copying col2)
    - [3-6]: Column 1 (binary 0-11)
    - [7-10]: Column 2 (binary 0-11, always 0000 for roundel)
    """
    # Move type: 'r' or 'b'
    move_type = 'r' if round(output[0]) == 0 else 'b'
    
    col_type = 0
    # Decode column type (neurons 1-2)
    col_type_bits = (round(output[1]), round(output[2]))
    if col_type_bits == (0, 0):
        col_type = 1  # One column
    elif col_type_bits == (0, 1):
        col_type = 2  # Two columns
    elif col_type_bits == (1, 0):
        col_type = 3  # Three columns, col3 copies col1
    elif col_type_bits == (1, 1):
        col_type = 3  # Three columns, col3 copies col2
    
    # Decode column 1 (neurons 3-6)
    col1 = int("".join(map(str, map(round, output[3:7]))), 2)
    
    # Decode column 2 (neurons 7-10)
    col2 = int("".join(map(str, map(round, output[7:11]))), 2) if col_type >= 2 else None
    
    # Construct move string
    move_str = f"{move_type}, {col1}"
    if col_type >= 2:
        move_str += f", {col2}"
    if col_type == 3:
        col3 = col1 if col_type_bits == (1, 0) else col2
        move_str += f", {col3}"

    return move_str

# Write all valid moves to a file
with open(".support/bin_moves.txt", 'w') as moves_file:
    for move in all_moves:
        #string = decode_output(move)
        for m in move:
            moves_file.write(str(m))
        moves_file.write('\n')
