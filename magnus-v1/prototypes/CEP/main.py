import os
import chess
from stockfish import Stockfish
from C2M import demo

# White Turn : 1
# Black Turn : 0


board = chess.Board()  # Initialize Board

# Path of stockfish.exe
stockfish = Stockfish(
    os.environ.get("STOCKFISH_PATH", "stockfish"))

dif = 0  # Difficulty level set by the interface
turn = 1  # Turn of the player
cal = 0  # Calibration Authentication
resign = 0 # Resignation Variable
fen = board.fen()  # Get fen from web app

'''boardMan = [['r','n','b','q','k','b','n','r'],
             ['p','p','p','p','p','p','p','p'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['P','P','P','P','P','P','P','P'],
             ['R','N','B','Q','K','B','N','R']]'''


boardMan = {'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r',
            'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p',
            'a6': '.', 'b6': '.', 'c6': '.', 'd6': '.', 'e6': '.', 'f6': '.', 'g6': '.', 'h6': '.',
            'a5': '.', 'b5': '.', 'c5': '.', 'd5': '.', 'e5': '.', 'f5': '.', 'g5': '.', 'h5': '.',
            'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.', 'f4': '.', 'g4': '.', 'h4': '.',
            'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.', 'f3': '.', 'g3': '.', 'h3': '.',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R'}


def difficulty():
    stockfish.set_depth(dif*5)
    stockfish.set_skill_level(dif*5)


while cal == 1:  # Recieve calibration var when difficulty is set
    difficulty(dif)
    # fen = board.fen()
    while board.outcome() == None and turn == 0 and resign != 0:  # While game has not ended
        # board.set_fen(fen) # Set board to obtained fen
        newMoves, _ = demo()
        if len(newMoves) == 2:
            if boardMan[newMoves[0]] == '.':
                boardMan[newMoves[0]] = boardMan[newMoves[1]]
                boardMan[newMoves[1]] = '.'
            elif boardMan[newMoves[1]] == '.':
                boardMan[newMoves[1]] = boardMan[newMoves[0]]
                boardMan[newMoves[0]] = '.'

        elif len(newMoves) == 3:
            
        elif len(newMoves) == 4:
            
        stockfish.set_fen_position(fen)  # Set engine to obtained fen
        move = stockfish.get_best_move()  # Evaluate best move
        board.push_san(move)  # Make the move on the board
        # print(board)
        print(stockfish.get_board_visual())
        fen = board.fen()  # Get new fen after the move was done and send it to the arm and interface
        turn = 1

    # print(board.outcome())



    