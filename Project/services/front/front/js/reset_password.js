import { urlLocationHandler } from "./url-router.js";
import fun_sign from "./signin.js";

const handleResetPassword = (e) => {
  e.preventDefault();
  const data = {
    email: document.getElementById("email_reset").value.trim(),
  };
  if (!data.email) {
    fun_sign.alert_message("Missing value", "Enter email");
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
  fetch(`https://${window.location.host}/api/reset-password/`, {
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
    .then((data) => {
      fun_sign.alert_message("Succès", "A reset email has been sent.");
    })
    .catch((error) => {
      fun_sign.alert_message("Error", error.message);
    });
};

const initResetPassword = () => {
  fun_sign.initFeedBack();
  const resetPasswordForm = document.getElementById("resetPasswordForm");
  resetPasswordForm.addEventListener("submit", handleResetPassword);
};

export default initResetPassword;
//

// fetch("http://127.0.0.1:8000/api/update_password/", {
//   method: "PUT",
//   headers: {
//     "Content-Type": "application/json",
//   },
//   body: JSON.stringify(data),
//   credentials: "include",
// })
//   .then((response) => response.json())
//   .then((data) => {
//     if (data.success) {
//       alert("Mot de passe mis à jour avec succès !");
//       passwordField.value = "";
//       confirmPasswordField.value = "";
//     } else {
//       alert("Erreur lors de la mise à jour du mot de passe");
//     }
//   })
//   .catch((error) => {
//     fun_sign.alert_message("Error", error.message);
//   });
