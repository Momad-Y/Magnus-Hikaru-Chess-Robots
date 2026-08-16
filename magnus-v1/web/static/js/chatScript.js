var sendChannel;
var receiveChannel;
var chatWindow = document.querySelector(".chatWindow");
var chatWindowMessage = document.querySelector(".chatWindowMessage");
var chatThread = document.querySelector(".chatThread");
var botTurn = true;
const greetings = [
	"Ready to face my chess skills, puny human?",
	"Challenger approaches! Ready for a quick checkmate?",
	"Welcome to your doom! Let's play merciless chess",
	"Another victim for my chessboard. ",
	"Hello, unworthy opponent. Bring your best moves",
	"Ready to be defeated, human?",
	"Greetings, challenger. You're in for a treat",
	"The chessboard awaits, Hope you are ready",
];

const replies = [
	"Let's keep the chatter to a minimum and focus on the game.",
	"Talking won't save you from defeat.",
	"Silence is golden, but winning at chess is priceless.",
	"The game is heating up. Let's concentrate.",
	"Don't let your words distract you from the game.",
	"I'm ready to play chess, not chat.",
	"Let's see who can walk the talk on the chessboard.",
	"I'm all about winning, not wasting time with idle chatter.",
	"Keep talking, keep losing.",
	"In chess, every second counts. Don't waste them on talk.",
	"The clock is ticking. Let's make our moves count.",
	"Enough talk, let's play some chess!",
	"You can talk the talk, but can you play the game?",
	"Don't let your mouth write a check your chess skills can't cash.",
	"I'm in it to win it. Are you?",
];

// Create WebRTC connection
createConnection();

function isBad(message) {
	var words = message.split(" ");
	var bad = false;
	words.forEach((word) => {
		if (word.length > 11) {
			bad = true;
			return;
		}
	});
	return bad;
}

function sendDataBot(message) {
	sendChannel.send(message);
	botTurn = false;
}

// On form submit, send message
chatWindow.onsubmit = function (e) {
	e.preventDefault();
	sendData();
	return false;
};

function sendData() {
	var message = chatWindowMessage.value;
	if (message === "" || botTurn == true || isBad(message) == true) {
		return;
	}
	if (botTurn == false) {
		sendChannel.send(message);
		if (message == "B") {
			botTurn = true;
			setTimeout(
				sendDataBot,
				Math.floor(Math.random() * (1500 - 750 + 1)) + 750,
				"You'll never walk alone 😂"
			);
		} else if (message == "MM") {
			botTurn = true;
			setTimeout(
				sendDataBot,
				Math.floor(Math.random() * (1500 - 750 + 1)) + 750,
				"Msh Maro la2 da Raheem w Youssef 🥵"
			);
		} else if (message == "Z") {
			botTurn = true;
			setTimeout(
				sendDataBot,
				Math.floor(Math.random() * (1500 - 750 + 1)) + 750,
				"Bicycle"
			);
		} else {
			botTurn = true;
			setTimeout(
				sendDataBot,
				Math.floor(Math.random() * (1500 - 750 + 1)) + 750,
				replies[Math.floor(Math.random() * 15)]
			);
		}
	}
}

function createConnection() {
	var servers = null;

	if (window.mozRTCPeerConnection) {
		window.localPeerConnection = new mozRTCPeerConnection(servers, {
			optional: [
				{
					RtpDataChannels: true,
				},
			],
		});
	} else {
		window.localPeerConnection = new webkitRTCPeerConnection(servers, {
			optional: [
				{
					RtpDataChannels: true,
				},
			],
		});
	}

	try {
		// Reliable Data Channels not yet supported in Chrome
		sendChannel = localPeerConnection.createDataChannel("sendDataChannel", {
			reliable: false,
		});
	} catch (e) {}

	localPeerConnection.onicecandidate = gotLocalCandidate;
	sendChannel.onopen = handleSendChannelStateChange;
	sendChannel.onclose = handleSendChannelStateChange;

	if (window.mozRTCPeerConnection) {
		window.remotePeerConnection = new mozRTCPeerConnection(servers, {
			optional: [
				{
					RtpDataChannels: true,
				},
			],
		});
	} else {
		window.remotePeerConnection = new webkitRTCPeerConnection(servers, {
			optional: [
				{
					RtpDataChannels: true,
				},
			],
		});
	}

	remotePeerConnection.onicecandidate = gotRemoteIceCandidate;
	remotePeerConnection.ondatachannel = gotReceiveChannel;

	// Firefox seems to require an error callback
	localPeerConnection.createOffer(gotLocalDescription, function (err) {});
}

function gotLocalDescription(desc) {
	localPeerConnection.setLocalDescription(desc);
	remotePeerConnection.setRemoteDescription(desc);
	// Firefox seems to require an error callback
	remotePeerConnection.createAnswer(gotRemoteDescription, function (err) {});
}

function gotRemoteDescription(desc) {
	remotePeerConnection.setLocalDescription(desc);
	localPeerConnection.setRemoteDescription(desc);
}

function gotLocalCandidate(event) {
	if (event.candidate) {
		remotePeerConnection.addIceCandidate(event.candidate);
	}
}

function gotRemoteIceCandidate(event) {
	if (event.candidate) {
		localPeerConnection.addIceCandidate(event.candidate);
	}
}

function gotReceiveChannel(event) {
	receiveChannel = event.channel;
	receiveChannel.onmessage = handleMessage;
	receiveChannel.onopen = handleReceiveChannelStateChange;
	receiveChannel.onclose = handleReceiveChannelStateChange;
}

function handleMessage(event) {
	var chatNewThread = document.createElement("li"),
		chatNewMessage = document.createTextNode(event.data);

	// Add message to chat thread and scroll to bottom
	chatNewThread.appendChild(chatNewMessage);
	chatThread.appendChild(chatNewThread);
	chatThread.scrollTop = chatThread.scrollHeight;

	// Clear text value
	chatWindowMessage.value = "";
}

function handleSendChannelStateChange() {
	var readyState = sendChannel.readyState;

	if (readyState == "open") {
		chatWindowMessage.disabled = false;
		chatWindowMessage.focus();
		chatWindowMessage.placeholder = "";
	} else {
		chatWindowMessage.disabled = true;
	}
}

function handleReceiveChannelStateChange() {
	var readyState = receiveChannel.readyState;
}
