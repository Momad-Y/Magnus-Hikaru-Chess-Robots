import tkinter as tk  # Importing the tkinter module for the GUI window
import os  # Importing the os module to get the current directory
import CE as chess_engine  # Importing the chess engine module

cwd_path = os.getcwd()  # Getting the current directory
stockfish_path = (
    cwd_path + "\\stockfish\\stockfish-windows-2022-x86-64-avx2.exe"
)  # Setting the path to the stockfish engine

bg_color = "#302e2b"  # Setting the background color of the GUI window
player_txt_color = (
    "#9cdc5b"  # Setting the text color of the GUI window if the timer is for the player
)
engine_txt_color = (
    "#fa732c"  # Setting the text color of the GUI window if the timer is for the engine
)
btn_bg_color = "#7c766f"  # Setting the background color of the button
btn_bg_active_color = (
    "#999691"  # Setting the background color of the button when active
)
main_txt_color = "#e4e2dd"  # Setting the text color of the button


class chess_game:
    def __init__(self, master: tk.Tk):
        self.player_turn = (
            True  # Creating a boolean variable to keep track of whose turn it is
        )
        self.time_left_engine = (
            10 * 60000  # Creating a variable to keep track of the engine's time left
        )
        self.time_left_player = (
            10 * 60000  # Creating a variable to keep track of the player's time left
        )
        self.update_every_ms = (
            1  # Creating a variable to keep track of how often to update the clock
        )

        self.difficulty = 0  # Creating a variable to keep track of the difficulty level

        self.engine = chess_engine.init_stockfish(stockfish_path)

        self.board = chess_engine.init_board()

        self.game_state = 0  # 0 = in progress, 1 = black won, 2 = white won, 3 = draw

        self.master = master  # Creating a master window object

        self.delay = 10  # Setting the delay for the countdown timer

        self.master.attributes(
            "-topmost", True
        )  # Making the GUI window topmost in Windows

        self.master.title(
            "Hikaru Nakarmsen Controls"
        )  # Setting the title of the GUI window

        self.master.resizable(False, False)  # Making the GUI non-resizable

        self.master.configure(bg=bg_color)  # Set the background color of the window

        self.window_width = 520  # Setting the width of the GUI window
        self.window_height = 184  # Setting the height of the GUI window
        self.window_x = 20  # Setting the x position of the GUI window
        self.window_y = 20  # Setting the y position of the GUI window

        self.master.geometry(
            f"{self.window_width}x{self.window_height}+{self.window_x}+{self.window_y}"
        )  # Setting the geometry of the GUI window

        self.master.iconbitmap(
            cwd_path + "\\images\\icon.ico"
        )  # Setting the icon of the GUI window if the timer is for the engine

        self.init_widgets()

        self.display_difficulty_options()

    def init_widgets(self):
        self.difficulty_label = tk.Label(
            self.master,
            text="Select Difficulty",
            font=("Courier", 18, "bold"),
            bg=bg_color,
            fg=main_txt_color,
        )  # Creating a label to display the countdown

        self.countdown_label = tk.Label(
            self.master,
            text="",
            font=("Courier", 18, "bold"),
            bg=bg_color,
            fg=main_txt_color,
        )  # Creating a label to display the countdown

        self.label_player = tk.Label(
            self.master,
            text="\nPlayer Time Left",
            font=("Courier", 18, "bold"),
            bg=bg_color,
            fg=player_txt_color,
        )  # Creating a label to display the text "Player Time Left"

        self.label_time_player = tk.Label(
            self.master,
            text="",
            font=("Courier", 18, "bold"),
            bg=bg_color,
            fg=player_txt_color,
        )  # Creating a label to display the player's time left

        self.label_engine = tk.Label(
            self.master,
            text="\nEngine Time Left",
            font=("Courier", 18, "bold"),
            bg=bg_color,
            fg=engine_txt_color,
        )  # Creating a label to display the text "Engine Time Left"

        self.label_time_engine = tk.Label(
            self.master,
            text="",
            font=("Courier", 18, "bold"),
            bg=bg_color,
            fg=engine_txt_color,
        )  # Creating a label to display the engine's time left

        self.change_turn_btn = tk.Button(
            self.master,
            text="Switch Turn",
            command=self.switch_turn,
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=15,
            border=0,
            cursor="hand2",
            font=("Courier", 13, "bold"),
        )
        # Creating a button to switch turns

        self.resign_btn = tk.Button(
            self.master,
            text="Resign",
            command=self.resign,
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=15,
            border=0,
            cursor="hand2",
            font=("Courier", 13, "bold"),
        )  # Creating a button to resign

        # Creating 4 buttons to set the difficulty level
        self.difficulty_easy_btn = tk.Button(
            self.master,
            text="Easy",
            command=lambda: self.set_difficulty(1),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=8,
            border=0,
            cursor="hand2",
            font=("Courier", 13, "bold"),
        )

        self.difficulty_meduim_btn = tk.Button(
            self.master,
            text="Medium",
            command=lambda: self.set_difficulty(2),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=8,
            border=0,
            cursor="hand2",
            font=("Courier", 13, "bold"),
        )

        self.difficulty_hard_btn = tk.Button(
            self.master,
            text="Hard",
            command=lambda: self.set_difficulty(3),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=8,
            border=0,
            cursor="hand2",
            font=("Courier", 13, "bold"),
        )

        self.difficulty_souls_btn = tk.Button(
            self.master,
            text="Souls",
            command=lambda: self.set_difficulty(4),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=8,
            border=0,
            cursor="hand2",
            font=("Courier", 13, "bold"),
        )

    def display_difficulty_options(self):
        self.difficulty_label.place(
            relx=0.5, rely=0.35, anchor=tk.CENTER
        )  # Placing the difficulty label in the GUI window

        # Placing the difficulty buttons in the GUI window
        self.difficulty_easy_btn.place(relx=0.2, rely=0.65, anchor=tk.CENTER)
        self.difficulty_meduim_btn.place(relx=0.4, rely=0.65, anchor=tk.CENTER)
        self.difficulty_hard_btn.place(relx=0.6, rely=0.65, anchor=tk.CENTER)
        self.difficulty_souls_btn.place(relx=0.8, rely=0.65, anchor=tk.CENTER)

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty  # Setting the difficulty level

        # Destroying the difficulty buttons and label
        self.difficulty_label.destroy()
        self.difficulty_easy_btn.destroy()
        self.difficulty_meduim_btn.destroy()
        self.difficulty_hard_btn.destroy()
        self.difficulty_souls_btn.destroy()

        # Setting the difficulty of the engine
        self.engine = chess_engine.set_engine_difficulty(self.engine, self.difficulty)
        print(self.engine.get_parameters())

        # Calling the start_game method to start the game
        self.start_game(self.delay)

    def start_game(self, time_left):
        # Displaying the difficulty buttons in the GUI window

        # Check if the countdown is over and start the game
        if time_left > 0:
            # Placing the countdown label in the GUI window
            self.countdown_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            time_left -= 1  # Decrementing the time left by 1 second
            self.countdown_label.config(
                text=f"Be Ready in {time_left} Seconds"
            )  # Displaying the countdown in the GUI window
            self.master.after(
                1000, self.start_game, time_left
            )  # Calling the start_game method again after 1 second

        # If the countdown is over, start the game
        else:
            # Destroy the countdown label
            self.countdown_label.destroy()

            # Place the widgets in the GUI window
            self.label_player.grid(row=0, column=0, padx=15, pady=5)
            self.label_time_player.grid(row=1, column=0, padx=10, pady=5)
            self.label_engine.grid(row=0, column=1, padx=15, pady=5)
            self.label_time_engine.grid(row=1, column=1, padx=10, pady=5)
            self.change_turn_btn.grid(row=2, column=0, padx=10, pady=20)
            self.resign_btn.grid(row=2, column=1, padx=10, pady=20)

            # Calling the game_loop method to start the game loop
            self.game_loop()

    def switch_turn(self):
        self.player_turn = not self.player_turn  # Toggling the value of player_turn

    def game_loop(self):
        # Check if the game is over
        if self.check_game_state() == 1:
            # give the player 5 seconds to see the result
            self.master.after(5000, self.master.destroy)
            return

        # Update the clock every ms based on whose turn it is
        if self.player_turn:
            self.time_left_player -= 1
        else:
            self.time_left_engine -= 1

        time_ms_player = (
            self.time_left_player
        )  # Getting the player time left in milliseconds as an integer
        time_sec_player = (
            time_ms_player // 1000
        )  # Getting the player time left in seconds as an integer
        time_min_player = (
            time_sec_player // 60
        )  # Getting the player time left in minutes as an integer

        # Formatting the player time string to display in the GUI window
        time_str_player = f"{time_min_player:02d}:{time_sec_player % 60:02d}:{time_ms_player % 100:02d}"

        self.label_time_player.config(
            text=time_str_player
        )  # Displaying the player time left in the GUI window

        time_ms_engine = (
            self.time_left_engine
        )  # Getting the engine time left in milliseconds as an integer
        time_sec_engine = (
            time_ms_engine // 1000
        )  # Getting the engine time left in seconds as an integer
        time_min_engine = (
            time_sec_engine // 60
        )  # Getting the engine time left in minutes as an integer

        # Formatting the engine time string to display in the GUI window
        time_str_engine = f"{time_min_engine:02d}:{time_sec_engine % 60:02d}:{time_ms_engine % 100:02d}"

        self.label_time_engine.config(
            text=time_str_engine
        )  # Displaying the engine time left in the GUI window

        # Calling the update_clock method again after the specified time
        self.master.after(self.update_every_ms, self.game_loop)

    def check_game_state(self):
        if self.time_left_player <= 0:
            self.game_state = 1
            return 1
        elif self.time_left_engine <= 0:
            self.game_state = 2

        if self.game_state == 1:
            self.label_time_player.config(text="You Lose!")
            self.label_time_engine.config(text="You Win!")
            return 1

        elif self.game_state == 2:
            self.label_time_player.config(text="You Win!")
            self.label_time_engine.config(text="You Lose!")
            return 1

        return 0

    def resign(self):
        # Check if the game is already over and return if it is
        if self.game_state != 0:
            return

        # If the player resigns, set the game state to 1 (Engine wins)
        self.game_state = 1

        # Check the game state to display the result of the game
        self.check_game_state()


if __name__ == "__main__":
    root = tk.Tk()
    clock = chess_game(root)
    root.mainloop()
