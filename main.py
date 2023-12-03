import tkinter as tk  # Importing the tkinter module for the GUI window
import os  # Importing the os module to get the current directory

current_dir = os.getcwd()  # Getting the current directory


class chess_gui:
    def __init__(self, master: tk.Tk):
        """
        Initializes the Hikaru Nakarmsen Controls GUI.

        Args:
        -   master: The master window object.

        Attributes:
        -   master: The master window object.
        -   player_turn: A boolean variable to keep track of whose turn it is.
        -   time_left_engine: A variable to keep track of the engine's time left.
        -   time_left_player: A variable to keep track of the player's time left.
        -   update_every_ms: A variable to keep track of how often to update the clock.
        -   label_player: A label to display the text "Player Time Left:".
        -   label_time_player: A label to display the player's time left.
        -   label_engine: A label to display the text "Engine Time Left:".
        -   label_time_engine: A label to display the engine's time left.
        -   button: A button to switch turns.
        """
        self.master = master  # Creating a master window object
        self.player_turn = (
            True  # Creating a boolean variable to keep track of whose turn it is
        )
        self.time_left_engine = (
            10000  # Creating a variable to keep track of the engine's time left
        )
        self.time_left_player = (
            10000  # Creating a variable to keep track of the player's time left
        )
        self.update_every_ms = (
            1  # Creating a variable to keep track of how often to update the clock
        )

        self.master.title(
            "Hikaru Nakarmsen Controls"
        )  # Setting the title of the GUI window

        root.resizable(False, False)  # Making the GUI non-resizable

        root.configure(bg="lightblue")  # Set the background color of the window

        self.master.iconbitmap(
            current_dir + "\\images\\player timer gui icon.ico"
        )  # Setting the icon of the GUI window if the timer is for the engine ?

        self.label_player = tk.Label(
            master,
            text="\nPlayer Time Left",
            font=("Courier", 18, "bold"),
            bg="lightblue",
        )  # Creating a label to display the text "Player Time Left:"

        self.label_time_player = tk.Label(
            master, text="", font=("Courier", 18, "bold"), bg="lightblue"
        )  # Creating a label to display the player's time left

        self.label_engine = tk.Label(
            master,
            text="\nEngine Time Left",
            font=("Courier", 18, "bold"),
            bg="lightblue",
        )  # Creating a label to display the text "Engine Time Left:"

        self.label_time_engine = tk.Label(
            master, text="", font=("Courier", 18, "bold"), bg="lightblue"
        )  # Creating a label to display the engine's time left

        self.button = tk.Button(
            master, text="Switch Turn", command=self.switch_turn
        )  # Creating a button to switch turns

        # Placing the widgets in the GUI window
        self.label_player.grid(row=0, column=0, padx=15, pady=5)
        self.label_time_player.grid(row=1, column=0, padx=10, pady=5)
        self.label_engine.grid(row=0, column=1, padx=15, pady=5)
        self.label_time_engine.grid(row=1, column=1, padx=10, pady=5)
        self.button.grid(row=2, column=0, columnspan=2, padx=10, pady=15)

        # Calling the update_clock method to update the clock
        self.update_clock()

    def switch_turn(self):
        """
        Switches the turn between players.

        This method toggles the value of the `player_turn` attribute, indicating
        which player's turn it currently is.

        Parameters:
        -   self (object): The instance of the class.

        Returns:
        -   None
        """
        self.player_turn = not self.player_turn  # Toggling the value of player_turn

    def update_clock(self):
        # Check if the game is over for either player and display the result
        if self.time_left_player <= 0:
            self.label_time_engine.config(text="Time's Up!")
            self.label_time_player.config(text="You Win!")
            return
        elif self.time_left_engine <= 0:
            self.label_time_player.config(text="Time's Up!")
            self.label_time_engine.config(text="You Win!")
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
        self.master.after(self.update_every_ms, self.update_clock)


root = tk.Tk()
clock = chess_gui(root)
root.mainloop()
