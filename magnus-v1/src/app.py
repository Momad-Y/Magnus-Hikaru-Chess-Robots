from flask import Flask, render_template, request as requestFlask
import json
import os
import chess
import time
from stockfish import Stockfish
from engine_path import find_stockfish

import C2M as c2m

# import ARM as arm

board = chess.Board()
stockfish = Stockfish(find_stockfish())
# Templates and static assets live in ../web/, one level up from src/.
_WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
app = Flask(
    __name__,
    template_folder=os.path.join(_WEB, "templates"),
    static_folder=os.path.join(_WEB, "static"),
)

go = False  # Received from js
difficulty = 0  # Received from js
resign = False  # Received from js
playerTurn = True  # Received from js, White
playerMove = ""  # Received from js

fen = board.fen()  # Send from py to js
situation = 69  # Send from py to js

prevImg = []
curImg = []
homography = []
moves = []
actualMove = ""
bestMove = ""
kill = False
nameQueue = []
dataQueue = []


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/links")
def links():
    return render_template("links.html")


@app.route("/play")
def play():
    reset()
    return render_template("play.html")


@app.route("/update")
def send():
    global nameQueue
    global dataQueue

    try:
        name = nameQueue.pop()
        data = dataQueue.pop()
        return {
            "name": name,
            "data": data,
        }
    except Exception:
        return "{}"


@app.route("/process/<string:data>/<string:name>", methods=["POST"])
def process(data, name):
    global go
    global difficulty
    global resign
    global playerTurn
    global playerMove

    data = json.loads(data)
    name = json.loads(name)

    if name == "go":
        go = data
        print("Go", go, type(go))

        if go == True:
            calibrate()
        else:
            return "/"

    if name == "difficulty":
        difficulty = data
        print("Difficulty", difficulty, type(difficulty))

        if difficulty >= 1 and difficulty <= 4:
            processPrevImg()
            setDifficulty()
        else:
            return "/"

    if name == "playerTurn":
        playerTurn = data
        print("playerTurn", playerTurn, type(playerTurn))

        if playerTurn == False and playerMove == "":
            playing()
        else:
            return "/"

    if name == "resign":
        resign = data
        print("Resign", resign, type(resign))

        if resign == True:
            reset()
            print("White resigned")
        else:
            return "/"

    if name == "playerMove":
        playerMove = data
        print("playerMove", playerMove, type(playerMove))

        if playerMove != "":
            played()
        else:
            return "/"

    return "/"


def calibrate():
    global homography
    global nameQueue
    global dataQueue

    emptyImg = c2m.takePic()
    if emptyImg == -1:
        print("Camera Error")
        # nameQueue.insert(0, "error")
        # dataQueue.insert(0, 12)
        return

    c2m.showImg(emptyImg, "Empty Chess Board Image")
    homography = c2m.findHomography(emptyImg)

    if homography == -1:
        print("Calibration Error")
        nameQueue.insert(0, "error")
        dataQueue.insert(0, 55)
        return

    c2m.showImg(
        c2m.applyHomography(emptyImg, homography), "Empty chessboard image warped"
    )


def setDifficulty():
    global difficulty

    stockfish.set_depth(difficulty * 5)
    stockfish.set_skill_level(difficulty * 5)
    print("Engine Depth and skill level:", difficulty * 5)


def processPrevImg():
    global prevImg
    global homography

    prevImg = c2m.takePic()
    if prevImg == -1:
        print("Camera Error")
        # nameQueue.insert(0, "error")
        # dataQueue.insert(0, 12)
        return

    c2m.showImg(prevImg, "Full chessboard image")
    prevImg = c2m.applyHomography(prevImg, homography)
    c2m.showImg(prevImg, "Full chessboard image warped")


def processCurImg():
    global curImg
    global homography

    curImg = c2m.takePic()
    if curImg == -1:
        print("Camera Error")
        # nameQueue.insert(0, "error")
        # dataQueue.insert(0, 12)
        return

    c2m.showImg(curImg, "Full chessboard image")
    curImg = c2m.applyHomography(curImg, homography)
    c2m.showImg(curImg, "Full chessboard image warped")


def ACN(moves):
    global board
    global kill

    actualMove = firstSq = ""

    if len(moves) == 2:
        if str(board.piece_at(chess.parse_square(moves[0]))).isupper():
            actualMove = moves[0] + moves[1]
        elif str(board.piece_at(chess.parse_square(moves[1]))).isupper():
            actualMove = moves[1] + moves[0]

        if str(board.piece_at(chess.parse_square(actualMove[2:]))).islower():
            kill = True

    if len(moves) == 3:
        kill = True

        if str(board.piece_at(chess.parse_square(moves[0]))).isupper():
            firstSq = moves[0]
        elif str(board.piece_at(chess.parse_square(moves[1]))).isupper():
            firstSq = moves[1]
        elif str(board.piece_at(chess.parse_square(moves[2]))).isupper():
            firstSq = moves[2]

        if str(board.piece_at(chess.parse_square(moves[0]))) == "None":
            actualMove = firstSq + moves[0]
        elif str(board.piece_at(chess.parse_square(moves[1]))) == "None":
            actualMove = firstSq + moves[1]
        elif str(board.piece_at(chess.parse_square(moves[2]))) == "None":
            actualMove = firstSq + moves[2]

    if len(moves) == 4:
        kill = False

        if "a1" in moves:
            actualMove = "e1" + "a1"
        elif "h1" in moves:
            actualMove = "e1" + "h1"

    return actualMove


def reset():
    global go
    global difficulty
    global resign
    global playerTurn
    global prevImg
    global curImg
    global homography
    global moves
    global fen
    global actualMove
    global bestMove
    global playerMove
    global kill
    global situation
    global dataQueue
    global nameQueue
    global board

    go = False
    difficulty = 0
    resign = False
    playerTurn = True
    playerMove = ""
    prevImg = []
    curImg = []
    homography = []
    moves = []
    fen = board.fen()
    actualMove = ""
    bestMove = ""
    kill = False
    situation = 69
    dataQueue = []
    nameQueue = []
    board = chess.Board()


def checkOutcome():
    global board
    global situation

    outcome = board.outcome()

    if outcome:
        if outcome.winner == chess.WHITE:
            print("white won")
            situation = 1
            nameQueue.insert(0, "situation")
            dataQueue.insert(0, situation)

        elif outcome.winner == chess.BLACK:
            print("black won")
            situation = 0
            nameQueue.insert(0, "situation")
            dataQueue.insert(0, situation)
        else:
            print("draw")
            situation = -1
            nameQueue.insert(0, "situation")
            dataQueue.insert(0, situation)

        reset()

        return True

    else:
        return False


def playing():
    global prevImg
    global curImg
    global moves
    global actualMove
    global bestMove
    global fen
    global kill

    processCurImg()

    moves, _ = c2m.findMoves(prevImg, curImg)
    actualMove = ACN(moves)

    try:
        board.push_san(actualMove)
    except:
        print("Move Error")
        nameQueue.insert(0, "error")
        dataQueue.insert(0, 100)
        return

    fen = board.fen()
    nameQueue.insert(0, "fen")
    dataQueue.insert(0, fen)

    if checkOutcome() == True:
        return

    stockfish.set_fen_position(fen)
    bestMove = stockfish.get_best_move()
    board.push_san(bestMove)

    # arm.moveArm(bestMove, kill)

    fen = board.fen()
    nameQueue.insert(0, "fen")
    dataQueue.insert(0, fen)

    if checkOutcome() == True:
        return

    processPrevImg()


def played():
    global curImg
    global bestMove
    global fen
    global playerMove
    global kill

    time.sleep(2)

    try:
        board.push_san(playerMove)
    except:
        print("Move Error")
        nameQueue.insert(0, "error")
        dataQueue.insert(0, 101)
        return

    if str(board.piece_at(chess.parse_square(playerMove[2:]))).islower():
        kill = True

    if checkOutcome() == True:
        return

    fen = board.fen()
    stockfish.set_fen_position(fen)
    bestMove = stockfish.get_best_move()
    board.push_san(bestMove)
    print("The best move is: ", bestMove)

    # arm.moveArm(bestMove, kill)

    fen = board.fen()
    nameQueue.insert(0, "fen")
    dataQueue.insert(0, fen)

    if checkOutcome() == True:
        return

    processPrevImg()

    playerMove = ""

    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9999)
