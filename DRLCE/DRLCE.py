"""
This file contains the main function for playing chess against the computer or watching self play games.
"""

import chess
import DRLCE.MCTS as MCTS
import torch
import DRLCE.AlphaZeroNetwork as AlphaZeroNetwork

rollouts = 10  # number of rollouts on computers turn
threads = 1  # number of threads used per rollout


def get_best_move(weights_file: str, board: chess.Board) -> chess.Move:
    """
    Returns the best move for the given chess board using the AlphaZero algorithm.

    Parameters:
    -   weights_file (str): The file path to the model weights.
    -   board (chess.Board): The chess board to evaluate.

    Returns:
    -   chess.Move: The best move for the given board.
    """

    # Initialize the neural network with the AlphaZero architecture
    alphaZeroNet = AlphaZeroNetwork.AlphaZeroNet(20, 256)

    weights = torch.load(
        weights_file, map_location=torch.device("cpu")
    )  # load the model weights

    alphaZeroNet.load_state_dict(weights)  # load the weights into the model

    # Freeze the weights so they are not updated during self play
    for param in alphaZeroNet.parameters():
        param.requires_grad = False

    # Set the model to evaluation mode
    alphaZeroNet.eval()

    # Get the best move from the MCTS algorithm
    with torch.no_grad():
        root = MCTS.Root(
            board, alphaZeroNet
        )  # Initialize the root node of the MCTS tree

        # Run the MCTS algorithm for num_rollouts iterations
        for i in range(rollouts):
            root.parallelRollouts(board.copy(), alphaZeroNet, threads)

    # Get the best move from the edge with the highest N value
    edge = root.maxNSelect()
    bestmove = edge.getMove()  # type: ignore

    return bestmove  # Return the best move
