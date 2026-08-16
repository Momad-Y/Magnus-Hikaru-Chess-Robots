const request = new XMLHttpRequest();

var config = {
	position: "start",
	draggable: true,
	onDrop: onDrop,
};

var board = Chessboard("board", config);

var sleep = (ms) => new Promise((res) => setTimeout(res, ms));

var popupCalibration = document.getElementById("popupCalibration");
var popupPieces = document.getElementById("popupPieces");
var popupStatus = document.getElementById("popupStatus");
var statusHeader = document.getElementById("statusHeader");
var statusP = document.getElementById("statusP");
var statusBtn = document.getElementById("statusBtn");
var popupError = document.getElementById("popupError");
var errorP = document.getElementById("errorP");
var errorBtn = document.getElementById("errorBtn");
var btnTag = document.getElementById("btnCalibration");
var turnA = document.getElementById("turnA");
var turn = document.getElementById("turn");

var go = false; // Send to python
var difficulty = 0; // Send to python
var resign = false; // Send to python
var playerTurn = true; // Send to python
var takeControlVar = false;
var playerMove = "";
var oldPosition;

var script = false;
var openings = [
	["c7-c5", "d7-d6", "e7-e5", "g8-f6", "b8-c6"],
	["g8-f6", "f6-d5", "b8-a6", "d7-d6", "c7-c5"],
];
var randomOpening;
var data = {
	name: "",
	data: 0,
};

function delay(milliseconds) {
	const date = Date.now();
	let currentDate = null;
	do {
		currentDate = Date.now();
	} while (currentDate - date < milliseconds);
}

window.onload = function () {
	go = true;
	post(go, "go");
	chkInternetStatus();
	start();
	if (script == true) takeControlVar = true;
	fetchData();
};

function chkInternetStatus() {
	if (!navigator.onLine) {
		alert("You're offline. You won't be able to use the chat feature");
	}
}

function takeControl() {
	if (script == true) {
		return;
	}
	if (takeControlVar == false && playerTurn == true) {
		takeControlVar = true;
	} else if (takeControlVar == true || playerTurn == false) {
		takeControlVar = false;
	}
}

function post(data, name) {
	request.open(
		"POST",
		`/process/${JSON.stringify(data)}/${JSON.stringify(name)}`
	);
	request.send();
}

function get() {
	var data;
	var name;
	var flag = false;

	while (!flag) {
		request.open(
			"GET",
			`/process/${JSON.stringify(data)}/${JSON.stringify(name)}`
		);
		request.send();

		console.log(data, name);
	}
}

function playOpenings() {
	board.move(openings[randomOpening][turn - 1]);
	turn++;
}

function onDrop(source, target, piece, newPos, oldPos, orientation) {
	if (piece.search(/b/) !== -1 || takeControlVar == false) {
		return "snapback";
	} else if (takeControlVar == true && piece.search(/w/) !== -1) {
		playerMove = source + target;
		board.position(Chessboard.objToFen(newPos), false);
		post(playerMove, "playerMove");
		// takeControlVar = false;
		oldPosition = oldPos;
	}
}

function start() {
	$(".btnCalibration").addClass("disabled");
	$(".cardChild").addClass("disabled");
	$(".navMenu").addClass("disabled");
	$("chatWindow").addClass("disabled");
	openPopupCalibration();
	setTimeout(enableCalibrationButton, 3000);
}

function openPopupCalibration() {
	popupCalibration.classList.add("open-popup");
}

function closePopupCalibration() {
	popupCalibration.classList.remove("open-popup");
	setTimeout(openPopupPieces, 1200);
}

function openPopupPieces() {
	popupPieces.classList.add("open-popup");
}

function closePopupPieces() {
	popupPieces.classList.remove("open-popup");
	piecesOnBoard = true;
	$(".cardChild").removeClass("disabled");
	$(".navMenu").removeClass("disabled");
	$("chatWindow").removeClass("disabled");
	var message = greetings[Math.floor(Math.random() * 8)];
	setTimeout(
		sendDataBot,
		Math.floor(Math.random() * (1500 - 750 + 1)) + 750,
		message
	);
}

function enableCalibrationButton() {
	$(".btnCalibration").removeClass("disabled");
	btnTag.innerHTML = "Done";
}

function chooseDifficulty(tag) {
	if (tag.id === "easy") {
		difficulty = 1;
	} else if (tag.id === "normal") {
		difficulty = 2;
	} else if (tag.id === "hard") {
		difficulty = 3;
	} else if (tag.id === "veryHard") {
		difficulty = 4;
	}
	post(difficulty, "difficulty");
}

function stateSleep(tag) {
	$(".cardChild").addClass("disabled");
	$(".navMenu").addClass("disabled");
	if (tag.id === "draw") {
		setTimeout(
			openPopupStatus,
			Math.floor(Math.random() * (1500 - 750 + 1)) + 750,
			tag
		);
	} else {
		setTimeout(openPopupStatus, 500, tag);
	}
}

function openPopupStatus(tag) {
	$(".cardChild").addClass("disabled");
	$(".navMenu").addClass("disabled");
	if (tag.id === "resign") {
		statusHeader.innerHTML = "Black Won";
		statusP.innerHTML = "Better luck next time";
		statusBtn.innerHTML = "Redirecting to home";
		statusBtn.setAttribute("onclick", "location.href='/'");
		resign = true;
		post(resign, "resign");
		setTimeout(() => {
			window.location.replace("/");
		}, 3000);
	} else if (tag.data === 0) {
		statusHeader.innerHTML = "Black Won";
		statusP.innerHTML = "Better luck next time";
		statusBtn.innerHTML = "Redirecting to home";
		statusBtn.setAttribute("onclick", "location.href='/'");
		setTimeout(() => {
			window.location.replace("/");
		}, 3000);
	} else if (tag.data === 1) {
		statusHeader.innerHTML = "White Won";
		statusP.innerHTML = "Good Game";
		statusBtn.innerHTML = "Redirecting to home";
		statusBtn.setAttribute("onclick", "location.href='/'");
		setTimeout(() => {
			window.location.replace("/");
		}, 3000);
	} else if (tag.data === -1) {
		statusHeader.innerHTML = "Draw";
		statusP.innerHTML = "Good Game";
		statusBtn.innerHTML = "Redirecting to home";
		statusBtn.setAttribute("onclick", "location.href='/'");
		setTimeout(() => {
			window.location.replace("/");
		}, 3000);
	}
	popupStatus.classList.add("open-popup");
}

function closePopupStatus() {
	popupStatus.classList.remove("open-popup");
	$(".cardChild").removeClass("disabled");
	$(".navMenu").removeClass("disabled");
}

function openPopupError(errorNum) {
	$(".navMenu").addClass("disabled");
	$(".cardChild").addClass("disabled");
	if (errorNum === 12) {
		errorP.innerHTML = "Error 12: Camera Not Found";
		errorBtn.innerHTML = "Redirecting to home";
		errorBtn.setAttribute("onclick", "");
		setTimeout(() => {
			window.location.replace("/");
		}, 3000);
	} else if (errorNum === 55) {
		errorP.innerHTML = "Error 55: Couldn't Calibrate";
		errorBtn.innerHTML = "Redirecting to home";
		errorBtn.setAttribute("onclick", "");
		setTimeout(() => {
			window.location.replace("/");
		}, 3000);
	} else if (errorNum === 100) {
		errorP.innerHTML = "Error 100: Incorrect Move";
		errorBtn.innerHTML = "Take Control";
		errorBtn.setAttribute("onclick", "closePopupError()");
	} else if (errorNum === 101) {
		board.position(Chessboard.objToFen(oldPosition), false);
		errorP.innerHTML = "Error 101: Incorrect Move on Web";
		errorBtn.innerHTML = "Return to the Game";
		errorBtn.setAttribute("onclick", "closePopupError()");
	}
	popupError.classList.add("open-popup");
}

function closePopupError() {
	$(".cardChild").removeClass("disabled");
	$(".navMenu").removeClass("disabled");
	popupError.classList.remove("open-popup");
}

function changeTurn() {
	// If is the players turn and he pressed it then make it the arms turn
	console.log("Hi");
	if (playerTurn === true) {
		playerTurn = false;
		takeControlVar = false;
		$("#turnA").addClass("disabled");
		turn.setAttribute("src", "/static/img/blackTurn.png");
		post(playerTurn, "playerTurn");
		return;
	}
	// If is the arms turn and he played his move then make it the players turn
	if (playerTurn === false) {
		playerTurn = true;
		$("#turnA").removeClass("disabled");
		turn.setAttribute("src", "/static/img/whiteTurn.png");
		return;
	}
}

async function fetchData() {
	while (true) {
		try {
			let response = await fetch("update");
			let data = await response.json();
			if (JSON.stringify(data) !== "{}") {
				process(data);
			}
		} catch (e) {
			console.log("error", e);
		}
		await sleep(1000);
	}
}

function process(data) {
	// console.log("Name", data.name, typeof data.name);
	// console.log("Data", data.data, typeof data.data);
	if (data.name === "error") {
		if (data.data === 12) {
			openPopupError(data.data);
		} else if (data.data === 55) {
			openPopupError(data.data);
		} else if (data.data === 100) {
			openPopupError(data.data);
		} else if (data.data === 101) {
			openPopupError(data.data);
		} else {
			return;
		}
	} else if (data.name === "situation") {
		if (data.data === 1) {
			stateSleep(data);
		} else if (data.data === 0) {
			stateSleep(data);
		} else if (data.data === -1) {
			stateSleep(data);
		} else {
			return;
		}
	} else if (data.name === "fen") {
		board.position(data.data);
	} else {
		return;
	}
}
