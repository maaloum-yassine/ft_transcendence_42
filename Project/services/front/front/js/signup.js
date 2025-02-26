import { urlLocationHandler } from "./url-router.js";
import fun_sign from "./signin.js";

const handleSignUp = (e) => {
  e.preventDefault();
  const data = {
    username: document.getElementById("Username").value.trim(),
    email: document.getElementById("Email").value.trim(),
    first_name: document.getElementById("First_Name").value.trim(),
    last_name: document.getElementById("Last_Name").value.trim(),
    password: document.getElementById("Password").value.trim(),
    confirm_password: document.getElementById("Confirm_Password").value.trim(),
  };
  console.log("Données envoyées :", data);
  if (
    !data.username ||
    !data.email ||
    !data.first_name ||
    !data.last_name ||
    !data.password ||
    !data.confirm_password
  ) {
    fun_sign.alert_message("Missing values", "All inputs are required");
    return;
  }
  if (data.password !== data.confirm_password) {
    fun_sign.alert_message("Password mismatch", "Passwords do not match");
    return;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    fun_sign.alert_message(
      "Invalid email",
      "Please provide a valid email address"
    );
    return;
  }
  const url = `https://${window.location.host}/api/signup/`;
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
            errorData.message || `HTTP Error: ${response.status}`
          );
        });
      }
      return response.json();
    })
    .then((data) => {
      fun_sign.alert_message(
        "Success",
        "Your registration has been successfully registered. A verification email has been sent to you. Please check your email to activate your account. Until you verify your email address, you will not be able to log in."
      );
      console.log("Réponse du backend :", data);
    })
    .catch((error) => {
      fun_sign.alert_message("Error", error.message);
    });
};

const initSignUp = () => {
  fun_sign.initFeedBack();
  const signupForm = document.getElementById("signupform");
  signupForm.addEventListener("submit", handleSignUp);
};

export default { initSignUp };
// MAALOUM0000#
// ymaloume
