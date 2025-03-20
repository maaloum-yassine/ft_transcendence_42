import { urlLocationHandler } from "./url-router.js";

const initProfile = () => {

    const gamesPlayed = document.getElementById("Games_Played");
    const winned = document.getElementById("Winned");
    const losed = document.getElementById("Losed");
    const username_pp = document.getElementById("username_pp"); // Added for username display
    const avatar_user = document.getElementById("avatar_user"); // Added for username display
    const url = `https://${window.location.host}/api/badr_game_stats/`;

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include"
    })
    .then((response) => {
        if (!response.ok) {
            return response.json().then((errorData) => {
                throw new Error(
                    errorData.message || `HTTP Error: ${response.status}`
                );
            });
        }
        return response.json();
    })
    .then((data) => {
        if (gamesPlayed) gamesPlayed.textContent = data.total_games;
        if (winned) winned.textContent = data.wins;
        if (losed) losed.textContent = data.losses;
        if (username_pp) username_pp.textContent = data.user;
        if (avatar_user)
        {
          avatar_user.style.display = "block";
          avatar_user.src = data.avatar;
        }
    })
    .catch((error) => {
        console.error("Error fetching game stats:", error);
    });



    const gamingLibraryContainer = document.querySelector('.gaming-library');

    // Ensure the container exists
    if (!gamingLibraryContainer) {
        console.error('Gaming library container not found');
        return;
    }

  const url2 = `https://${window.location.host}/api/badr_list_games/`;
  fetch(url2, {
      method: "GET",
      headers: {
          "Content-Type": "application/json"
      },
      credentials: "include"
  })
  .then((response) => {
      if (!response.ok) {
          return response.json().then((errorData) => {
              throw new Error(
                  errorData.message || `HTTP Error: ${response.status}`
              );
          });
      }
      return response.json();
  })
  .then((data) => {
      const games = data.games;
      if (games && games.length > 0) {
          games.forEach((game) => {
              const gameItem = document.createElement('div');
              gameItem.classList.add('item');

              // Add the content for each match
              gameItem.innerHTML = `
                  <ul>
                      <li><img src="images/game-01.jpg" alt="" class="templatemo-item"></li>
                      <li>
                          <h4>Players</h4>
                          <span>${game.players.join(', ')}</span>
                      </li>
                      <li>
                          <h4>Date</h4>
                          <span>${new Date(game.created_at).toLocaleDateString()}</span>
                      </li>
                      <li>
                          <h4>Your Score</h4>
                          <span>${game.player1Score} | ${game.player2Score}</span>
                      </li>
                      <li>
                          <h4>State</h4>
                          <span>${game.winner === data.user ? 'Won' : 'Lost'}</span>
                      </li>
                  </ul>
              `;

              gamingLibraryContainer.appendChild(gameItem);
          });
      } else {
          gamingLibraryContainer.innerHTML = '<p>No match history available.</p>';
      }
  })
  .catch((error) => {
      console.error("Error fetching game stats:", error);
  });
    // Detailed logging function

};

export default initProfile;
