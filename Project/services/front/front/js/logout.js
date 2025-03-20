import { urlLocationHandler } from "./url-router.js";

const logout = () => {
  const logoutLink = document.getElementById("logoutLink");
  logoutLink.addEventListener("click", (event) => {
    event.preventDefault();
    handleLogout();
  });
};

// Fonction pour gérer la déconnexion
const handleLogout = () => {
  const url = `https://${window.location.host}/api/logout/`; // URL de la déconnexion

  fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Erreur lors de la déconnexion");
      }
      return response.json();
    })
    .then((data) => {
      history.pushState(null, "", "/signin");
      urlLocationHandler();
      console.log("Déconnexion réussie:", data);
    })
    .catch((error) => {
      console.error("Erreur lors de la déconnexion:", error);
    });
};

export default logout;
