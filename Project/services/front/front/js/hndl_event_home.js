import { urlLocationHandler } from "./url-router.js";

const initgame_tic = () => {
  const addNavigationListener = (selector, path) => {
    const element = document.getElementById(selector);
    if (element) {
      element.addEventListener("click", (e) => {
        e.preventDefault();
        history.pushState(null, "", path);
        urlLocationHandler();
      });
    }
  };

  const navigationLinks = [
    { id: "startButton", path: "/tictactoe_game" },
    { id: "friendsModeButton", path: "/create_friends_game" },
    { id: "hometotournamentButton", path: "/tournament" },
    { id: "startButton_Profile", path: "/profile" },
    { id: "edit", path: "/edit" },
    { id: "chat", path: "/chat" }
  ];

  navigationLinks.forEach(({ id, path }) => addNavigationListener(id, path));

  const logoLink = document.querySelector(".logo");
  if (logoLink) {
    logoLink.addEventListener("click", (e) => {
      e.preventDefault();
      history.pushState(null, "", "/home");
      urlLocationHandler();
    });
  }
};

export default initgame_tic;
