import chess  # Importing the chess module
from chess import (
    pgn,
    svg,
)  # Importing the pgn and svg modules from chess
from stockfish import (
    Stockfish,
)  # Importing the Stockfish module to use the Stockfish engine
import cairosvg  # Importing the cairosvg module to convert svg to png
import cv2  # Importing the cv2 module to display the chess board
import numpy as np  # Importing the numpy module to convert png to numpy array
from PIL import (
    Image,
    ImageTk,
)  # Importing the Image and ImageTk modules to display the chess board


def init_stockfish(stockfish_path_str: str):
    """
    Initializes the Stockfish engine.

    Args:
    -   stockfish_path_str (str): The path to the Stockfish engine.

    Returns:
    -   Stockfish: The Stockfish engine object.
    """

    stockfish = Stockfish(stockfish_path_str)  # Initializing the Stockfish engine

    return stockfish  # Returning the stockfish object


def init_board():
    """
    Initializes the chess board.

    Returns:
    -   chess.Board: The chess board object.
    """

    board = chess.Board()  # Initializing the chess board

    return board  # Returning the board object


def set_board_from_fen(board: chess.Board, fen_str: str):
    """
    Sets the state of the chess board from a FEN string.

    Args:
    -   board (chess.Board): The chess board object to be updated.
    -   fen_str (str): The FEN string.

    Returns:
    -   chess.Board: The updated chess board object.
    """

    board.set_fen(fen_str)  # Setting the board from the FEN string

    return board  # Returning the edited board object


def set_engine_difficulty(stockfish: Stockfish, difficulty_int: int):
    """
    Sets the difficulty level of the Stockfish engine.

    Args:
    -   stockfish (Stockfish): The Stockfish engine object.
    -   difficulty_int (int): The difficulty level as an integer.

    Returns:
    -   stockfish: The modified Stockfish engine object.
    """

    if difficulty_int == 5:  # Checking if the difficulty is 5
        difficulty_int = 1  # Test

    stockfish.set_depth(difficulty_int * 5)  # Setting the depth of the engine
    stockfish.set_skill_level(
        difficulty_int * 5
    )  # Setting the skill level of the engine

    return stockfish  # Returning the edited stockfish object


def check_move(board: chess.Board, move_str: str):
    """
    Check if a move is valid on the given chess board.

    Parameters:
    -   board (chess.Board): The chess board to check the move on.
    -   move_str (str): The move to be checked in UCI format.

    Returns:
    -   bool: True if the move is valid, False otherwise.
    """

    if len(move_str) != 4:  # Checking if the length of the move is 4
        return False

    move_uci = chess.Move.from_uci(move_str)  # Converting the move to UCI format

    if move_uci in board.legal_moves:  # Checking if the move is valid
        return True  # Returning True if the move is valid

    return False  # Returning False if the move is invalid


def check_game_state(board: chess.Board):
    """
    Check the game state and print the board, game state, and outcome of the game.

    Parameters:
    -   board (chess.Board): The chess board to check the game state for.

    Returns:
    -   int: 0 if the game is in progress, 1 if black won, 2 if white won, 3 if draw.
    """

    outcome_str = str(
        board.outcome(claim_draw=True)
    )  # Getting the outcome of the game as a string

    # Checking if the game is not over
    if outcome_str == "None":
        return 0  # Returning 0 if the game is not over

    # Get the value between the brackets of the outcome string <>
    outcome_str_winner = outcome_str[outcome_str.find("winner=") + 7 : -1]
    outcome_str = outcome_str[outcome_str.find("<") + 1 : outcome_str.find(">")]
    outcome_str = outcome_str[outcome_str.find(".") + 1 : outcome_str.find(":")]

    if outcome_str == "CHECKMATE":
        if outcome_str_winner == "True":
            return 2  # Returning 2 if white won
        elif outcome_str_winner == "False":
            return 1  # Returning 1 if black won

    else:
        return 3  # Returning 3 if draw


def make_move(board: chess.Board, move_str: str):
    """
    Makes a move on the chess board.

    Args:
    -   board (chess.Board): The current state of the chess board.
    -   move_str (str): The move to be made in UCI format.

    Returns:
    -   chess.Board: The updated chess board after making the move.
    """

    move_uci = chess.Move.from_uci(move_str)  # Converting the move to UCI format

    board.push(move_uci)  # Pushing the move to the board

    return board  # Returning the edited board object


def set_board_from_pgn(board: chess.Board, pgn_path_str: str):
    """
    Sets the state of the chess board by reading moves from a PGN file.

    Args:
    -   board (chess.Board): The chess board object to be updated.
    -   pgn_path_str (str): The path to the PGN file.

    Returns:
    -   chess.Board: The updated chess board object.
    """

    pgn_file = open(pgn_path_str)  # Opening the pgn file

    pgn_game = pgn.read_game(pgn_file)  # Reading the pgn string

    board = pgn_game.board()  # type: ignore  # Getting the board from the pgn string

    # Iterating through the moves in the pgn string and pushing them to the board
    for move in pgn_game.mainline_moves():  # type: ignore
        board.push(move)

    return board  # Returning the edited board object


def get_best_move(stockfish: Stockfish, board: chess.Board):
    """
    Gets the best move from the Stockfish engine.

    Args:
    -   stockfish (Stockfish): The Stockfish engine object.
    -   board (chess.Board): The current state of the chess board.

    Returns:
    -   str: The best move in UCI format.
    """

    stockfish.set_fen_position(
        board.fen()
    )  # Setting the position of the stockfish engine

    best_move = stockfish.get_best_move()  # Getting the best move from the engine

    return best_move  # Returning the best move


def check_indicators(board: chess.Board, move_str: str):
    """
    Checks if the move is a kill, enpassant, castling.

    Args:
    -   board (chess.Board): The current state of the chess board.
    -   move_str (str): The move to be checked in UCI format.

    Returns:
    -   tuple: A tuple of booleans indicating if the move is a kill, enpassant, castling.
    """

    indicators = (False, False, False)  # Initializing the indicators as False
    move_uci = chess.Move.from_uci(move_str)  # Converting the move to UCI format

    if board.is_castling(move_uci):  # Checking if the move is castling
        indicators = (False, False, True)  # Setting the castling indicator to False

    if board.is_capture(move_uci):  # Checking if the move is a capture
        indicators = (True, False, False)  # Setting the kill indicator to True

    if board.is_en_passant(move_uci):  # Checking if the move is an en passant move
        indicators = (False, True, False)  # Setting the en passant indicator to True

    return indicators  # Returning the edited indicators


def get_board_img(board: chess.Board):
    """
    Displays the chess board.

    Args:
    -   board (chess.Board): The chess board object to be displayed.

    Returns:
    -   board_tk (np.ndarray): The tkinter image of the chess board.
    """

    # Convert the board to SVG
    svg_board = svg.board(board=board)

    # Convert the SVG to PNG
    png_bytes = cairosvg.svg2png(bytestring=svg_board)

    # Convert the PNG to a numpy array
    png_array = cv2.imdecode(np.frombuffer(png_bytes, np.uint8), cv2.IMREAD_UNCHANGED)  # type: ignore

    # Resize the numpy array to 400x400
    png_array = cv2.resize(png_array, (400, 400))

    # Convert the numpy array to a tkinter image
    board_tkimg = ImageTk.PhotoImage(image=Image.fromarray(png_array))

    return board_tkimg  # Returning the board image


def moves_to_ACN(board: chess.Board, moves_list: list):
    """
    Converts a move from a chess board to Algebraic Chess Notation (ACN) format.

    Args:
    -   board (chess.Board): The chess board.
    -   moves_list (list): The list of moves.

    Returns:
    -   str: The move in ACN format.
    """

    move_ACN = ""  # Initializing the move in ACN format as an empty string

    # If the length of the moves list is 2 then the move is a normal move or a capture move for white
    if len(moves_list) == 2:
        if str(board.piece_at(chess.parse_square(moves_list[0]))).isupper():
            move_ACN = moves_list[0] + moves_list[1]
        elif str(board.piece_at(chess.parse_square(moves_list[1]))).isupper():
            move_ACN = moves_list[1] + moves_list[0]

    # If the length of the moves list is 3 then the move is an en passant move for white
    if len(moves_list) == 3:
        # If the move is an en passant move then the first square is the square of the white pawn
        if str(board.piece_at(chess.parse_square(moves_list[0]))).isupper():
            first_square_en_passant = moves_list[0]
        elif str(board.piece_at(chess.parse_square(moves_list[1]))).isupper():
            first_square_en_passant = moves_list[1]
        elif str(board.piece_at(chess.parse_square(moves_list[2]))).isupper():
            first_square_en_passant = moves_list[2]

        # If the move is an en passant move then the second square is the empty square
        if str(board.piece_at(chess.parse_square(moves_list[0]))) == "None":
            move_ACN = first_square_en_passant + moves_list[0]  # type: ignore
        elif str(board.piece_at(chess.parse_square(moves_list[1]))) == "None":
            move_ACN = first_square_en_passant + moves_list[1]  # type: ignore
        elif str(board.piece_at(chess.parse_square(moves_list[2]))) == "None":
            move_ACN = first_square_en_passant + moves_list[2]  # type: ignore

    # If the length of the moves list is 4 then the move is a castling move for white
    if len(moves_list) == 4:
        # If the castling move is queenside then the move is "e1a1"
        if "a1" in moves_list:
            move_ACN = "e1" + "a1"
        # If the castling move is kingside then the move is "e1h1"
        elif "h1" in moves_list:
            move_ACN = "e1" + "h1"

    return move_ACN  # Returning the move in ACN format
