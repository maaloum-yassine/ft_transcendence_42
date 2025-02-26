import { urlLocationHandler } from "./url-router.js";

const initFeedBack = () => {
  const signInFeedbackContainer = document.getElementById(
    "signInFeedbackContainer"
  );
  const hideSignInFeedBack = document.getElementById("hideSignInFeedBack");

  if (signInFeedbackContainer)
    signInFeedbackContainer.addEventListener("click", (e) => {
      if (e.target.id === "signInFeedbackContainer")
        signInFeedbackContainer.style.display = "none";
    });
  if (hideSignInFeedBack)
    hideSignInFeedBack.addEventListener("click", () => {
      signInFeedbackContainer.style.display = "none";
    });
};

function alert_message(title, content) {
  signInFeedBackTitle.textContent = title;
  signInFeedBackDesc.textContent = content;
  signInFeedbackContainer.style.display = "flex";
}

function fetch_end_point(login_user, login_password) {
  const url = `https://${window.location.host}/api/login/`;
  const data = {
    username: login_user,
    password: login_password,
  };

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
    credentials: "include",
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errorData) => {
          throw new Error(
            errorData.message || `Erreur HTTP : ${response.status}`
          );
        });
      }
      return response.json();
    })
    .then((responseData) => {
      if (responseData.message === "Login successful, 2FA required") {
        history.pushState(null, "", "/twofa");
      } else {
        history.pushState(null, "", "/home");
      }
      urlLocationHandler();
    })
    .catch((error) => {
      alert_message("ERROR", error.message);
    });
}

const handleSignIn = (e) => {
  e.preventDefault();
  const login_user = document.getElementById("login_user");
  const login_password = document.getElementById("login_password");
  const signInFeedbackContainer = document.getElementById(
    "signInFeedbackContainer"
  );
  const signInFeedBackTitle = document.getElementById("signInFeedBackTitle");
  const signInFeedBackDesc = document.getElementById("signInFeedBackDesc");
  if (!login_user.value || !login_password.value)
    alert_message("Missing values", "All inputs are required");
  else fetch_end_point(login_user.value, login_password.value);
};

const handleSignIn_remote = (platform) => {
  if (platform === "google") {
    window.location.href = `https://${window.location.host}/api/oauth/login/`;
  } else if (platform === "42Intra") {
    window.location.href = `https://${window.location.host}/api/authorize/`;
  }
};

const initSignIn_remote = () => {
  const remoteLogin = document.getElementById("remote_login");
  remoteLogin.addEventListener("click", (event) => {
    if (event.target.closest(".google")) {
      handleSignIn_remote("google");
    } else if (event.target.closest(".inta")) {
      handleSignIn_remote("42Intra");
    }
  });
};
const initSignIn = () => {
  initFeedBack();
  const loginForm = document.getElementById("loginForm");
  loginForm.addEventListener("submit", handleSignIn);
  initSignIn_remote();
};

export default { initSignIn, alert_message, initFeedBack };

// {
//     "username":"yassine1",
//     "email": "maaloum.yassine@gmail.com",
//     "first_name": "ayss",
//     "last_name": "maal",
//     "password": "MAALOUM1111##33",
//     "confirm_password": "MAALOUM1111##33"
// }
// yassineMAA;
