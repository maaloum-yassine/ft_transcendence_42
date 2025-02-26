function run() {
  const apiBaseUrl = `https://${window.location.host}/api/tictactoe-api`;
  const gameBoard = document.getElementById("game-board");
  const statusElement = document.getElementById("status");
  const newGameButton = document.getElementById("new-game");
  const fetchGamesButton = document.getElementById("fetch-games");
  const gameListElement = document.getElementById("game-list");
  const joinGameButton = document.getElementById("join-game");
  const gameIdInput = document.getElementById("game-id-input");
  const getstatsButton = document.getElementById("fetch-stats");

  let currentGameId = null;
  let playerSymbol = null; // Store the player's assigned symbol
  let isMyTurn = false; // Track if it's this player's turn
  let start_game = false;
  let player_o = null;
  let player_x = null;
  let statsChart = null;

  function createCell(index) {
    const cell = document.createElement("div");
    cell.classList.add("cell");
    cell.dataset.index = index;
    cell.addEventListener("click", handleCellClick);
    return cell;
  }

  function isValidBoardState(boardState) {
    if (!boardState) return false;

    if (typeof boardState === "string") {
      return boardState.length === 9 && /^[XO-]{9}$/.test(boardState);
    }
    console.log("anna");
    if (Array.isArray(boardState)) {
      return (
        boardState.length === 9 &&
        boardState.every(
          (cell) => cell === null || cell === "X" || cell === "O"
        )
      );
    }

    return false;
  }

  async function fetchUserStats() {
    const authResponse = await fetch(
      `https://${window.location.host}/api/getId/`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      }
    );

    if (!authResponse.ok) {
      throw new Error(`Auth check failed! Status: ${authResponse.status}`);
    }

    const authData = await authResponse.json();
    const userId = authData.user_id;
    console.log("User ID:", userId);

    try {
      const statsResponse = await fetch(
        `${apiBaseUrl}/user_stats?id_user=${userId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
          },
        }
      );

      const statsData = await statsResponse.json();
      console.log("User stats:", statsData);

      displayStatsChart(statsData);
    } catch (error) {
      console.error("Error fetching user stats:", error);
      gameListElement.innerHTML = `<div>Error fetching stats: ${error.message}</div>`;
    }
  }

  function displayStatsChart(stats) {
    const ctx = document.getElementById("statsChart").getContext("2d");
    
    if (statsChart) {
      statsChart.destroy();
    }
    statsChart = new Chart(ctx, {
      type: "pie",
      data: {
        labels: ["Wins", "Losses", "Draws"],
        datasets: [
          {
            label: "Game Stats",
            data: [stats.wins, stats.losses, stats.draws],
            backgroundColor: [
              "#00FF00", // Bright Neon Green for Wins
              "#FF00FF", // Bright Neon Magenta for Losses
              "#FFFF00", // Bright Neon Yellow for Draws
            ],
            borderColor: [
              "#00FF00", // Neon Green border
              "#FF00FF", // Neon Magenta border
              "#FFFF00", // Neon Yellow border
            ],
            borderWidth: 3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "top",
            labels: {
              font: {
                family: "'VT323', monospace",
                size: 18,
              },
              color: "#ff6b00",
            },
          },
          tooltip: {
            backgroundColor: "#000000",
            titleColor: "#FF00FF",
            bodyColor: "#00FF00",
          },
        },
      },
    });
  }

  function handleCellClick(event) {
    const index = event.target.dataset.index;
    if (
      isMyTurn &&
      event.target.textContent === "" &&
      currentGameId &&
      start_game
    ) {
      makeMove(index);
    }
  }

  function makeMove(index) {
    if (!playerSymbol) {
      statusElement.textContent = "Error: Player symbol not assigned";
      return;
    }

    console.log("send the move");
    const updatedBoard = updateBoard(index);

    const boardString = updatedBoard.join("");
    if (window.socket && window.socket.readyState === WebSocket.OPEN) {
      window.socket.send(
        JSON.stringify({
          type: "make_move",
          position: parseInt(index),
          symbol: playerSymbol,
        })
      );
    }
  }

  function updateBoard(index) {
    const cells = Array.from(gameBoard.children);
    cells[index].textContent = playerSymbol;

    console.log("update the fucking board");
    return cells.map((cell) => cell.textContent || "-");
  }

  function renderBoard(boardState) {
    if (!isValidBoardState(boardState)) {
      console.error("Invalid board state received:", boardState);
      statusElement.textContent = "Error: Invalid board state";
      return;
    }

    gameBoard.innerHTML = "";

    const boardArray =
      typeof boardState === "string"
        ? boardState.split("").map((cell) => (cell === "-" ? null : cell)) // Convert "-" to `null`
        : boardState.map((cell) => (cell === null ? null : cell)); // Ensure `null` stays as `null`

    boardArray.forEach((cell, index) => {
      const cellElement = createCell(index);

      cellElement.textContent = cell === null ? "" : cell;

      if (cell !== null) {
        cellElement.classList.add("disabled");
      }

      gameBoard.appendChild(cellElement);
    });
  }

  async function startNewGame() {
    newGameButton.disabled = true; // Disable the button during the request
    statusElement.textContent = "Checking user authentication...";

    try {
      const authResponse = await fetch(
        `https://${window.location.host}/api/getId/`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include", // Inclure les cookies pour la déconnexion
        }
      );

      if (!authResponse.ok) {
        throw new Error(`Auth check failed! Status: ${authResponse.status}`);
      }

      const authData = await authResponse.json();

      const userId = authData.user_id;
      player_x = userId;
      statusElement.textContent = "Starting new game...";

      const gameResponse = await fetch(`${apiBaseUrl}/games`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_x: userId,
          board_state: "---------",
          current_turn: "X",
        }),
      });

      if (!gameResponse.ok) {
        throw new Error(`Game creation failed! Status: ${gameResponse.status}`);
      }

      const gameData = await gameResponse.json();

      if (!gameData || !gameData.id || !gameData.board_state) {
        throw new Error("Invalid response data from server");
      }

      currentGameId = gameData.id;
      renderBoard(gameData.board_state);

      const gameIdDisplay = document.createElement("div");
      gameIdDisplay.classList.add("game-id-display");
      gameIdDisplay.innerHTML = `Game ID: <strong>${currentGameId}</strong> (Share this ID with the second player)`;
      document.querySelector(".game-container").appendChild(gameIdDisplay);

      connectToWebSocket(currentGameId);
    } catch (error) {
      console.error("Error starting game:", error);
      statusElement.textContent = "Failed to start game. Please try again.";
    } finally {
      newGameButton.disabled = false;
    }
  }

  async function fetchGames() {
    try {
      const authResponse = await fetch(
        `https://${window.location.host}/api/getId/`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );

      if (!authResponse.ok) {
        throw new Error(
          `Authentication failed! Status: ${authResponse.status}`
        );
      }

      const authData = await authResponse.json();
      const userId = authData.user_id;
      const userData = await fetch(
        `https://${window.location.host}/api/getUsername/`,
        {
          method: "GET",
          headers: {
          "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );
      
      if (!userData.ok) {
        throw new Error(
          `Authentication failed! Status: ${userData.status}`
        );
      }
      const Data = await userData.json();
      const username = Data.user;

      const gamesResponse = await fetch(
        `${apiBaseUrl}/stats?id_user=${userId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
          },
        }
      );

      if (!gamesResponse.ok) {
        throw new Error(
          `Failed to fetch games! Status: ${gamesResponse.status}`
        );
      }

      const games = await gamesResponse.json();

      if (!Array.isArray(games)) {
        console.error("Invalid games response:", games);
        throw new Error("Games response is not an array");
      }

      gameListElement.innerHTML = ""; // Clear any previous games
      games.forEach((game) => {
        const gameItem = document.createElement("div");

        const playerX = game.player_x || "Unknown Player X";
        const playerO = game.player_o || "Unknown Player O";
        const winner = game.winner;
        const isDraw = winner === "D";

        let resultMessage = "Still in progress";
        console.log("winner",winner, "plyer o", playerO, "plyer x", playerX, "user id",username);
        if (isDraw) {
          resultMessage = "Draw";
        } else if (winner) {
          if ((winner === "X" && playerX === username) || winner === "O" && playerO === username ) {
            resultMessage = "You won!";
          } else {
            resultMessage = "You lost.";
          }
        } else {
          resultMessage = "Still in progress";
        }

        gameItem.textContent = `${playerX} played as X vs ${playerO} as O - Result: ${resultMessage}`;
        gameListElement.appendChild(gameItem);
      });
    } catch (error) {
      console.error("Error during fetchGames:", error);
      gameListElement.innerHTML = `<div>Error fetching games: ${error.message}</div>`;
    }
  }

  async function joinExistingGame() {
    const roomId = gameIdInput.value.trim(); // Get game ID from input

    if (!roomId) {
      statusElement.textContent = "Please enter a valid game ID";
      return;
    }

    try {
      const authResponse = await fetch(
        `https://${window.location.host}/api/getId/`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );

      if (!authResponse.ok) {
        throw new Error(`Auth check failed! Status: ${authResponse.status}`);
      }

      const authData = await authResponse.json();
      const userId = authData.user_id;
      console.log("hada user_id dial li bgha yjoin ", userId);
      player_o = userId;

      const response = await fetch(`${apiBaseUrl}/games/${roomId}/join`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
        },
        body: JSON.stringify({
          room_id: roomId,
          player_o: userId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.error) {
          statusElement.textContent = data.error;
        } else {
          statusElement.textContent =
            "Failed to join the game. Please try again.";
        }
        return;
      }

      statusElement.textContent = data.message;

      currentGameId = roomId;
      connectToWebSocket(currentGameId);
    } catch (error) {
      console.error("Error joining game:", error);
      statusElement.textContent = "An error occurred. Please try again.";
    }
  }

  async function handleGameEnd(winner) {
    const cells = Array.from(gameBoard.children);

    cells.forEach((cell) => cell.classList.add("disabled")); // Disable all cells

    let gameStatus, winnerSymbol;

    console.log("-****************************",winnerSymbol);
    if (winner == "X" || winner == 'O') {
      statusElement.textContent =
        winner === playerSymbol ? "You win!" : "You lose!";
      winnerSymbol =
        winner === playerSymbol
          ? playerSymbol
          : playerSymbol === "X"
          ? "O"
          : "X";
    } else if (winner == "draw") {
      statusElement.textContent = "It's a draw!";
      winnerSymbol = "D";
    }
 
    isMyTurn = false;

    const updatePayload = {
      id: currentGameId,
      player_x: player_x,
      player_o: player_o,
      board_state: getCurrentBoardState(),
      current_turn: "X",
      winner: winnerSymbol,
    };
    console.log(updatePayload);
    try {
      const response = await fetch(`${apiBaseUrl}/games/${currentGameId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
        },
        credentials: "include",
        body: JSON.stringify(updatePayload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server error response:", errorText);
        throw new Error("Failed to update game state");
      }

      const updatedGame = await response.json();
      console.log("Game state updated:", updatedGame);
    } catch (error) {
      console.error("Error updating game state:", error);
      statusElement.textContent =
        "Error updating game state. Please try again.";
    }
  }

  function getCurrentBoardState() {
    const cells = Array.from(gameBoard.children);
    return cells
      .map((cell) => {
        if (cell.textContent === "X") return "X";
        if (cell.textContent === "O") return "O";
        return "-";
      })
      .join("");
  }

  function getCurrentBoardState() {
    const cells = Array.from(gameBoard.children);
    return cells
      .map((cell) => {
        if (cell.textContent === "X") return "X";
        if (cell.textContent === "O") return "O";
        return "-";
      })
      .join("");
  }

  function connectToWebSocket(roomName) {
    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const socketUrl = `${protocol}${window.location.host}/ws/tictactoe/${roomName}/`;

    if (window.socket) {
      window.socket.close();
    }

    const socket = new WebSocket(socketUrl);

    socket.onmessage = function (event) {
      const message = JSON.parse(event.data);

      console.log("Received WebSocket message:", message);

      switch (message.type) {
        case "player_assigned":
          playerSymbol = message.symbol;
          isMyTurn = message.is_first_player;
          start_game = message.start_game;
          statusElement.textContent = `You are player ${playerSymbol}. ${
            isMyTurn ? "Your turn!" : "Waiting for opponent..."
          }`;
          break;

        case "game_start":
          statusElement.textContent = message.message;
          start_game = message.start_game;
          break;

        case "board_update":
          // console.log("Updating board:", message.board_state);
          renderBoard(message.board_state);
          isMyTurn = message.current_turn === playerSymbol;
          statusElement.textContent = isMyTurn
            ? "Your turn!"
            : "Waiting for other player...";
          break;

        case "game_end":
          console.log("Game ended. Updating board:", message.board_state);
          renderBoard(message.board_state);
          handleGameEnd(message.winner); 
          break;

        case "error":
          console.log("error");
          break;

        default:
          console.warn("Unhandled WebSocket message type:", message.type);
      }
    };

    socket.onopen = function () {
      console.log("Connected to WebSocket");
      statusElement.textContent = "Connected! Waiting for other player...";
    };

    socket.onclose = function (event) {
      console.log("WebSocket connection closed:", event);
      statusElement.textContent = "Connection lost. Please refresh the page.";
    };

    socket.onerror = function (error) {
      console.error("WebSocket error:", error);
      statusElement.textContent = "Connection error. Please try again.";
    };

    window.socket = socket;
  }

  joinGameButton.addEventListener("click", joinExistingGame);
  newGameButton.addEventListener("click", startNewGame);
  fetchGamesButton.addEventListener("click", fetchGames);
  getstatsButton.addEventListener("click", fetchUserStats);
}

export default run;
