"""
This module contains the functions that control the robotic arm.
"""

import Dobot.DoBotArm as db
import xmltodict

coordinates_dict = {}  # Initialize the coordinates dictionary
home_graveyard_coordinate = (0, 0, 0)  # Initialize the home and graveyard coordinates
calibration_coordinate = (0, 0, 0)  # Initialize the calibration coordinate
z_picked = 80  # The height of the piece when it is picked up


def init_arm(xml_file_path: str):
    """
    Initializes the DoBot arm.

    Args:
    -   None

    Returns:
    -   arm (DoBotArm): The initialized DoBot arm object.
    """

    get_coordinates_from_xml(xml_file_path)

    arm = db.DoBotArm(
        home_graveyard_coordinate[0],
        home_graveyard_coordinate[1],
        home_graveyard_coordinate[2],
    )

    arm.setSuction(False)

    return arm


def get_coordinates_from_xml(xml_file_path: str):
    """
    Reads an XML file containing coordinates and converts it into a coordinates dictionary.

    Args:
    -   xml_file_path (str): The path to the XML file.

    Returns:
    -   None
    """

    global coordinates_dict  # Make the coordinates dictionary global
    global home_graveyard_coordinate  # Make the home and graveyard coordinate global
    global calibration_coordinate  # Make the calibration coordinate global

    edited_dict = {}  # Initialize the edited dictionary

    # Read the XML file
    with open(xml_file_path, "r") as file:
        xml_string = file.read()

    xml_dict = xmltodict.parse(xml_string)  # Convert the XML file to a dictionary

    xml_dict = xml_dict["root"]  # Remove the first element of the dictionary (metadata)

    # Remove the first 2 elements of the dictionary (metadata)
    del xml_dict["DobotType"]
    del xml_dict["row_StudioVersion"]

    # Rename the keys of the dictionary to the cell names
    i = 0
    for key in xml_dict:
        edited_dict[xml_dict["row" + str(i)]["item_1"]] = xml_dict[key]
        i += 1

    # Remove the first and last 2 elements of the dictionary for each key
    for key in edited_dict:
        del edited_dict[key]["item_0"]
        del edited_dict[key]["item_1"]
        del edited_dict[key]["item_10"]
        del edited_dict[key]["item_12"]

    # Convert the dictionary to a dictionary of tuples
    for key in edited_dict:
        edited_dict[key] = (
            float(edited_dict[key]["item_2"]),
            float(edited_dict[key]["item_3"]),
            float(edited_dict[key]["item_4"]),
            float(edited_dict[key]["item_5"]),
        )

    calibration_coordinate = edited_dict[
        "Calibration Coordinate"
    ]  # Set the calibration coordinate
    home_graveyard_coordinate = edited_dict[
        "Home and Graveyard Coordinate"
    ]  # Set the home and graveyard coordinate

    # Remove the calibration coordinate and the home and graveyard coordinate from the dictionary
    del edited_dict["Calibration Coordinate"]
    del edited_dict["Home and Graveyard Coordinate"]

    coordinates_dict = (
        edited_dict  # Set the global coordinates dictionary to the edited dictionary
    )


def move_arm_Z(arm: db.DoBotArm, z: float):
    """
    Moves the arm to a specified height in the Z-axis.

    Args:
    -   arm (db.DoBotArm): The DoBotArm object representing the robotic arm.
    -   z (float): The desired height in the Z-axis.

    Returns:
    -   None
    """

    arm.pick(z)


def toggle_suction(arm: db.DoBotArm):
    """
    Toggles the suction on the DoBotArm.

    Args:
    -   arm (db.DoBotArm): The DoBotArm object to toggle the suction on.

    Returns:
    -   None
    """

    arm.toggleSuction()


def move_arm_XYR(arm: db.DoBotArm, pos: tuple):
    """
    Moves the DoBot arm to the specified X, Y and R.

    Args:
    -   arm (db.DoBotArm): The DoBot arm object.
    -   pos (tuple): A tuple containing the coordinates.

    Returns:
    -   None
    """

    arm.moveArmXYR(pos[0], pos[1], pos[3])


def move_arm_XYR_jump(arm: db.DoBotArm, pos: tuple):
    """
    Moves the DoBot arm to the specified X, Y and R.

    Args:
    -   arm (db.DoBotArm): The DoBot arm object.
    -   pos (tuple): A tuple containing the coordinates.

    Returns:
    -   None
    """

    arm.moveArmXYR_jump(pos[0], pos[1], pos[3])


def go_to_home(arm: db.DoBotArm):
    """
    Moves the robotic arm to the home position.

    Args:
    -   arm (db.DoBotArm): The robotic arm object.

    Returns:
    -   None
    """
    move_arm_Z(arm, 30)
    arm.moveHome()


def go_to_cell(arm: db.DoBotArm, pos: tuple):
    """
    Moves the DoBotArm to the specified cell position.

    Args:
    -   arm (db.DoBotArm): The DoBotArm object.
    -   pos (tuple): The target cell position (x, y, z, r).

    Returns:
    -   None
    """

    move_arm_Z(arm, z_picked)
    move_arm_XYR_jump(arm, pos)
    move_arm_Z(arm, pos[2])


def go_to_cell_str(arm: db.DoBotArm, move: str):
    """
    Moves the DoBotArm to the specified cell position.

    Args:
    -   arm (db.DoBotArm): The DoBotArm object.
    -   pos (str): The target cell position in the format 'x_y'.

    Returns:
    -   None
    """

    go_to_cell(arm, coordinates_dict[move])


def go_to_cell_castling(arm: db.DoBotArm, pos: tuple):
    """
    Moves the DoBotArm to the specified cell position.

    Args:
    -   arm (db.DoBotArm): The DoBotArm object.
    -   pos (tuple): The target cell position (x, y, z, r).

    Returns:
    -   None
    """

    # move_arm_Z(arm, z_picked)
    move_arm_XYR(arm, pos)
    move_arm_Z(arm, pos[2])


def go_to_calibration(arm: db.DoBotArm):
    """
    Moves the robotic arm to the calibration position.

    Args:
    -   arm (db.DoBotArm): The robotic arm object.

    Returns:
    -   None
    """

    go_to_cell(arm, calibration_coordinate)


def remove_killed(arm: db.DoBotArm, pos: tuple):
    """
    Moves the robotic arm to the specified position on the chessboard,
    removes the killed piece from that position, and moves the piece to the graveyard.

    Args:
    -   arm (db.DoBotArm): The robotic arm object.
    -   pos (str): The position of the killed piece on the chessboard.

    Returns:
    -   None
    """

    go_to_cell(arm, pos)
    toggle_suction(arm)
    move_arm_Z(arm, z_picked)
    go_to_graveyard(arm)


def go_to_graveyard(arm: db.DoBotArm):
    """
    Moves the robotic arm to the graveyard position.

    Args:
    -   arm (db.DoBotArm): The robotic arm object.

    Returns:
    -   None
    """
    go_to_home(arm)
    toggle_suction(arm)


def castling_move(arm: db.DoBotArm, move: str):
    """
    Applies castling on the chessboard using the robotic arm.

    Args:
    -   arm (db.DoBotArm): The robotic arm object.
    -   move (str): The move to be applied in the format 'src_dest'.

    Returns:
    -   None
    """
    src_str = move[0] + move[1]
    dest_str = move[2] + move[3]
    src = coordinates_dict[src_str]
    dest = coordinates_dict[dest_str]

    # go_to_cell(arm, src)
    # toggle_suction(arm)
    # go_to_cell(arm, dest)
    # toggle_suction(arm)

    if dest_str[0] == "a":
        go_to_cell_castling(arm, src)
        toggle_suction(arm)
        move_arm_Z(arm, z_picked)
        go_to_cell_castling(arm, coordinates_dict["c" + dest[1]])
        toggle_suction(arm)
        # move_arm_Z(arm, z_picked)
        go_to_cell_castling(arm, dest)
        toggle_suction(arm)
        go_to_cell_castling(arm, coordinates_dict["d" + dest[1]])
        toggle_suction(arm)
    else:
        go_to_cell_castling(arm, src)
        toggle_suction(arm)
        go_to_cell_castling(arm, coordinates_dict["g" + dest[1]])
        toggle_suction(arm)
        go_to_cell_castling(arm, dest)
        toggle_suction(arm)
        go_to_cell_castling(arm, coordinates_dict["f" + dest[1]])
        toggle_suction(arm)


def apply_move(arm: db.DoBotArm, move: str, indicators: tuple):
    """
    Applies the specified move on the chessboard using the robotic arm and goes back to the home position after finishing.

    Args:
    -   arm (db.DoBotArm): The robotic arm object.
    -   move (str): The move to be applied in the format 'src_dest'.
    -   indicators (tuple): A tuple containing the indicators for the move (killing, enpassant, castling).

    Returns:
    -   None
    """

    src_str = move[0] + move[1]
    dest_str = move[2] + move[3]
    src = coordinates_dict[src_str]
    dest = coordinates_dict[dest_str]

    if indicators[0] == True:
        remove_killed(arm, dest)
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, dest)
        toggle_suction(arm)

    if indicators[1] == True:
        passant = coordinates_dict[dest_str[0] + str(int(dest_str[1]) + 1)]
        remove_killed(arm, passant)
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, dest)

    if indicators[2] == True:
        castling_move(arm, move)

    if indicators[0] == False and indicators[1] == False and indicators[2] == False:
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, dest)
        toggle_suction(arm)

    go_to_home(arm)


def disconnect(arm: db.DoBotArm):
    """
    Disconnects the Dobot arm.

    Args:
    -   arm (db.DoBotArm): The Dobot arm object.

    Returns:
    -   None
    """
    arm.setSuction(False)
    arm.dobotDisconnect()


def connect(arm: db.DoBotArm):
    """
    Connects the Dobot arm.

    Args:
    -   arm (db.DoBotArm): The Dobot arm object.

    Returns:
    -   None
    """
    arm.dobotConnect()
