import os
import chess
from stockfish import Stockfish

fen = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1' # Example fen
board = chess.Board() # Initialize Board
stockfish = Stockfish(os.environ.get("STOCKFISH_PATH", "stockfish")) # Path of stockfish.exe
stockfish.set_depth(20) # How deep the AI looks
stockfish.set_skill_level(20) # Highest rank stockfish

while board.outcome() == None : # While game has not ended
    board.set_fen(fen) # Set board to obtained fen
    stockfish.set_fen_position(fen) # Set engine to obtained fen
    move = stockfish.get_best_move() # Evaluate best move
    board.push_san(move) # Make the move on the board
    newFen = board.fen() # Get new fen after the move was done and send it to the arm and interfacesud  