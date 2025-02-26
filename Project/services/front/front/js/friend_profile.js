import { urlLocationHandler } from "./url-router.js";



const  fetchAndRenderProfile  = (friendId) =>  {


  const url = `https://${window.location.host}/api/user-data/?friend_id=${friendId}`;
   
  fetch(url, {
      method: "GET",
      headers: {
          "Content-Type": "application/json"
      },
      credentials: "include"
  })
  .then((response) => {
      if (!response.ok) {
        history.pushState(null, "", "/404");
      	urlLocationHandler();
      }
      return response.json();
  })  
  .then((data) => {
    console.log(data)
    document.getElementById("profileName").textContent = data.user;
    document.getElementById("timePlayed").textContent = data.total_games;
    document.getElementById("totalWins").textContent = data.wins;
    document.getElementById("totalLosed").textContent = data.losses;
    document.getElementById("theImageAvtar").src = data.avatar;
    fetch(`https://${window.location.host}/api/history/?friend_id=${friendId}`,{method:"GET", credentials:"include"}).then(res=>
    {
      res.json().then(res=>{
        console.log(res)
        if (res.games && res.games.length > 0) {
          res.games.forEach((game)=>{
            const gameItem = document.createElement('div');
            const history = document.getElementById("history")
            gameItem.classList.add('item');
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

        history.appendChild(gameItem);

          })
        }
      })
    })

  })
}

export default fetchAndRenderProfile;