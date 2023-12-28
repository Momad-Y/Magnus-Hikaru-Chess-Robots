import Dobot_main.DoBotArm as db
import xmltodict

coordinates_dict = {}


def init_arm():
    """
    Initializes the DoBot arm.

    Returns:
    arm (DoBotArm): The initialized DoBot arm object.
    """
    arm = db.DoBotArm(homeX, homeY, homeZ)
    arm.setSuction(False)
    return arm


def get_coordinates_from_xml(xml_file_path: str):
    with open(xml_file_path, "r") as file:
        xml_string = file.read()

    xml_dict = xmltodict.parse(xml_string)

    xml_dict = xml_dict["root"]

    # Remove the first 2 elements of the dictionary
    del xml_dict["DobotType"]
    del xml_dict["row_StudioVersion"]

    edited_dict = {}

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

    # Print the dictionary in a format that can be copied and pasted to the code
    for key in edited_dict:
        print(f'"{key}": {edited_dict[key]},')


def move_arm_Z(arm: db.DoBotArm, z: float):
    """
    Moves the arm to a specified height in the Z-axis.

    Parameters:
    arm (db.DoBotArm): The DoBotArm object representing the robotic arm.
    z (float): The desired height in the Z-axis.

    Returns:
    None
    """
    arm.pick(z)


def toggle_suction(arm: db.DoBotArm):
    """
    Toggles the suction on the DoBotArm.

    Parameters:
    arm (db.DoBotArm): The DoBotArm object to toggle the suction on.
    """
    arm.toggleSuction()


def move_arm_XY(arm: db.DoBotArm, pos: tuple):
    """
    Moves the DoBot arm to the specified X and Y coordinates.

    Args:
        arm (db.DoBotArm): The DoBot arm object.
        pos (tuple): A tuple containing the coordinates.

    Returns:
        None
    """
    arm.moveArmXY(pos[0], pos[1], pos[3])


def go_to_home(arm: db.DoBotArm):
    """
    Moves the robotic arm to the home position.

    Parameters:
    arm (db.DoBotArm): The robotic arm object.

    Returns:
    None
    """
    arm.moveHome()


def go_to_cell(arm: db.DoBotArm, pos: tuple):
    """
    Moves the DoBotArm to the specified cell position.

    Args:
        arm (db.DoBotArm): The DoBotArm object.
        pos (tuple): The target cell position (x, y, z, r).
    """
    move_arm_Z(arm, z_picked)
    move_arm_XY(arm, pos)
    move_arm_Z(arm, pos[2])


def remove_killed(arm: db.DoBotArm, pos: tuple):
    """
    Moves the robotic arm to the specified position on the chessboard,
    removes the killed piece from that position, and moves the piece to the graveyard.

    Parameters:
    - arm (db.DoBotArm): The robotic arm object.
    - pos (str): The position of the killed piece on the chessboard.

    Returns:
    None
    """
    go_to_cell(arm, pos)
    toggle_suction(arm)
    move_arm_Z(arm, z_picked)
    go_to_graveyard(arm)


def go_to_graveyard(arm: db.DoBotArm):
    """
    Moves the robotic arm to the graveyard position.

    Parameters:
    arm (db.DoBotArm): The robotic arm object.

    Returns:
    None
    """
    go_to_home(arm)
    toggle_suction(arm)


def castling_move(arm: db.DoBotArm, move: str):
    """
    Applies castling on the chessboard using the robotic arm.

    Parameters:
    arm (db.DoBotArm): The robotic arm object.
    move (str): The move to be applied in the format 'src_dest'.

    Returns:
    None
    """
    src_str = move[0] + move[1]
    dest_str = move[2] + move[3]
    src = coordinates_dict[src_str]
    dest = coordinates_dict[dest_str]

    go_to_cell(arm, src)
    toggle_suction(arm)
    go_to_cell(arm, dest)
    toggle_suction(arm)

    if dest_str[0] == "a":
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, coordinates_dict["c" + dest[1]])
        toggle_suction(arm)
        go_to_cell(arm, dest)
        toggle_suction(arm)
        go_to_cell(arm, coordinates_dict["d" + dest[1]])
        toggle_suction(arm)
    else:
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, coordinates_dict["g" + dest[1]])
        toggle_suction(arm)
        go_to_cell(arm, dest)
        toggle_suction(arm)
        go_to_cell(arm, coordinates_dict["f" + dest[1]])
        toggle_suction(arm)


def apply_move(arm: db.DoBotArm, move: str, indicators: tuple):
    """
    Applies the specified move on the chessboard using the robotic arm and goes back to the home position after finishing.

    Parameters:
    arm (db.DoBotArm): The robotic arm object.
    move (str): The move to be applied in the format 'src_dest'.
    kill (bool): Indicates if a piece is being killed.
    castling (bool): Indicates if castling is being performed.
    enpassant (bool): Indicates if en passant is being performed.

    Returns:
    None
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
        passant = dest_str[0] + str(int(dest_str[1]) + 1)
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
        arm (db.DoBotArm): The Dobot arm object.

    Returns:
        None
    """
    arm.setSuction(False)
    arm.dobotDisconnect()


def connect(arm: db.DoBotArm):
    """
    Connects the Dobot arm.

    Args:
        arm (db.DoBotArm): The Dobot arm object.

    Returns:
        None
    """
    arm.dobotConnect()


homeX, homeY, homeZ = 250, 0, 50  # !!: Change this value

z_picked = 50  # !!: Change this value
