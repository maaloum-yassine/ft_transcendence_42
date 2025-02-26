import { urlLocationHandler } from "./url-router.js";

const logout = () => {
  // Sélectionner le lien de déconnexion
  const logoutLink = document.getElementById("logoutLink");

  // Ajouter l'événement 'click' pour déclencher la fonction de déconnexion
  logoutLink.addEventListener("click", (event) => {
    // Empêcher le comportement par défaut du lien (navigation)
    event.preventDefault();

    // Appeler la fonction de déconnexion
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
    credentials: "include", // Inclure les cookies pour la déconnexion
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
      // window.location.href = "/"; // Redirection vers la page d'accueil après la déconnexion
    })
    .catch((error) => {
      console.error("Erreur lors de la déconnexion:", error);
    });
};

export default logout;
