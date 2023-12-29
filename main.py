from GUI import chess_game
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()  # Creating a root window object
    game = chess_game(root)  # Creating a chess game object with the root window object
    root.mainloop()  # Running the mainloop of the root window object
