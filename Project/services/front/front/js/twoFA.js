import { urlLocationHandler } from "./url-router.js";
import fun_sign from "./signin.js";

function initTwoFA_endpoint(code) {
  const url = `https://${window.location.host}/api/otp/`;
  const data = {
    code_otp: code,
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
    .then((data) => {
      history.pushState(null, "", "/home");
      urlLocationHandler();
    })
    .catch((error) => {
      fun_sign.alert_message("ERROR", error.message);
    });
}

const handleTwoFA = (e) => {
  e.preventDefault();

  const inputs = document.querySelectorAll(".code-input");

  const code = Array.from(inputs)
    .map((input) => input.value)
    .join("");

  if (code.length === 8) {
    initTwoFA_endpoint(code);
  } else {
    fun_sign.alert_message("Please enter a complete 8-digit code");
  }
};

const initTwoFA = () => {
  const inputs = document.querySelectorAll(".code-input");
  inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, "");
      if (e.target.value.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && e.target.value.length === 0 && index > 0) {
        inputs[index - 1].focus();
      }
    });
  });
  fun_sign.initFeedBack();
  const faForm = document.getElementById("2faForm");
  faForm.addEventListener("submit", handleTwoFA);
};

export default initTwoFA;
