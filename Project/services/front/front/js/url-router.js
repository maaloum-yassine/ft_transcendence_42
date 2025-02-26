import fun_sign from "./signin.js";
import fun_signup from "./signup.js";
import fun_verfiy from "./verify.js";
import initResetPassword from "./reset_password.js";
import initTwoFA from "./twoFA.js";
import initProfile from "./profile.js";
import edit from "./edit.js";
import custom from "./custom.js";
import team from "./team.js";
import FriendManager from "./script.js";
import run from "./tictactoe.js";
import logout from "./logout.js";
import initgame_tic from "./hndl_event_home.js";
import ChatManager from "./chat.js";
import { initFriendsModeGame } from "./friends_mode.js";
import { CGR_ } from "./create_friend_game.js";
import { initTournament } from "./tournament.js";
import fetchAndRenderProfile from "./friend_profile.js";
import BlockedUserManager from "./deblock.js";

document.addEventListener("click", (e) => {
  const { target } = e;
  if (!target.matches("a")) {
    return;
  }
  e.preventDefault();
  urlRoute(e);
});

const urlRoutes = {
  "/404": {
    template: "/templates/error/404/404.html",
    title: "404",
    description: "Page not found",
  },
  "/register_invalid": {
    template: "/templates/error/error_signup/error_signup.html",
    title: "Register Invalid",
    description: "Registration failed",
  },
  "/sucess_register": {
    template: "/templates/sucess/signin_sucess.html",
    title: "Success Register",
    description: "Registration successful",
  },
  "/": {
    template: "/templates/signin/signin.html",
    title: "Signin",
    description: "Sign in to your account",
  },
  "/signin": {
    template: "/templates/signin/signin.html",
    title: "Signin",
    description: "Sign in to your account",
  },
  "/signup": {
    template: "/templates/signup/signup.html",
    title: "Signup",
    description: "Create a new account",
  },
  "/profile": {
    template: "/templates/profile/profile.html",
    title: "Profile",
    description: "Your profile",
  },
  "/verify": {
    template: "/templates/verify/verify.html",
    title: "Verify",
    description: "Verify your account",
  },
  "/password_reset": {
    template: "/templates/rest_password/password_reset.html",
    title: "Reset Password",
    description: "Reset your password",
  },
  "/password_reset_confirm": {
    template: "/templates/rest_password/password_reset_confirm.html",
    title: "Confirm Password Reset",
    description: "Confirm your password reset",
  },
  "/twofa": {
    template: "/templates/twoFA/twoFA.html",
    title: "Two Factor Authentication",
    description: "Enable two-factor authentication",
  },
  "/edit": {
    template: "/templates/edit/edit.html",
    title: "Edit Profile",
    description: "Edit your profile",
  },
  "/home": {
    template: "/templates/home/home.html",
    title: "Home",
    description: "Welcome to the homepage",
  },
  "/friend": {
    template: "/templates/friendpage/friend.html",
    title: "Friends",
    description: "Your friends",
  },
  "/tictactoe_game": {
    template: "/templates/tictactoe/tictactoe.html",
    title: "Tic Tac Toe",
    description: "Play Tic Tac Toe",
  },
  "/chat": {
    template: "/templates/chat/chat.html",
    title: "chat",
    description: "chat",
  },

  "/friends_mode": {
    template: "/templates/friends_mode/friends_mode.html",
    title: "Friends Mode Pong",
    description: "Play Pong with Friends",
  },
  "/create_friends_game": {
    template: "/templates/friends_mode/create_friends_game.html",
    title: "Create Friends Mode Pong",
    description: "Create Game to Play Pong with Friends",
  },
  "/tournament": {
    template: "/templates/tournament/tournament.html",
    title: "Create Tournament Pong",
    description: "Create tournament to Play Pong with Friends",
  },
  "/tournament_join": {
    template: "/templates/tournament/tournament_join.html",
    title: "Join Tournament Pong",
    description: "Join tournament to Play Pong with Friends",
  },
  "/friend_profile": {
    template: "/templates/friend_profile/friend_profile.html",
    title: "Friend Profile",
    description: "Friend's Profile",
  },
  "/deblock_page": {
    template: "/templates/deblock_page/deblock_page.html",
    title: "Deblock page",
    description: "Deblock page",
  },
};


const urlRoute = (event) => {
  event = event || window.event;
  event.preventDefault();

  const targetUrl = event.target.href || window.location.href;
  const path = new URL(targetUrl).pathname.toLowerCase();
  const searchParams = new URLSearchParams(new URL(targetUrl).search); // Récupère les paramètres de l'URL
  const id = searchParams.get("id"); // Récupère le paramètre 'id' de l'URL

  console.log("ID Param: ", id); // Vérifie l'ID dans la console

  // Si un paramètre 'id' est présent dans l'URL
  if (id) {
    // Vérifie si l'URL actuelle est différente et inclut l'ID
    if (
      window.location.pathname !== path ||
      window.location.search !== `?id=${id}`
    ) {
      window.history.pushState({}, "", `${path}?id=${id}`); // Met à jour l'URL avec l'ID
      urlLocationHandler(path, id); // Passe l'ID à la fonction de traitement de la route
    }
  } else {
    // Si l'ID n'est pas présent, laisse l'URL sans modification du paramètre 'id'
    if (window.location.pathname !== path || window.location.search !== "") {
      window.history.pushState({}, "", path); // Met à jour l'URL sans 'id'
      urlLocationHandler(path); // Appelle la fonction sans l'ID
    }
  }
};

async function check_authenticate() {
  try {
    const response = await fetch(`https://${window.location.host}/api/check/`, {
      method: "GET",
      credentials: "include",
    });
    if (response.status === 200) return "1";
    if (response.status === 203) return "2";
    if (response.status === 400) return "0";
  } catch (error) {
    console.error("Request failed", error);
    return "0";
  }
}
function isAuthenticatedRoute(location) {
  const list = [
    "/signup",
    "/signin",
    "/verify",
    "/password_reset",
    "/password_reset_confirm",
    "/register_invalid",
    "/sucess_register",
    "/twofa",
    "/",
  ];
  return !list.includes(location);
}

function isAuthenticatedRouteTwFa(location) {
  const list = [
    "/signup",
    "/signin",
    "/password_reset",
    "/",
    "/twofa",
    "/password_reset_confirm",
    "/register_invalid",
    "/sucess_register",
    "/verify",
  ];
  return list.includes(location);
}

function isNotAuthenticatedRoute(location) {
  const list = [
    "/signup",
    "/signin",
    "/password_reset",
    "/",
    "/password_reset_confirm",
    "/register_invalid",
    "/sucess_register",
    "/verify",
  ];
  return list.includes(location);
}

/************************************************** INIT Route************************************************** */
// Fonction pour gérer la route en fonction de l'URL
const urlLocationHandler = async (
  path = window.location.pathname.toLowerCase()
) => {
  let location = path;
  const searchParams = new URLSearchParams(window.location.search);
  const friendProfileId = searchParams.get("id");

  const isAuthenticated = await check_authenticate();

  let route = urlRoutes[location] || urlRoutes["/404"]; // Route par défaut : 404

  if (location !== "/password_reset_confirm") {
    if (route !== urlRoutes["/404"]) {
      if (isAuthenticated === "1") {
        if (!isAuthenticatedRoute(location)) {
          location = "/home";
        }
      } else if (isAuthenticated === "2") {
        if (!isAuthenticatedRouteTwFa(location)) location = "/twofa";
      } else if (isAuthenticated === "0") {
        if (!isNotAuthenticatedRoute(location)) location = "/signin";
      }

      // Update the history state only if the location has changed
      if (window.location.pathname !== location) {
        history.pushState(null, null, location);
      }
    } else {
      location = "/404";
      history.pushState(null, null, location);
    }

    route = urlRoutes[location]; // Get the route
  } else {
    if (isAuthenticated === "1") {
      location = "/profile";
      history.pushState(null, null, "/profile");
    }
  }

  const html = await fetch(route.template).then((response) => response.text());
  document.getElementById("content").innerHTML = html; // Replace content

  handlePageScripts(location, friendProfileId);
};

// Handle the specific scripts for each page
function handlePageScripts(location, friendProfileId = null) {
  const pageSelected = urlRoutes[location].template
    .split("/")
    .pop()
    .toLowerCase();

  if (pageSelected === "signin.html") {
    fun_sign.initSignIn();
  } else if (pageSelected === "signup.html") {
    fun_signup.initSignUp();
  } else if (pageSelected === "verify.html") {
    fun_verfiy.initVerifying();
  } else if (pageSelected === "password_reset.html") {
    initResetPassword();
  } else if (pageSelected === "password_reset_confirm.html") {
    fun_verfiy.initResetPassConfirm();
  } else if (pageSelected === "twofa.html") {
    initTwoFA();
  } else if (pageSelected === "profile.html") {
    custom();
    initProfile();
    logout();
  } else if (pageSelected === "edit.html") {
    edit();
    logout();
  } else if (pageSelected === "home.html") {
    custom();
    team();
    initgame_tic();
    logout();
  } else if (pageSelected === "friend.html") {
    FriendManager.initialize();
    initProfile();
    logout();
  } else if (pageSelected === "tictactoe.html") {
    run();
    logout();
  } else if (pageSelected === "chat.html") {
    ChatManager.initialize();
    logout();
  } else if (pageSelected === "friend_profile.html") {
      custom();
    initProfile();
    if (friendProfileId) {
      fetchAndRenderProfile(friendProfileId);
    }
    logout();
  } else if (pageSelected === "friends_mode.html") {
    const cleanup = initFriendsModeGame();
    window.gameCleanup = cleanup;
  } else if (pageSelected === "create_friends_game.html") {
    CGR_();
  } else if (pageSelected === "tournament.html") {
    initTournament();
  }  else if (pageSelected === "deblock_page.html")
    BlockedUserManager.initialize();
}
// On popstate (back and forward buttons)
window.onpopstate = () => {
  urlLocationHandler(window.location.pathname); // Load the page corresponding to the URL
};

// Initial route handling
urlLocationHandler(window.location.pathname.toLowerCase());

export { urlLocationHandler };
