from multiprocessing import (
    Process,
    Manager,
)  # Importing the multiprocessing module to create the timer process
import tkinter as tk  # Importing the tkinter module to create the GUI
import os  # Importing the os module to get the current directory

update_every = 1  # Update the GUI every millisecond
engine_time_left = 10000  # The engine's timer initially set to 10 seconds
player_timer_left = 10000  # The player's timer initially set to 10 seconds
current_dir = os.getcwd()  # Getting the current directory


def timer_gui_proc(time_left_dict: dict, engine_or_player: str):
    """
    Creates a GUI window to display a timer for the engine or player.

    Parameters:
    -   time_left_dict (multiprocessing.managers.DictProxy): A dictionary that stores the time left for the engine and player.
    -   engine_or_player (str): A string that specifies whether the timer is for the engine or player.

    Returns:
    -   None

    The function updates the time left in the dictionary every second and displays it in the GUI window.
    The window's title, position, dimensions, and background color depend on whether the timer is for the engine or player.
    The window is non-resizable and has a custom icon.

    The timer value is displayed in the format "MM:SS:MS", where MM is minutes, SS is seconds, and MS is milliseconds.

    """

    def update_timer_label():
        """
        Updates the label with the remaining time.

        This function decrements the timer value by 1, calculates the remaining time in minutes, seconds, and milliseconds,
        formats the time string, and updates the label in the GUI window. It then schedules the next update of the label
        after a specified time interval.

        Parameters:
        -   None

        Returns:
        -   None
        """

        # Checking if the timer has not expired
        if time_left_dict[engine_or_player] > 0:
            time_left_dict[engine_or_player] -= 1  # Decrementing the timer value by 1
            time_ms = int(
                time_left_dict[engine_or_player]
            )  # Getting the time left in milliseconds as an integer
            time_sec = time_ms // 1000  # Getting the time left in seconds as an integer
            time_min = time_sec // 60  # Getting the time left in minutes as an integer
            time_str = f"{time_min:02d}:{time_sec % 60:02d}:{time_ms % 100:02d}"  # Formatting the time string to display in the GUI window
            label.config(
                text=time_str, font=("Courier", 18, "bold"), bg=bg_color
            )  # Updating the label to display the new time string
            root.after(
                update_every, update_timer_label
            )  # Calling the update_label function after 1 millisecond to update the label again

    main_label = "\n" + engine_or_player + "'s Time Left"  # The main label of the GUI

    root = tk.Tk()  # Creating the root window of the GUI

    if engine_or_player == "Engine":
        y = 50  # Y coordinate for the Tk root window if the timer is for the engine
        bg_color = "lightpink"  # Background color for the Tk root window if the timer is for the engine
        root.iconbitmap(
            current_dir + "\\images\\engine timer gui icon.ico"
        )  # Setting the icon of the GUI window if the timer is for the engine

    else:
        y = 210  # Y coordinate for the Tk root window if the timer is for the player
        bg_color = "lightblue"  # Background color for the Tk root window if the timer is for the player
        root.iconbitmap(
            current_dir + "\\images\\player timer gui icon.ico"
        )  # Setting the icon of the GUI window if the timer is for the engine

    root.title(engine_or_player + "'s Timer")  # Setting the title of the GUI

    w = 300  # Width for the Tk root window
    h = 115  # Height for the Tk root window
    x = 10  # X coordinate for the Tk root window

    root.geometry(
        "%dx%d+%d+%d" % (w, h, x, y)
    )  # Setting the dimensions of the GUI window

    root.resizable(False, False)  # Making the GUI non-resizable

    root.configure(bg=bg_color)  # Set the background color of the window

    label = tk.Label(
        root, text=main_label, font=("Courier", 18, "bold"), bg=bg_color
    )  # Creating the main label of the GUI
    label.pack()  # Packing the main label into the root window

    label = tk.Label(root, text="")  # Creating the label to display the timer value
    label.pack()  # Packing the label into the root window

    root.after(
        update_every, update_timer_label
    )  # Calling the update_label function every millisecond

    root.mainloop()  # Running the GUI in a loop


def demo():
    global engine_time_left
    global player_timer_left

    with Manager() as manager:  # Creating a manager object to share the timer values between processes
        time_left_dict = (
            manager.dict()
        )  # Creating a dictionary to store the timer values
        time_left_dict[
            "Engine"
        ] = engine_time_left  # Adding the engine's timer to the dictionary
        time_left_dict[
            "Player"
        ] = player_timer_left  # Adding the player's timer to the dictionary

        while True:
            x = input("Press q to stop or r to restart or : ")

            if x == "q":
                engine_timer_proc.terminate()
                player_timer_proc.terminate()

                engine_timer_left = time_left_dict["Engine"]
                player_timer_left = time_left_dict["Player"]

                print(f"Engine time left: {engine_timer_left}")
                print(f"Player time left: {player_timer_left}")

                continue

            elif x == "r":
                engine_timer_proc = Process(
                    target=timer_gui_proc, args=(time_left_dict, "Engine")
                )  # Creating the engine's timer process
                player_timer_proc = Process(
                    target=timer_gui_proc, args=(time_left_dict, "Player")
                )  # Creating the player's timer process

                engine_timer_proc.start()  # Starting the engine's timer process
                player_timer_proc.start()  # Starting the player's timer process

                engine_timer_left = time_left_dict["Engine"]
                player_timer_left = time_left_dict["Player"]

                print(f"Engine time left: {engine_timer_left}")
                print(f"Player time left: {player_timer_left}")


if __name__ == "__main__":
    demo()
