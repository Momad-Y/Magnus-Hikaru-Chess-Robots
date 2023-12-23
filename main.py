import tkinter as tk  # Importing the tkinter module for the GUI window
import os  # Importing the os module to get the current directory
import CE as ce  # Importing the chess engine module
import C2M as c2m  # Importing the camera to moves module

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

        # self.dobot_cam = c2m.init_cam(0)  # Initializing the camera # Test

        self.homography_matrix = (
            []
        )  # Creating a variable to keep track of the homography matrix

        self.player_move = ""  # Creating a variable to keep track of the player's move

        self.engine_move = ""  # Creating a variable to keep track of the engine's move

        self.difficulty = 0  # Creating a variable to keep track of the difficulty level

        self.engine = ce.init_stockfish(stockfish_path)  # Initializing the engine

        self.board = (
            ce.init_board()
        )  # Creating a chess board object to keep track of the board

        self.board = ce.set_board_from_fen(
            self.board,
            "1b2B3/kP6/8/8/4Q3/8/8/7K w - - 0 1",
        )  # Test

        self.chess_move_indicators = (
            False,
            False,
            False,
        )  # Creating a variable to keep track of the chess move indicators (kill, enpassant, castling)

        self.game_state = 0  # 0 = in progress, 1 = black won, 2 = white won, 3 = draw

        self.master = master  # Creating a master window object

        self.delay = 1  # Setting the delay for the countdown timer # Test

        self.master.attributes(
            "-topmost", True
        )  # Making the GUI window topmost in Windows

        self.master.title("Hikaru Nakarmsen")  # Setting the title of the GUI window

        self.master.resizable(False, False)  # Making the GUI non-resizable

        # Creating an image object for the board
        self.board_img = ce.get_board_img(self.board)

        self.master.configure(bg=bg_color)  # Set the background color of the window

        self.window_width = 1440  # Setting the width of the GUI window
        self.window_height = 440  # Setting the height of the GUI window
        self.window_x = 20  # Setting the x position of the GUI window
        self.window_y = 20  # Setting the y position of the GUI window

        self.master.geometry(
            f"{self.window_width}x{self.window_height}+{self.window_x}+{self.window_y}"
        )  # Setting the geometry of the GUI window

        self.master.iconbitmap(
            cwd_path + "\\images\\icon.ico"
        )  # Setting the icon of the GUI window if the timer is for the engine

        self.init_widgets()  # Calling the init_widgets method to initialize the widgets

        self.init_game()  # Calling the init_game method to initialize the game

    def init_widgets(self):
        self.difficulty_label = tk.Label(
            self.master,
            text="Select Difficulty",
            font=("Courier", 25, "bold"),
            bg=bg_color,
            fg=main_txt_color,
        )  # Creating a label to display the countdown

        self.countdown_label = tk.Label(
            self.master,
            text="",
            font=("Courier", 25, "bold"),
            bg=bg_color,
            fg=main_txt_color,
        )  # Creating a label to display the countdown

        self.label_player = tk.Label(
            self.master,
            text="Time Left for\nThe Player",
            font=("Courier", 20, "bold"),
            bg=bg_color,
            fg=player_txt_color,
        )  # Creating a label to display the text "Player Time Left"

        self.label_time_player = tk.Label(
            self.master,
            text="",
            font=("Courier", 20, "bold"),
            bg=bg_color,
            fg=player_txt_color,
        )  # Creating a label to display the player's time left

        self.label_engine = tk.Label(
            self.master,
            text="Time Left for\nThe Engine",
            font=("Courier", 20, "bold"),
            bg=bg_color,
            fg=engine_txt_color,
        )  # Creating a label to display the text "Engine Time Left"

        self.empty = tk.Label(
            self.master,
            text="",
            font=("Courier", 20, "bold"),
            bg=bg_color,
            fg=engine_txt_color,
        )  # Creating an empty label to fill the space

        self.label_time_engine = tk.Label(
            self.master,
            text="",
            font=("Courier", 20, "bold"),
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
            width=18,
            border=0,
            cursor="hand2",
            font=("Courier", 15, "bold"),
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
            width=18,
            border=0,
            cursor="hand2",
            font=("Courier", 15, "bold"),
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
            width=13,
            border=0,
            cursor="hand2",
            font=("Courier", 15, "bold"),
        )

        self.difficulty_meduim_btn = tk.Button(
            self.master,
            text="Medium",
            command=lambda: self.set_difficulty(2),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=13,
            border=0,
            cursor="hand2",
            font=("Courier", 15, "bold"),
        )

        self.difficulty_hard_btn = tk.Button(
            self.master,
            text="Hard",
            command=lambda: self.set_difficulty(3),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=13,
            border=0,
            cursor="hand2",
            font=("Courier", 15, "bold"),
        )

        self.difficulty_souls_btn = tk.Button(
            self.master,
            text="Souls",
            command=lambda: self.set_difficulty(4),
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=13,
            border=0,
            cursor="hand2",
            font=("Courier", 15, "bold"),
        )

        self.start_game_btn = tk.Button(
            self.master,
            text="Start Game",
            command=self.start_game,
            background=btn_bg_color,
            foreground=main_txt_color,
            activebackground=btn_bg_active_color,
            activeforeground=main_txt_color,
            width=30,
            border=0,
            cursor="hand2",
            font=("Courier", 25, "bold"),
        )  # Creating a button to start the game

        self.virtual_board_img_canvas = tk.Canvas(
            root,
            width=400,
            height=400,
            borderwidth=0,
            highlightthickness=0,
        )  # Creating a canvas to display the virtual board image

        self.real_board_img_canvas = tk.Canvas(
            root,
            width=400,
            height=400,
            borderwidth=0,
            highlightthickness=0,
        )  # Creating a canvas to display the cropped board image

    def init_game(self):
        # self.empty_board_img = c2m.take_img(
        #     self.dobot_cam
        # )  # Take a picture of the empty board
        self.empty_board_img = c2m.read_img(
            cwd_path + "/Test/Dataset Empty.jpg"
        )  # Test

        self.homography_matrix = c2m.get_homography_matrix(
            self.empty_board_img, cwd_path + "/Images/Motherboard.jpg"
        )  # Find the homography matrix between the empty board image and the reference board image

        self.display_difficulty_options()  # Displaying the difficulty options

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
        self.engine = ce.set_engine_difficulty(self.engine, self.difficulty)

        # Calling the start_game method to start the game
        self.start_game_countdown(self.delay)

    def start_game_countdown(self, time_left):
        # Displaying the difficulty buttons in the GUI window

        # Check if the countdown is over and start the game
        if time_left > 0:
            # Placing the countdown label in the GUI window
            self.countdown_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            time_left -= 1  # Decrementing the time left by 1 second
            self.countdown_label.config(
                text=f"Place the pieces on the board in\n{time_left} seconds"
            )  # Displaying the countdown in the GUI window
            self.master.after(
                1000, self.start_game_countdown, time_left
            )  # Calling the start_game method again after 1 second

        # If the countdown is over, start the game
        else:
            self.countdown_label.destroy()  # Destroying the countdown label
            self.start_game_btn.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def start_game(self):
        # Destroy the countdown label
        self.start_game_btn.destroy()

        # Place the widgets in the GUI window
        self.label_player.grid(row=0, column=0, padx=30, pady=0)
        self.label_engine.grid(row=0, column=1, padx=30, pady=0)

        self.label_time_engine.grid(row=1, column=1, padx=30, pady=0)
        self.label_time_player.grid(row=1, column=0, padx=30, pady=0)

        self.change_turn_btn.grid(row=2, column=0, padx=10, pady=0)
        self.resign_btn.grid(row=2, column=1, padx=10, pady=0)

        self.empty.grid(row=3, column=0, padx=30, pady=0)
        self.empty.grid(row=3, column=1, padx=30, pady=0)

        self.virtual_board_img_canvas.grid(row=0, column=2, rowspan=4, padx=20, pady=20)

        self.real_board_img_canvas.grid(row=0, column=3, rowspan=4, padx=20, pady=20)

        # self.prev_img = c2m.take_img(
        #     self.dobot_cam
        # )  # Take a picture of the board with the pieces on it befor the move is made
        self.prev_img = c2m.read_img(cwd_path + "/Test/Dataset Previous.jpg")  # Test

        self.prev_img, flip = c2m.warp_img(
            self.prev_img, self.homography_matrix  # type: ignore
        )  # Warp the image to a top-down view

        self.prev_img = c2m.flip_img(
            self.prev_img, flip
        )  # Flip the image if it is upside down

        self.prev_img_tk = c2m.cv2_to_tk(
            self.prev_img
        )  # Convert the numpy array to a tkinter image

        # Display the virtual board image in the GUI window
        self.virtual_board_img_canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.board_img,
        )

        # Display the real board image in the GUI window
        self.real_board_img_canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.prev_img_tk,
        )

        # Calling the game_loop method to start the game loop
        self.game_loop()

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

    def switch_turn(self):
        # Check the game state to display the result of the game
        if self.check_game_state() == 1:
            return

        # self.cur_img = c2m.take_img(
        #     self.dobot_cam
        # )  # Take a picture of the board with the pieces on it after the move is made

        self.cur_img = c2m.read_img(cwd_path + "/Test/Dataset Current.jpg")  # Test

        self.cur_img, flip = c2m.warp_img(
            self.cur_img, self.homography_matrix  # type: ignore
        )  # Warp the image to a top-down view

        self.cur_img = c2m.flip_img(
            self.cur_img, flip
        )  # Flip the image if it is upside down

        self.cur_img_tk = c2m.cv2_to_tk(
            self.cur_img
        )  # Convert the numpy array to a tkinter image

        self.player_moves_list = c2m.find_moves(
            self.prev_img, self.cur_img
        )  # Get the player's moves from the images

        if self.player_moves_list == None:
            self.game_state = 1  # Set the game state to 1 (Engine wins)
            self.check_game_state()  # Check the game state to display the result of the game
            return

        self.player_move = ce.moves_to_ACN(
            self.board, self.player_moves_list  # type: ignore
        )  # Get the player's move

        # self.player_move = input("Enter your move: ")  # Test

        # Check the move and return if it is invalid
        if not ce.check_move(self.board, self.player_move):
            self.game_state = 1  # Set the game state to 1 (Engine wins)
            self.check_game_state()  # Check the game state to display the result of the game
            return  # Return if the move is invalid

        # Make the move on the board
        self.board.push_san(self.player_move)

        # Get the tkinter img of the board after the player's move
        self.board_img = ce.get_board_img(self.board)

        self.virtual_board_img_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.board_img
        )  # Display the virtual board image in the GUI window

        self.real_board_img_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.cur_img_tk
        )  # Display the real board image in the GUI window

        # Disabling the button to switch turns
        self.change_turn_btn.config(state=tk.DISABLED, cursor="arrow")

        self.player_turn = not self.player_turn  # Toggling the value of player_turn

        self.prev_img = self.cur_img  # Setting the previous image to the current image

        self.get_engine_move()  # Calling the get_engine_move method to get the engine's move

    def get_engine_move(self):
        # Get the best move from the engine
        self.engine_move = ce.get_best_move(self.engine, self.board)

        # Check the move and return if it is invalid
        if not ce.check_move(self.board, self.engine_move):  # type: ignore
            self.game_state = 2  # Set the game state to 2 (Player wins)
            self.check_game_state()  # Check the game state to display the result of the game
            return  # Return if the move is invalid

        # Check if the move is a kill, castling or enpassant
        self.chess_move_indicators = ce.check_indicators(self.board, self.engine_move)  # type: ignore

        # Send the move to the arm !!

        # Make the move on the board
        self.board.push_san(self.engine_move)  # type: ignore

        # Get the tkinter img of the board after the engine's move
        self.board_img = ce.get_board_img(self.board)

        # Display the board image in the GUI window
        self.virtual_board_img_canvas.create_image(
            0, 0, anchor=tk.NW, image=self.board_img
        )

        # Check the game state to display the result of the game
        if self.check_game_state() == 1:
            return

        # Enabling the button to switch turns
        self.change_turn_btn.config(state=tk.NORMAL, cursor="hand2")

        # Wait till the arm is done moving !!

        self.player_turn = not self.player_turn  # Toggling the value of player_turn

    def resign(self):
        # Check if the game is already over and return if it is
        if self.game_state != 0:
            return

        # If the player resigns, set the game state to 1 (Engine wins)
        self.game_state = 1

        # Check the game state to display the result of the game
        self.check_game_state()

    def check_game_state(self):
        if self.time_left_player <= 0:
            self.game_state = 1  # Set the game state to 1 (Engine wins)

        elif self.time_left_engine <= 0:
            self.game_state = 2  # Set the game state to 2 (Player wins)

        if ce.check_game_state(self.board) == 1:
            self.game_state = 1  # Set the game state to 1 (Engine wins)

        elif ce.check_game_state(self.board) == 2:
            self.game_state = 2  # Set the game state to 2 (Player wins)

        elif ce.check_game_state(self.board) == 3:
            self.game_state = 3  # Set the game state to 3 (Draw)

        return self.display_result()  # Display the result of the game

    def display_result(self):
        # Display the result of the game if the game is over and return 1

        if self.game_state == 1:  # If the engine wins
            self.change_turn_btn.config(
                state=tk.DISABLED, cursor="arrow"
            )  # Disable the button to switch turns

            self.resign_btn.config(
                state=tk.DISABLED, cursor="arrow"
            )  # Disable the button to resign

            # Display the result of the game in the GUI window
            self.label_time_player.config(text="You Lose!")
            self.label_time_engine.config(text="You Win!")
            return 1

        elif self.game_state == 2:  # If the player wins
            self.change_turn_btn.config(
                state=tk.DISABLED, cursor="arrow"
            )  # Disable the button to switch turns

            self.resign_btn.config(
                state=tk.DISABLED, cursor="arrow"
            )  # Disable the button to resign

            # Display the result of the game in the GUI window
            self.label_time_player.config(text="You Win!")
            self.label_time_engine.config(text="You Lose!")
            return 1

        elif self.game_state == 3:  # If the game is a draw
            self.change_turn_btn.config(
                state=tk.DISABLED, cursor="arrow"
            )  # Disable the button to switch turns

            self.resign_btn.config(
                state=tk.DISABLED, cursor="arrow"
            )  # Disable the button to resign

            # Display the result of the game in the GUI window
            self.label_time_player.config(text="Draw!")
            self.label_time_engine.config(text="Draw!")
            return 1

        return 0


if __name__ == "__main__":
    root = tk.Tk()  # Creating a root window object
    game = chess_game(root)  # Creating a chess game object with the root window object
    root.mainloop()  # Running the mainloop of the root window object
