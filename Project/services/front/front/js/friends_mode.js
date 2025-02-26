// friends_mode.js
export function initFriendsModeGame() {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');

  // Further reduce canvas size
  canvas.width = window.innerWidth * 0.7;
  canvas.height = window.innerHeight * 0.6;

  const netWidth = 2;
  const paddleWidth = 6;
  const paddleHeight = 60;
  const ballSize = 6;

  let ballX = canvas.width / 2 - ballSize / 2;
  let ballY = canvas.height / 2 - ballSize / 2;
  let player1Y = canvas.height / 2 - paddleHeight / 2;
  let player2Y = canvas.height / 2 - paddleHeight / 2;
  let player1Score = 0;
  let player2Score = 0;
  let myPaddle = null;
  let gameStarted = false;
  let paddleVelocity = 0;
  let winner = null;

  const keydownHandler = (e) => {
    if (myPaddle === 'paddle1') {
      if (e.key === 'w') paddleVelocity = -300;
      if (e.key === 's') paddleVelocity = 300;
    } else if (myPaddle === 'paddle2') {
      if (e.key === 'ArrowUp') paddleVelocity = -300;
      if (e.key === 'ArrowDown') paddleVelocity = 300;
    }
    ws.send(JSON.stringify({ velocity: paddleVelocity }));
  };

  const keyupHandler = (e) => {
    if (myPaddle === 'paddle1' && (e.key === 'w' || e.key === 's')) {
      paddleVelocity = 0;
    } else if (myPaddle === 'paddle2' && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      paddleVelocity = 0;
    }
    ws.send(JSON.stringify({ velocity: paddleVelocity }));
  };

  document.addEventListener('keydown', keydownHandler);
  document.addEventListener('keyup', keyupHandler);

  function drawRect(x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
  }

  function drawCircle(x, y, size, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2, false);
    ctx.closePath();
    ctx.fill();
  }

  function drawNet() {
    ctx.beginPath();
    ctx.setLineDash([10, 8]); 
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = netWidth;
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.stroke();
    ctx.setLineDash([]); 
  }

  function drawScore() {
    ctx.font = '20px "Courier New", monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.textAlign = 'center';
    ctx.fillText(player1Score, canvas.width / 2 - 70, 30);
    ctx.fillText(player2Score, canvas.width / 2 + 70, 30);
  }

  function drawGame() {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(1, '#16213e');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawNet();
    drawScore();
    
    ctx.shadowBlur = 8;
    ctx.shadowColor = '#00ffff';
    drawRect(canvas.width / 10 + 3, player1Y, paddleWidth, paddleHeight, '#00ffff');
    drawRect(canvas.width - canvas.width / 10 - paddleWidth - 3, player2Y, paddleWidth, paddleHeight, '#ff00ff');
    ctx.shadowBlur = 0;

    ctx.shadowBlur = 10;
    ctx.shadowColor = '#00ff80';
    drawCircle(ballX, ballY, ballSize, '#00ff80');
    ctx.shadowBlur = 0;
  }

  function check_winner() {
    if (winner) {
      ctx.font = '30px "Courier New", monospace';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.textAlign = 'center';
      ctx.fillText(`${winner} wins!`, canvas.width / 2, canvas.height - 50);
      return;
    }
  }

  function gameLoop(timestamp) {
    drawGame();
    check_winner();
    requestAnimationFrame(gameLoop);
  }

  const state = history.state;
  const roomName = state ? state.roomName : null;

  if (!roomName) {
    alert('Room not found');
    return;
  }
  const ws = new WebSocket(`wss://${window.location.host}/ws/game/${roomName}/`);

  ws.onopen = () => {
    console.log('Connected to the server');
    try {
      ws.send(JSON.stringify({
        type: 'screen_dimensions',
        width: canvas.width,
        height: canvas.height,
      }));
    } catch (error) {
      console.error('Failed to send data:', error);
    }
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.paddle) {
      myPaddle = data.paddle;
      console.log("Assigned to:", myPaddle);
    }

    if (data.start_game !== undefined) {
      gameStarted = data.start_game;
      ballX = data.ballX;
      ballY = data.ballY;
      player1Y = data.player1Y;
      player2Y = data.player2Y;
    }

    if (data.player1Y !== undefined && data.player2Y !== undefined) {
      player1Y = data.player1Y;
      player2Y = data.player2Y;
      ballX = data.ballX;
      ballY = data.ballY;
      player1Score = data.player1Score;
      player2Score = data.player2Score;
      winner = data.winner;
    }
  };

  ws.onclose = () => console.log('Disconnected from the server');
  ws.onerror = (error) => console.error(error);

  const velocityInterval = setInterval(() => {
    if (myPaddle && gameStarted) {
      ws.send(JSON.stringify({ velocity: paddleVelocity }));
    }
  }, 30);

  requestAnimationFrame(gameLoop);

  return () => {
    document.removeEventListener('keydown', keydownHandler);
    document.removeEventListener('keyup', keyupHandler);
    
    clearInterval(velocityInterval);
    
    ws.close();
  };
}