<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tournament Waiting Room</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            background-color: #1a1a1a;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .container {
            width: 80%;
            max-width: 800px;
            background-color: #2c2c2c;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
        }

        h1 {
            font-size: 2em;
            margin-bottom: 20px;
        }

        p {
            font-size: 1.2em;
            margin-bottom: 40px;
            color: #aaa;
        }

        .players-list {
            background-color: #3c3c3c;
            padding: 20px;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 30px;
        }

        .players-list h2 {
            font-size: 1.5em;
            margin-bottom: 15px;
        }

        .player {
            background-color: #444;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .start-btn {
            background-color: #d23600;
            color: #fff;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
            transition: background-color 0.3s;
        }

        .start-btn:disabled {
            background-color: #666;
            cursor: not-allowed;
        }

        .start-btn:hover:not(:disabled) {
            background-color: #e8491e;
        }

        .close-btn {
            background-color: transparent;
            color: #999;
            border: none;
            cursor: pointer;
            margin-top: 20px;
        }

        .close-btn:hover {
            color: #fff;
        }

        .username-badge {
            padding: 8px 16px;
            background-color: #e8491e;
            color: rgb(228, 225, 225);
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 300;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            display: inline-block;
        }

        .player.ready .username-badge {
            background-color: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tournament Waiting Room</h1>
        <p id="tournament-status">Waiting for players to join...</p>

        <div class="players-list">
            <h2>Players Joined:</h2>
            <ul id="player-list">
            </ul>
        </div>

        <button id="start-btn" class="start-btn" disabled>Start Match</button>
        
        <br>
        <button class="close-btn">Close</button>
    </div>

    <script>
        
        const tournamentName = 'Ps5zdZxLoGziiCcwmjwxsX';
        let ws = null;
        let isPlayerReady = false;
        let tournamentData = null;

        
        async function fetchTournamentData() {
            try {
                const response = await fetch(`game/tournament/Ps5zdZxLoGziiCcwmjwxsX/`);
                tournamentData = await response.json();
                
                updatePlayerList(tournamentData.tournament_members);
                
                updateTournamentStatus(tournamentData);
            } catch (error) {
                console.error('Error fetching tournament data:', error);
                document.getElementById('tournament-status').textContent = 'Error loading tournament data';
            }
        }

        
        function updatePlayerList(players) {
            const playerList = document.getElementById('player-list');
            playerList.innerHTML = ''; 
            
            if (players.length === 0) {
                const li = document.createElement('li');
                li.classList.add('player');
                li.textContent = 'Waiting for players to join...';
                playerList.appendChild(li);
            } else {
                players.forEach(player => {
                    const li = document.createElement('li');
                    li.classList.add('player');
                    const badge = document.createElement('div');
                    badge.classList.add('username-badge');
                    badge.textContent = player.username;
                    li.appendChild(badge);
                    playerList.appendChild(li);
                });
            }
        }

        
        function updateTournamentStatus(tournamentData) {
            const statusElement = document.getElementById('tournament-status');
            const startBtn = document.getElementById('start-btn');

            if (tournamentData.is_tournament_full) {
                statusElement.textContent = 'Tournament is full. Ready to start!';
                startBtn.disabled = false;
            } else {
                const remainingSpots = 4 - tournamentData.tournament_members.length;
                statusElement.textContent = `Waiting for ${remainingSpots} more player${remainingSpots !== 1 ? 's' : ''} to join`;
                startBtn.disabled = true;
            }
        }

        
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws/game/tournament/${tournamentName}/`);

            ws.onopen = function(event) {
                console.log('Connected to WebSocket');
                ws.send(JSON.stringify({ action: 'join' }));
                
                
                fetchTournamentData();
            };

            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                
                if (message.type === 'tournament_members_handler') {
                    fetchTournamentData(); 
                }
                
                if (message.type === 'player_ready_update') {
                    updateReadyStatus(message.ready_players);
                }
                
                if (message.type === 'redirect_to_game') {   
                    window.location.href = `/game/${message.game_room}/`;
                }
            };

            ws.onerror = function(error) {
                console.error('WebSocket Error:', error);
                document.getElementById('tournament-status').textContent = 'Connection error. Please refresh.';
            };

            ws.onclose = function() {
                console.log('WebSocket connection closed');
                setTimeout(connectWebSocket, 3000); 
            }
        }

        
        function updateReadyStatus(readyPlayers) {
            const playerItems = document.querySelectorAll('.player');
            playerItems.forEach(playerItem => {
                const playerName = playerItem.querySelector('.username-badge').textContent;
                if (readyPlayers.includes(playerName)) {
                    playerItem.classList.add('ready');
                }
            });
        }

        
        document.getElementById('start-btn').addEventListener('click', function() {
            if (!isPlayerReady && !this.disabled) {
                isPlayerReady = true;
                this.disabled = true;
                this.textContent = 'Waiting for others...';
                
                if (ws) {
                    ws.send(JSON.stringify({ action: 'player_ready' }));
                }
            }
        });

        
        document.querySelector('.close-btn').addEventListener('click', () => {
            window.close(); 
        });

        
        connectWebSocket();
    </script>
</body>
</html>


i want you to split this code to css and html and js file for my spa website the html will be only dive and i want you to change the design i want the design to be more fancy and more modern and for the classes name and ids name make them unique make them all have something unique so no problem happend in the css 