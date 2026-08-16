import CE as ce

board = ce.init_board()

ce.set_board_from_fen(board, "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

print(board)

while True:
    x = input("Enter move: ")
    ce.make_move(board, x)
    print(board)
