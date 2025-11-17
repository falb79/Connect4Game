import tkinter as tk  #GUI library for building the window and to draw the board
from tkinter import messagebox, Label  #To show "gameover" messages and text in instructions window
import random  #For random bot moves
import copy # To create a copy of the board

class ConnectFour:
    def __init__(self, root):
        self.root = root  #Main window
        self.root.title("Connect Four Game")  #The Title of window
        self.rows = 6  #Number of rows
        self.columns = 7  #Number of columns
        self.board = [[0] * self.columns for _ in range(self.rows)]  # 2D list to represent the board (0: empty, 1: user, 2: bot)
        self.current_player = 1  # Start with user
        self.colors = {0: "light gray", 1: "pink", 2: "yellow"}  # Mapping values to colors
        self.create_ui()  # Set up the UI

    # Create a canvas where the board will be drawn
    def create_ui(self):
        self.canvas = tk.Canvas(self.root, width=700, height=600, bg="white")
        self.canvas.pack() #Adds the canvas to the window
        self.draw_board() #Draws the initial board
        self.canvas.bind("<Button-1>", self.user_move)# Bind mouse click to user's move

    # Draw the board based on the current state
    def draw_board(self):  
        self.canvas.delete("all")  # Clear existing shapes
        # Loop through each cell and draw a circle with the appropriate color
        for row in range(self.rows):
            for col in range(self.columns):
                x1 = col * 100 + 9  # Left padding
                y1 = row * 100 + 9  # Top padding
                x2 = x1 + 50  # Width of the circle
                y2 = y1 + 50  # Height of the circle
                color = self.colors[self.board[row][col]]  # Get color based on cell value
                self.canvas.create_oval(x1, y1,x2, y2,fill=color, outline="purple")  # Draw the circle

    #Handle user's move when they click on the board
    def user_move(self, event): 
        col = event.x // 100  # Determine the column based on x-position of the click
        if self.make_move(col, 1):  # Make user's move
            if self.check_winner(self.board, 1):  # Check if user wins
                self.end_game("Congrats, You win!")  #Show win message and quit
                return
            self.bot_move()  # Let the bot make its move

    # Handle bot moves
    def bot_move(self, depth = 4):
        # Get all columns that are not full
        available_columns = self.get_valid_locations(self.board)
        if available_columns:
            # Use minimax to get the best column to play
            col, _ = self.minimax(self.board, depth, True, 2, 1)
            self.make_move(col, 2)  # Bot makes its move
            if self.check_winner(self.board, 2):  # Check if bot wins
                self.end_game("AI Bot wins!")  # Show lose message and quit
                return

    # Function to add the player/bot move to the board
    def make_move(self, col, player):
        # Start from bottom row and place piece in the first empty cell
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = player  #Set cell to player's value
                self.draw_board()  #Redraw board with new move
                return True  #Move is successful
        return False  #Column is full, move failed

    # Check who won the game
    def check_winner(self, board, player):
        for r in range(self.rows):
            for c in range(self.columns):
                # If 4 in a row are pink/yellow
                if c <= self.columns - 4 and all(board[r][c + k] == player for k in range(4)):
                    return True
                # If 4 in a column are pink/yellow
                if r <= self.rows - 4 and all(board[r + k][c] == player for k in range(4)):
                    return True
                # If 4 are connected diagonally (\)
                if r <= self.rows - 4 and c <= self.columns - 4 and all(board[r + k][c + k] == player for k in range(4)):
                    return True
                # If 4 are connected diagonally (/)
                if r >= 3 and c <= self.columns - 4 and all(board[r - k][c + k] == player for k in range(4)):
                    return True
        # Otherwise, return false since no player won
        return False
    
    # Function to check the next available row 
    def get_valid_row(self, board, col):
        for row in range(self.rows - 1, -1, -1):  # Start from bottom row to top
            if board[row][col] == 0: # if the position is empty
                return row
        return -1  # position is full
    
    # Function to check if the column is empty
    def is_valid_column(self, board, col):
        # Returns true if the position is empty, -1 otherwise
        return self.get_valid_row(board, col) != -1
    
    # Function to return all available columns 
    def get_valid_locations(self, board):
        # check each column of the board, if they are valid add them to the array
        return [col for col in range(self.columns) if self.is_valid_column(board, col)]

    # Function to help score the state of the game
    def evaluate_window(self, window, player):
        score = 0   # Initialize score to zero
        opponent_piece = 1 if player == 2 else 2    # define player and opponent pieces

        # If the player has 4 pieces on the board, then it's probably a winning move
        if window.count(player) == 4:
            score += 100  
        # If the player has 3 pieces on the board, then they have good oppotunity to win
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 10  
        # If the player has 2 pieces on the board, then they have potential oppotunity to win
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 4 

        # On the other hand, the player needs to stop opponent from winning
        if window.count(opponent_piece) == 3 and window.count(0) == 1:
            score -= 80  # if they have 3 pieces, prioritize blocking
        elif window.count(opponent_piece) == 2 and window.count(0) == 2:
            score -= 5

        return score
    
    # Function to evaluate current board state
    def score_position(self, board, player):
        score = 0
        # loop through the board
        for row in range(self.rows):
            for col in range(self.columns):
                # check by row
                if col + 3 < self.columns:
                    # Evaluate board state
                    window = [board[row][col + i] for i in range(4)]
                    score += self.evaluate_window(window, player)

                # check by column
                if row + 3 < self.rows:
                    # Evaluate board state
                    window = [board[row + i][col] for i in range(4)]
                    score += self.evaluate_window(window, player)

                # check diagonally (\)
                if row + 3 < self.rows and col + 3 < self.columns:
                    # Evaluate board state
                    window = [board[row + i][col + i] for i in range(4)]
                    score += self.evaluate_window(window, player)

                # check diagonally (/)
                if row - 3 >= 0 and col + 3 < self.columns:
                    # Evaluate coard state
                    window = [board[row - i][col + i] for i in range(4)]
                    score += self.evaluate_window(window, player)
        return score
        
    # Minimax function to maximize bot movement
    def minimax(self, board, depth, maximizingPlayer, bot_piece, player_piece):
        # Get list of valid columns "not full"
        valid_columns = self.get_valid_locations(board)
        # Check if the game has ended or reached max depth
        is_terminal = self.check_winner(board, 2) or self.check_winner(board, 1) or not valid_columns

        # Return evaluation score at terminal node or max depth
        if depth == 0 or is_terminal:
            if self.check_winner(board, 2):
                return (None, 100000)  # Big positive score if bot wins
            elif self.check_winner(board, 1):
                return (None, -100000)  # Big negative score if player wins
            else:
                return (None, self.score_position(board, bot_piece))  # Heuristic score

        # Maximize the score if it is the robot’s turn
        if maximizingPlayer:
            best_score = -float('inf')
            best_col = random.choice(valid_columns)
            for col in valid_columns:
                # create a copy of the board
                temp_board = copy.deepcopy(board)
                row = self.get_valid_row(temp_board, col)
                temp_board[row][col] = bot_piece
                # check the score when adding the bot piece
                _, score = self.minimax(temp_board, depth - 1, False, bot_piece, player_piece)
                # if it's higher than previous best score, update
                if score > best_score:
                    best_score = score
                    best_col = col
            return best_col, best_score

        # Minimize the score if it is the player's turn 
        else:
            best_score = float('inf')
            best_col = random.choice(valid_columns)
            for col in valid_columns:
                # create a copy of the board
                temp_board = copy.deepcopy(board)
                row = self.get_valid_row(temp_board, col)
                # check the score when adding the player piece
                temp_board[row][col] = player_piece
                _, score = self.minimax(temp_board, depth - 1, True, bot_piece, player_piece)
                # if it's lower than previous best score, update
                if score < best_score:
                    best_score = score
                    best_col = col
            return best_col, best_score

    # Function to end the game and display the correct message
    def end_game(self, message):
        messagebox.showinfo("Game Over", message)  # Show message box with the result
        self.root.quit()  # Exit the game

if __name__ == "__main__":
    instructions = tk.Tk()#Create the instructions window
    instructions.title("Game instructions") # instructions window title
    canvas = tk.Canvas(instructions, width=700, height=600, bg="white")
    canvas.pack() #Adds the canvas to the window
    # the instructions on how to play the game
    text = "Welcome to Connect 4\n\nHow to play:"
    label = Label(instructions, text=text, font=('Times New Roman', 16), bg="white", justify="center") # create a label
    label.place(x=250, y=200)    # place the label in this position on the window
    label = Label(instructions, text="1. You have the pink pieces, and the bot has the yellow pieces\n\n" \
    "2. Try to connect 4 pieces horizontally, vertically, or diagonally\n\n3. You will alternate turns with the bot, try to defeat it!\n",
    font=('Times New Roman', 16), bg="white", justify="left")
    label.place(x=80, y=300)    # place the label in this position on the window
    label = Label(instructions, text="Close the tab to start the game", font=('Times New Roman', 16), bg="white", justify="center") # create a label
    label.place(x=210, y=450)    # place the label in this position on the window

    instructions.mainloop()#Run the Tkinter event loop
    
    root = tk.Tk()#Create the main window
    game = ConnectFour(root)#Start the game
    root.mainloop()#Run the Tkinter event loop
