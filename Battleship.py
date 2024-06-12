import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colors
from matplotlib.patches import Rectangle
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox as messagebox
from tkinter import simpledialog

# Global variables to hold the game state
player_board = None
ai_board = None
player_hits = None
player_misses = None
ai_hits = None
ai_misses = None
turn_counter = 0
player_successful_hits = 0
ai_successful_hits = 0
player_turn = True  # Track whose turn it is
game_over = False   # Track if the game is over
starting_player = "Player"  # Track the starting player, default is Player

# Ship lengths for each type of ship
ship_lengths = {'P': 5, 'C': 4, 'S': 3, 'L': 2}
ship_names = {'P': 'Portaaviones', 'C': 'Crucero', 'S': 'Submarino', 'L': 'Lancha torpedera'}

# Initialize empty dictionaries to store ship locations and types
player_ships = {}
ai_ships = {}

# Initialize hit counters
player_hit_counters = {ship_type: 0 for ship_type in ship_lengths}
ai_hit_counters = {ship_type: 0 for ship_type in ship_lengths}

# Add a global variable to store which ships have been sunk
sunk_ships = set()

#------------------------------------------------------------
def print_board_preview(board):
    """Print a preview of the board with ships."""
    for row in board:
        row_str = ' '.join(map(str, row))
        print(row_str.replace('0', '.').replace('1', 'X'))  # Replace 0 with '.' and 1 with 'X'

def manually_place_ships_gui():
    ships = ['P', 'C', 'S', 'L']
    
    root = tk.Tk()
    root.title("Colocación Manual de Barcos")
    root.geometry("500x600")  # Set a larger size for the window

    # Initialize an empty board
    board = np.zeros((10, 10), dtype=int)

    # Instructions label
    instructions = (
        "Instrucciones:\n"
        "Ingrese las coordenadas en el formato: fila, columna, orientación\n"
        "Ejemplo: 3, 4, horizontal\n"
        "Los valores de fila y columna deben estar entre 1 y 10.\n"
        "La orientación debe ser 'horizontal' o 'vertical'."
    )
    label = tk.Label(root, text=instructions, wraplength=450, justify="left")
    label.pack(pady=10)
    
    
    
    # Initialize a dictionary to track placed ships
    placed_ships = {ship: False for ship in ships}

    # Function to handle manual ship placement
    def place_ship(ship_type, length):
        nonlocal board, ships
        while True:
            # Prompt the player for ship placement
            prompt = f"Ingresa las coordinadas para {ship_names[ship_type]} (tamaño: {length}):"
            coordinates = simpledialog.askstring("Colocación Manual de Barcos", prompt)
            if coordinates is None:  # If the player cancels, return None
                root.destroy()
                return None
            try:
                length_of_the_ship = ship_lengths[ship_type]
                row, col, orientation = map(str.strip, coordinates.split(','))
                row, col = int(row) - 1, int(col) - 1
                if not (0 <= row <= 9 and 0 <= col <= 9):
                    raise ValueError("La fila y la columna deben estar entre 1 y 10.")
                if orientation not in ['horizontal', 'vertical']:
                    raise ValueError("Orientación inválida. Por favor, ingrese 'horizontal' o 'vertical'.")
                if orientation == 'horizontal':
                    if col + length > 10:
                        raise ValueError("La colocación del barco está fuera de los límites.")
                    for i in range(length):
                        if board[row][col + i] != 0:
                            raise ValueError("La colocación del barco se superpone con un barco existente.")
                    for i in range(length):
                        board[row][col + i] = 1
                        player_ships[ship_type] = [(row, col + i) for i in range(length_of_the_ship)]
                else:
                    if row + length > 10:
                        raise ValueError("La colocación del barco está fuera de los límites.")
                    for i in range(length):
                        if board[row + i][col] != 0:
                            raise ValueError("La colocación del barco se superpone con un barco existente.")
                    for i in range(length):
                        board[row + i][col] = 1
                        player_ships[ship_type] = [(row + i, col) for i in range(length_of_the_ship)]
                placed_ships[ship_type] = True
                #player_ships[ship_type] = [(row, col + i) for i in range(length_of_the_ship)]
                break
            except (ValueError, IndexError) as e:
                tk.messagebox.showerror("Error", f"Entrada inválida: {e}. Por favor, inténtelo de nuevo.")
        print(f"Vista previa después de colocar {ship_names[ship_type]}:")
        print_board_preview(board)
        check_all_ships_placed()
    
    # Function to check if all ships have been placed and enable the confirm button
    def check_all_ships_placed():
        if all(placed_ships.values()):
            confirm_btn.config(state=tk.NORMAL)

    # Create buttons for each ship type
    for ship_type, length in ship_lengths.items():
        btn = tk.Button(root, text=f"Coloca {ship_names[ship_type]}", command=lambda st=ship_type, l=length: place_ship(st, l), font=("Arial", 14), padx=10, pady=10, width=20, height=2)
        btn.pack(pady=5)
    
    # Confirmation button to return the updated board
    confirm_btn = tk.Button(root, text="Confirmar Colocación", command=root.destroy, font=("Arial", 14), padx=10, pady=10, width=20, height=2, state=tk.DISABLED)
    confirm_btn.pack(pady=20)
    
    root.mainloop()
    
    # Return the updated player board after manual ship placement
    return board
#---------------------------------------

def generateRandomBoard(user):
    board = np.full((10, 10), 0)
    ships = ['P', 'C', 'S', 'L']

    for ship_type in ships:
        length_of_the_ship = ship_lengths[ship_type]
        placed = False
        while not placed:
            col_or_row = random.randint(0, 1)
            
            if col_or_row == 1:  # row
                random_row = random.randint(0, 9)
                random_col = random.randint(0, 9 - length_of_the_ship)  # Adjusted to ensure ship fits within board
                if np.all(board[random_row, random_col:random_col + length_of_the_ship] == 0):
                    board[random_row, random_col:random_col + length_of_the_ship] = 1
                    placed = True
                    if user == 2:
                        # Store ship location and type for Player
                        player_ships[ship_type] = [(random_row, random_col + i) for i in range(length_of_the_ship)]
                    if user == 1:
                        # Store ship location and type for AI
                        ai_ships[ship_type] = [(random_row, random_col + i) for i in range(length_of_the_ship)]

            else:  # col
                random_col = random.randint(0, 9)
                random_row = random.randint(0, 9 - length_of_the_ship)  # Adjusted to ensure ship fits within board
                if np.all(board[random_row:random_row + length_of_the_ship, random_col] == 0):
                    board[random_row:random_row + length_of_the_ship, random_col] = 1
                    placed = True
                    if user == 2:
                        # Store ship location and type for Player
                        player_ships[ship_type] = [(random_row + i, random_col) for i in range(length_of_the_ship)]
                    if user == 1:
                        # Store ship location and type for AI
                        ai_ships[ship_type] = [(random_row + i, random_col) for i in range(length_of_the_ship)]

    return board

def possibleLocationsProbability(board_with_hits, board_with_misses, length_of_the_ship):
    list_of_probabilities = []
    
    for row in range(10):
        for col in range(11 - length_of_the_ship):
            positions_to_consider = range(col, col + length_of_the_ship)
            positions_with_hits = [element for element in positions_to_consider if board_with_hits[row, element] == 1]
            if np.all(board_with_misses[row, col:col + length_of_the_ship] == 0):
                new_state = np.full((10, 10), 0.0)
                if_there_is_hit = 4 * len(positions_with_hits) if positions_with_hits else 1
                for element in positions_to_consider:
                    new_state[row, element] = float(length_of_the_ship) * if_there_is_hit if element not in positions_with_hits else 0
                list_of_probabilities.append(new_state)

    for col in range(10):
        for row in range(11 - length_of_the_ship):
            positions_to_consider = range(row, row + length_of_the_ship)
            positions_with_hits = [element for element in positions_to_consider if board_with_hits[element, col] == 1]
            if np.all(board_with_misses[row:row + length_of_the_ship, col] == 0):
                new_state = np.full((10, 10), 0.0)
                if_there_is_hit = 4 * len(positions_with_hits) if positions_with_hits else 1
                for element in positions_to_consider:
                    new_state[element, col] = float(length_of_the_ship) * if_there_is_hit if element not in positions_with_hits else 0
                list_of_probabilities.append(new_state)

    final_matrix = np.sum(list_of_probabilities, axis=0)
    return final_matrix

def generateProbabilitiesForAllShips(board_with_hits, board_with_misses):
    final = np.full((10, 10), 0.0)
    ships = ['P', 'C', 'S', 'L']
    for ship_type in ships:
        length_of_the_ship = ship_lengths[ship_type]
        probabilities = possibleLocationsProbability(board_with_hits, board_with_misses, length_of_the_ship)
        final = np.add(final, probabilities)
    return final

def generateNextMove(board_with_probabilities):
    return np.unravel_index(board_with_probabilities.argmax(), board_with_probabilities.shape)

def record_attempt(player_turn, row, col, hit):
    with open("control.txt", "a") as file:
        if player_turn:
            player = "Player"
        else:
            player = "AI"
        row_letter = chr(65 + row)  # Convert row number to letter (A-J)
        col_number = col + 1  # Adjust column from 0-indexed to 1-indexed
        file.write(f"{player}: {'Tocado' if hit else 'Agua'} at ({row_letter}, {col_number})\n")

def ai_turn():
    global ai_hits, ai_misses, player_board, ai_successful_hits

    board_with_probabilities = generateProbabilitiesForAllShips(ai_hits, ai_misses)
    next_hit = generateNextMove(board_with_probabilities)
    row, col = next_hit

    if player_board[row, col] == 1:
        ai_successful_hits += 1
        ai_hits[row, col] = 1
        ship_type = get_ship_type(row, col)
        if ship_type is not None:
            update_message(f"{ship_names[ship_type]} Jugador tocado!")
            update_ai_moves(f"AI: Tocado at ({chr(row + 65)}, {col + 1})")
            record_attempt(False, row, col, True)  # Record AI's hit
            player_board[row, col] = 2  # Mark as hit ship segment
            ai_hit_counters[ship_type] += 1
            if ai_hit_counters[ship_type] == ship_lengths[ship_type]:
                update_message(f"{ship_names[ship_type]} Jugador Hundido!")
    else:
        ai_misses[row, col] = 2
        update_ai_moves(f"AI: Agua ({chr(row + 65)}, {col + 1})")
        record_attempt(False, row, col, False)  # Record AI's miss

def choose_starter():
    global starting_player
    choice = messagebox.askyesno("Choose Starter", "Do you want to start the game as Player?")
    if choice:
        starting_player = "Player"
    else:
        starting_player = "AI"
    messagebox.showinfo("Starter Chosen", f"{starting_player} starts the game!")
    initialize_game()

def initialize_game():
    global ai_board, player_board, player_hits, player_misses, ai_hits, ai_misses
    if starting_player == "AI":
        ai_turn()
    update_boards()
    
def get_ship_type(row, col, is_player=True):
    ships = player_ships if is_player else ai_ships
    for ship_type, locations in ships.items():
        if (row, col) in locations:
            return ship_type
    return None

def update_message(message):
    message_box.configure(state=tk.NORMAL)
    message_box.insert(tk.END, message + "\n")
    message_box.see(tk.END)  # Scroll to the end
    message_box.configure(state=tk.DISABLED)

def update_ai_moves(message):
    ai_moves_box.configure(state=tk.NORMAL)
    ai_moves_box.insert(tk.END, message + "\n")
    ai_moves_box.see(tk.END)  # Scroll to the end
    ai_moves_box.configure(state=tk.DISABLED)

    
    
def on_click(event):
    global player_hits, player_misses, ai_board, ai_hits, player_successful_hits, player_turn, turn_counter, game_over

    if game_over:
        return

    if player_turn:
        y, x = int(event.ydata), int(event.xdata)
        # Check if the selected location has already been hit or missed by the player
        if player_hits[y, x] == 1 or player_misses[y, x] == 2:
            update_message("Invalid move! You have already selected this location. Please choose another location.")
            return  # Do not proceed further

        if ai_board[y, x] == 1:
            player_successful_hits += 1
            player_hits[y, x] = 1  # Mark the tile as hit
            ship_type = get_ship_type(y, x, is_player=False)
            if ship_type is not None:
                update_message(f"{ship_names[ship_type]} AI Tocado!")
                player_hit_counters[ship_type] += 1
                if player_hit_counters[ship_type] == ship_lengths[ship_type]:
                    update_message(f"{ship_names[ship_type]} AI Hundido!")
        else:
            player_misses[y, x] = 2
            update_message("Jugador: Agua")

        player_turn = False
        turn_counter += 1
        update_boards()

        if player_successful_hits >= 14:  # Adjusted for ship lengths
            update_message("Jugador gana!")
            game_over = True
            update_boards()  # Update boards to display winner
            return

        # Call record_attempt for player's move
        record_attempt(True, y, x, player_hits[y, x] == 1)

        ai_turn()
        if ai_successful_hits >= 14:  # Adjusted for ship lengths
            update_message("AI wins!")
            game_over = True
            update_boards()  # Update boards to display winner
            return

        player_turn = True
        update_boards()

        # Call record_attempt for AI's move
        ai_row, ai_col = np.unravel_index(board_with_probabilities.argmax(), board_with_probabilities.shape)
        record_attempt(False, ai_row, ai_col, player_board[ai_row, ai_col] == 1)


def update_boards():
    global ax1, ax2, player_hits, player_misses, ai_hits, ai_misses, player_board, ai_board, turn_counter, game_over

    ax1.clear()
    ax2.clear()

    cmap = colors.ListedColormap(['lightgrey', 'red', 'blue'])
    bounds = [-1, 0.5, 1.5, 2.5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    player_combined = ai_hits + ai_misses
    ai_combined = player_hits + player_misses

    sns.heatmap(player_combined, linewidth=0.5, cmap=cmap, cbar=False, norm=norm, ax=ax1, square=True)
    sns.heatmap(ai_combined, linewidth=0.5, cmap=cmap, cbar=False, norm=norm, ax=ax2, square=True)

    ax1.set_title("Player's Board")
    ax2.set_title("AI's Board")

    for ship_type, ship_locations in ai_ships.items():
        for location in ship_locations:
            row, col = location
            if 0 <= row < 10 and 0 <= col < 10:
                if player_hits[row, col] == 1:
                    color = 'red'
                elif player_misses[row, col] == 2:
                    color = 'blue'

    for ship_type, ship_locations in player_ships.items():
        for location in ship_locations:
            row, col = location
            if 0 <= row < 10 and 0 <= col < 10:
                if ai_hits[row, col] == 1:
                    color = 'red'
                elif ai_misses[row, col] == 2:
                    color = 'blue'
                else:
                    color = 'black'
                ax1.add_patch(Rectangle((col, row), 1, 1, fill=True, color=color, lw=1))

    ax1.set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    ax1.set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])

    ax2.set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    ax2.set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])

    if game_over:
        if player_successful_hits >= 14:
            ax2.set_title("AI's Board - Player Wins!")
        elif ai_successful_hits >= 14:
            ax1.set_title("Player's Board - AI Wins!")

    ax1.annotate(f'Turn: {turn_counter}', xy=(0.5, 1.15), xycoords='axes fraction', ha='center', fontsize=12, color='blue')
    plt.draw()

    if game_over:
        plt.pause(5)  # Pause for 5 seconds before closing the game window
        plt.close()


# Initialize the game state
ai_board = generateRandomBoard(1)
player_board = manually_place_ships_gui()
player_hits = np.zeros((10, 10))
player_misses = np.zeros((10, 10))
ai_hits = np.zeros((10, 10))
ai_misses = np.zeros((10, 10))

# Create the Tkinter window
root = tk.Tk()
root.title("Battleship")

# Create the frames for message boxes and boards
message_frame = tk.Frame(root)
message_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
ai_moves_frame = tk.Frame(root)
ai_moves_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
boards_frame = tk.Frame(root)
boards_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Create the message boxes
message_box = ScrolledText(message_frame, wrap=tk.WORD, height=10, width=40)
message_box.pack(fill="both", expand=True)
message_box.configure(state=tk.DISABLED)

ai_moves_box = ScrolledText(ai_moves_frame, wrap=tk.WORD, height=10, width=40)
ai_moves_box.pack(fill="both", expand=True)
ai_moves_box.configure(state=tk.DISABLED)

# Create the Choose Starter button
start_button = tk.Button(root, text="Choose Starter", command=choose_starter)
start_button.grid(row=2, column=0, columnspan=2, pady=10)

# Setup the plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

update_boards()

canvas = FigureCanvasTkAgg(fig, master=boards_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

fig.canvas.mpl_connect('button_press_event', on_click)

root.mainloop()


