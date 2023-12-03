import chess  # Importing the chess module
from chess import pgn
from stockfish import (
    Stockfish,
)  # Importing the Stockfish module to use the the stockfish engine


def set_engine_difficulty(stockfish: Stockfish, difficulty_int: int):
    """
    Sets the difficulty level of the Stockfish engine.

    Args:
    -   stockfish (Stockfish): The Stockfish engine object.
    -   difficulty_int (int): The difficulty level as an integer.

    Returns:
    -   stockfish: The modified Stockfish engine object.
    """

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

    board = pgn_game.board()  # Getting the board from the pgn string

    # Iterating through the moves in the pgn string and pushing them to the board
    for move in pgn_game.mainline_moves():
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
