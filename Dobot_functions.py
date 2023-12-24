import Dobot_main.DoBotArm as db

""" 
Todo: 
    1. Make a function that performs a move
        a. If kill == 1, remove the killed piece from the board, then move the the eating piece. 
        b. If kill == 0, move piece directly.
        c. If castling, move king first then move rook.
        d. If en passant, remove killed pawn first then move pawn.
        e. To be continued...
            
        1.1. Implement move_piece() function
            - goes to source cell using the angles
            - toggle suction cup
            - goes to destination cell using the angles
            - toggle suction cup
                        
    2. Make a function that moves the arm away for the camera to calibrate
    
    3. Set home cell to a specific coordinates
    
    4. Calculate an offset to add for ranks and files
    
        
    Indicators: 
        - Kill: bool
        - En passant: bool
        - Catling: bool

"""

coordinates_dict = {}


def init_arm(homeX, homeY, homeZ):
    """
    Initializes the DoBot arm with the specified home coordinates.

    Parameters:
    homeX (float): The X coordinate of the home position.
    homeY (float): The Y coordinate of the home position.
    homeZ (float): The Z coordinate of the home position.

    Returns:
    DoBotArm: The initialized DoBot arm object.
    """
    arm = db.DoBotArm(homeX, homeY, homeZ)
    return arm


def move_arm_Z(arm: db.DoBotArm, z):
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
    Moves the arm to the specified X and Y coordinates.

    Parameters:
    arm (db.DoBotArm): The DoBotArm object representing the arm.
    x (float): The X coordinate.
    y (float): The Y coordinate.
    """
    arm.moveArmXY(pos[0], pos[1])


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
    Moves the robotic arm to the specified cell position.

    Parameters:
    arm (db.DoBotArm): The robotic arm object.
    pos (str): The position of the cell in the format 'A1', 'B2', etc.

    Returns:
    None
    """
    move_arm_Z(arm, z_picked)
    move_arm_XY(arm, pos)  # type: ignore
    move_arm_Z(arm, z_piece)


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
    move_arm_Z(arm, z_picked)
    move_arm_XY(arm, pos[0], pos[1])  # type: ignore
    move_arm_Z(arm, z_piece)
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
    move_arm_XY(arm, x_graveyard, y_graveyard)  # type: ignore
    move_arm_Z(arm, z_graveyard)
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

    go_to_home(arm)


def apply_move(
    arm: db.DoBotArm, move: str, kill: bool, castling: bool, enpassant: bool
):
    """
    Applies the specified move on the chessboard using the robotic arm.

    Parameters:
    arm (db.DoBotArm): The robotic arm object.
    move (str): The move to be applied in the format 'src_dest'.
    kill (bool): Indicates if a piece is being killed.
    castling (bool): Indicates if castling is being performed.
    enpassant (bool): Indicates if en passant is being performed.

    Returns:
    None
    """
    src = move[0] + move[1]
    dest = move[2] + move[3]
    src = coordinates_dict[src]
    dest = coordinates_dict[dest]

    if enpassant == True:
        passant = dest[0] + str(int(dest[1]) + 1)
        remove_killed(arm, passant)
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, dest)

    if kill == True:
        remove_killed(arm, dest)
        go_to_cell(arm, src)
        toggle_suction(arm)
        go_to_cell(arm, dest)
        toggle_suction(arm)

    if castling == True:
        castling_move(arm, move)

    if kill == False and castling == False and enpassant == False:
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
    arm.dobotDisconnect()


def get_coordinates(coordinates: dict):
    """
    Retrieves the coordinates and stores them in the global variable coordinates_dict.

    Parameters:
    coordinates (dict): A dictionary containing the coordinates.

    Returns:
    None
    """
    global coordinates_dict
    coordinates_dict = coordinates


homeX, homeY, homeZ = 250, 0, 50

z_piece = 50  # ! Change this value
z_picked = 50  # ! Change this value

x_graveyard = 0
y_graveyard = 175
z_graveyard = 0


def connect(arm: db.DoBotArm):
    """
    Connects the Dobot arm.

    Args:
        arm (db.DoBotArm): The Dobot arm object.

    Returns:
        None
    """
    arm.dobotConnect()
