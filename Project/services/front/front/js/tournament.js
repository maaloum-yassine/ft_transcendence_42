var isRunning = false;

class PingPongGame {
	constructor() {
		this.canvas = document.getElementById("gameCanvas");
		this.ctx = this.canvas.getContext("2d");
		this.player1Score = document.getElementById("player1Score");
		this.player2Score = document.getElementById("player2Score");

		// Game objects
		this.player1 = {
			x: 20,
			y: this.canvas.height / 2 - 50,
			width: 10,
			height: 100,
			score: 0,
			speed: 5,
		};

		this.player2 = {
			x: this.canvas.width - 30,
			y: this.canvas.height / 2 - 50,
			width: 10,
			height: 100,
			score: 0,
			speed: 5,
		};

		this.ball = {
			x: this.canvas.width / 2,
			y: this.canvas.height / 2,
			radius: 10,
			speedX: 4,
			speedY: 4,
		};

		// Keyboard state
		this.keys = {
			w: false,
			s: false,
			ArrowUp: false,
			ArrowDown: false,
		};

		this.setupEventListeners();
	}

	setupEventListeners() {
		document.addEventListener("keydown", (e) => {
			if (e.key === "w") this.keys.w = true;
			if (e.key === "s") this.keys.s = true;
			if (e.key === "ArrowUp") this.keys.ArrowUp = true;
			if (e.key === "ArrowDown") this.keys.ArrowDown = true;
		});

		document.addEventListener("keyup", (e) => {
			if (e.key === "w") this.keys.w = false;
			if (e.key === "s") this.keys.s = false;
			if (e.key === "ArrowUp") this.keys.ArrowUp = false;
			if (e.key === "ArrowDown") this.keys.ArrowDown = false;
		});
	}

	movePlayers() {
		// Player 1 movement (WASD)
		if (this.keys.w && this.player1.y > 0) this.player1.y -= this.player1.speed;
		if (
			this.keys.s &&
			this.player1.y < this.canvas.height - this.player1.height
		)
			this.player1.y += this.player1.speed;

		// Player 2 movement (Arrow keys)
		if (this.keys.ArrowUp && this.player2.y > 0)
			this.player2.y -= this.player2.speed;
		if (
			this.keys.ArrowDown &&
			this.player2.y < this.canvas.height - this.player2.height
		)
			this.player2.y += this.player2.speed;
	}

	async updateBall() {
		// Move ball
		this.ball.x += this.ball.speedX;
		this.ball.y += this.ball.speedY;

		// Wall collision (top and bottom)
		if (
			this.ball.y - this.ball.radius <= 0 ||
			this.ball.y + this.ball.radius >= this.canvas.height
		) {
			this.ball.speedY = -this.ball.speedY;
		}

		// Paddle collision
		const checkPaddleCollision = (player) => {
			if (
				this.ball.x - this.ball.radius <= player.x + player.width &&
				this.ball.x + this.ball.radius >= player.x &&
				this.ball.y >= player.y &&
				this.ball.y <= player.y + player.height
			) {
				// console.log(this.ball.x - this.ball.radius, this.ball.y);

				// console.log(player.x + player.width);
				this.ball.speedX = -this.ball.speedX;
				// Optional: Add slight angle change
				this.ball.speedY += Math.random() - 0.5;
			} else {
				// console.log("Not in range")
			}
		};

		checkPaddleCollision(this.player1);
		checkPaddleCollision(this.player2);

		// Scoring
		if (this.ball.x <= 0) {
			this.player2.score++;
			// console.log("Player 1 scored");
			playerScoredT(2);
			if (this.player2.score == 5) {
				this.player1.score = 0;
				this.player2.score = 0;
			}
			this.resetBall();
		}
		if (this.ball.x >= this.canvas.width) {
			this.player1.score++;
			// console.log("Player 2 scored");
			playerScoredT(1);
			if (this.player1.score == 5) {
				this.player1.score = 0;
				this.player2.score = 0;
			}
			this.resetBall();
		}

		// Update score display
		this.player1Score.textContent = this.player1.score;
		this.player2Score.textContent = this.player2.score;
	}

	resetBall() {
		this.ball.x = this.canvas.width / 2;
		this.ball.y = this.canvas.height / 2;
		this.ball.speedX = -this.ball.speedX;
		this.ball.speedY = 4 * (Math.random() > 0.5 ? 1 : -1);
	}

	draw() {
		// Clear canvas
		this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

		// Draw center line
		this.ctx.beginPath();
		this.ctx.setLineDash([5, 5]);
		this.ctx.moveTo(this.canvas.width / 2, 0);
		this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
		this.ctx.strokeStyle = "#ccc";
		this.ctx.stroke();
		this.ctx.setLineDash([]);

		// Draw paddles
		this.ctx.fillStyle = "blue";
		this.ctx.fillRect(
			this.player1.x,
			this.player1.y,
			this.player1.width,
			this.player1.height
		);
		this.ctx.fillRect(
			this.player2.x,
			this.player2.y,
			this.player2.width,
			this.player2.height
		);

		// Draw ball
		this.ctx.beginPath();
		this.ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
		this.ctx.fillStyle = "white";
		this.ctx.fill();
	}

	gameLoop() {
		if (isRunning) {
			this.movePlayers();
			this.updateBall();
			this.draw();
		}
		requestAnimationFrame(() => this.gameLoop());
	}

	start() {
		console.log("Testing");
		this.gameLoop();
	}
}

// Initialize and start the game

const toogleGameState = (state) => {
	isRunning = state;
};

const initPong = () => {
	const game = new PingPongGame();
	game.start();
};

var currentView = 0;
var step = 1;

var tournamentProccess = 0;

const players = {
	playerOne: "",
	playerTwo: "",
	playerThree: "",
	playerFour: "",
};

const matchOne = {
	playerOne: "",
	playerTwo: "",
	playerOneScore: 0,
	playerTwoScore: 0,
	winner: "",
};

const matchTwo = {
	playerOne: "",
	playerTwo: "",
	playerOneScore: 0,
	playerTwoScore: 0,
	winner: "",
};

const matchFinal = {
	playerOne: "",
	playerTwo: "",
	playerOneScore: 0,
	playerTwoScore: 0,
	winner: "",
};

const playerScoredT = (players) => {
	const player1NickName = document.getElementById("player1NickName");
	const player2NickName = document.getElementById("Player2NickName");
	const player1Score = document.getElementById("player1Score");
	const player2Score = document.getElementById("player2Score");
	const tournamentStepsContainer = document.getElementById(
		"tournamentStepsContainer"
	);
	const winnerNickName = document.getElementById("winnerNickName");

	// console.log(player1Score);
	// console.log(player2Score);

	if (tournamentProccess == 0) {
		// console.log(matchOne);
		if (players == 1) {
			matchOne.playerOneScore++;
			// matchOne.playerOneScore++;
		} else if (players == 2) {
			matchOne.playerTwoScore++;
		}

		if (matchOne.playerOneScore == 5) {
			matchOne.winner = matchOne.playerOne;
			toogleGameState(false);
			tournamentProccess++;
			//
			player1NickName.textContent = matchTwo.playerOne;
			player2NickName.textContent = matchTwo.playerTwo;
			player1Score.textContent = "0";
			player2Score.textContent = "0";
			matchFinal.playerOne = matchOne.winner;
			setTimeout(() => {
				toogleGameState(true);
			}, 1000);
		} else if (matchOne.playerTwoScore == 5) {
			matchOne.winner = matchOne.playerTwo;
			toogleGameState(false);
			tournamentProccess++;
			//
			player1NickName.textContent = matchTwo.playerOne;
			player2NickName.textContent = matchTwo.playerTwo;
			player1Score.textContent = "0";
			player2Score.textContent = "0";
			matchFinal.playerOne = matchOne.winner;
			setTimeout(() => {
				toogleGameState(true);
			}, 1000);
		}
		// console.log(matchOne);
	} else if (tournamentProccess == 1) {
		// console.log(matchTwo);
		if (players == 1) {
			matchTwo.playerOneScore++;
			// matchTwo.playerOneScore++;
		} else if (players == 2) {
			matchTwo.playerTwoScore++;
		}
		if (matchTwo.playerOneScore == 5) {
			matchTwo.winner = matchTwo.playerOne;
			matchFinal.playerTwo = matchTwo.winner;
			player1NickName.textContent = matchOne.winner;
			player2NickName.textContent = matchTwo.winner;
			toogleGameState(false);
			tournamentProccess++;
			setTimeout(() => {
				toogleGameState(true);
			}, 1000);
		} else if (matchTwo.playerTwoScore == 5) {
			matchTwo.winner = matchTwo.playerTwo;
			matchFinal.playerTwo = matchTwo.winner;
			player1NickName.textContent = matchOne.winner;
			player2NickName.textContent = matchTwo.winner;
			toogleGameState(false);
			tournamentProccess++;
			setTimeout(() => {
				toogleGameState(true);
			}, 1000);
		}
		// console.log(matchTwo);
	} else if (tournamentProccess == 2) {
		// console.log(matchFinal);
		if (players == 1) {
			matchFinal.playerOneScore++;
		} else if (players == 2) {
			matchFinal.playerTwoScore++;
		}
		if (matchFinal.playerOneScore == 5) {
			toogleGameState(false);
			matchFinal.winner = matchFinal.playerOne;
			winnerNickName.textContent = matchFinal.winner;
			tournamentProccess++;
			tournamentStepsContainer.style.transform = `translateY(-300svh)`;
		} else if (matchFinal.playerTwoScore == 5) {
			toogleGameState(false);
			matchFinal.winner = matchFinal.playerTwo;
			winnerNickName.textContent = matchFinal.winner;
			tournamentProccess++;
			tournamentStepsContainer.style.transform = `translateY(-300svh)`;
		}
	}
};

const handleAddForm = () => {
	const addPlayerForm = document.getElementById("addPlayerForm");
	const tournamentEmailInput = document.querySelectorAll(
		".tournamentEmailInput"
	);
	const player1NickName = document.getElementById("player1NickName");
	const player2NickName = document.getElementById("Player2NickName");
	// 	const otpInput = document.querySelectorAll(".otpInput");
	// 	const formData = new FormData();
	// 	tournamentEmailInput.forEach((ele, idx) => {
	// 		formData.append(`email${idx + 1}`, ele.value);
	// 	});
	const tournamentStepsContainer = document.getElementById(
		"tournamentStepsContainer"
	);
	addPlayerForm.addEventListener("submit", (e) => {
		e.preventDefault();
		var check = true;
		tournamentEmailInput.forEach((ele) => {
			if (!check) return;
			if (ele.value.length == 0) check = false;
		});
		if (!check) {
			alert("All inputs are required");
			return;
		}
		players.playerOne = tournamentEmailInput[0].value;
		players.playerTwo = tournamentEmailInput[1].value;
		players.playerThree = tournamentEmailInput[2].value;
		players.playerFour = tournamentEmailInput[3].value;

		matchOne.playerOne = players.playerOne;
		matchOne.playerTwo = players.playerThree;

		matchTwo.playerOne = players.playerTwo;
		matchTwo.playerTwo = players.playerFour;
		currentView--;
		tournamentStepsContainer.style.transform = `translateY(${
			currentView * 100
		}svh)`;
		console.log(players);
		player1NickName.textContent = matchOne.playerOne;
		player2NickName.textContent = matchOne.playerTwo;
		setTimeout(() => {
			initPong();
			toogleGameState(true);
		}, 700);
	});
};

const requestCreatingTournament = () => {

	currentView--;
	tournamentStepsContainer.style.transform = `translateY(${
		currentView * 100
	}svh)`;

};

const initTournament = () => {
	const createTournament = document.getElementById("createTournament");
	const tournamentStepsContainer = document.getElementById(
		"tournamentStepsContainer"
	);

	createTournament.addEventListener("click", requestCreatingTournament);
	handleAddForm();
	window.addEventListener("keydown", (e) => {
		if (e.key == "f") {
			console.log("======================");
			console.log(matchOne);
			console.log(matchTwo);
			console.log(matchFinal);
		}
	});
};

export { initTournament, playerScoredT };