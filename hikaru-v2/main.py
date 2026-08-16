"""
This is the main file of the chess game. It creates a root window object and a chess game object.
"""

from GUI import chess_game  # Importing the chess game class from the GUI module
import tkinter as tk  # Importing tkinter for the GUI window

if __name__ == "__main__":
    root = tk.Tk()  # Creating a root window object
    game = chess_game(root)  # Creating a chess game object with the root window object
    root.mainloop()  # Running the mainloop of the root window object
