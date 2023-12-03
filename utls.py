from multiprocessing import (
    Process,
    Manager,
)  # Importing the multiprocessing module to create the timer process
import tkinter as tk  # Importing the tkinter module to create the GUI

update_every = 1  # Update the GUI every millisecond
engine_timer = 10000  # The engine's timer initially set to 10 seconds
player_timer = 10000  # The player's timer initially set to 10 seconds


def timer_gui(time_left_dict, engine_or_player):
    def update_label():
        if time_left_dict[engine_or_player] > 0:
            time_left_dict[engine_or_player] -= 1
            time_ms = int(time_left_dict[engine_or_player])
            time_sec = time_ms // 1000
            time_min = time_sec // 60
            time_str = f"{time_min:02d}:{time_sec % 60:02d}:{time_ms % 100:02d}"
            label.config(text=time_str)
            root.after(update_every, update_label)

    main_label = "\n" + engine_or_player + "'s Time Left"  # The main label of the GUI

    root = tk.Tk()  # Creating the root window of the GUI

    root.title(engine_or_player + "'s Timer")  # Setting the title of the GUI

    root.geometry("250x70")  # Setting the size of the GUI

    root.resizable(False, False)  # Making the GUI non-resizable

    label = tk.Label(root, text=main_label)  # Creating the main label of the GUI
    label.pack()  # Packing the main label into the root window

    label = tk.Label(
        root, text=str(time_left_dict[engine_or_player])
    )  # Creating the label to display the timer value
    label.pack()  # Packing the label into the root window

    root.after(
        update_every, update_label
    )  # Calling the update_label function every millisecond

    root.mainloop()  # Running the GUI in a loop


if __name__ == "__main__":
    with Manager() as manager:  # Creating a manager object to share the timer values between processes
        time_left_dict = (
            manager.dict()
        )  # Creating a dictionary to store the timer values
        time_left_dict[
            "Engine"
        ] = engine_timer  # Adding the engine's timer to the dictionary
        time_left_dict[
            "Player"
        ] = player_timer  # Adding the player's timer to the dictionary

        engine_timer = Process(
            target=timer_gui, args=(time_left_dict, "Engine")
        )  # Creating the engine's timer process
        player_timer = Process(
            target=timer_gui, args=(time_left_dict, "Player")
        )  # Creating the player's timer process

        engine_timer.start()  # Starting the engine's timer process
        player_timer.start()  # Starting the player's timer process

        x = input(
            "Press q to stop: "
        )  # Waiting for the user to press q to stop the timer

        if x == "q":
            engine_timer.terminate()
            player_timer.terminate()
            engine_timer.join()
            player_timer.join()

            engine_timer = time_left_dict["Engine"]
            player_timer = time_left_dict["Player"]

            print(f"Engine time left: {engine_timer}")
            print(f"Player time left: {player_timer}")
