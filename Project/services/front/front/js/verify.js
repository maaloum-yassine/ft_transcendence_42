import { urlLocationHandler } from "./url-router.js";
import fun_sign from "./signin.js";

const getErrHtml = () => {
  return new Promise((resolve, reject) => {
    fetch(`/templates/error/error_signup/error_signup.html`).then((res) => {
      return resolve(res.text());
    });
  });
};

const getSeccHtml = () => {
  return new Promise((resolve, reject) => {
    fetch(`/templates/sucess/signin_sucess.html`).then((res) => {
      return resolve(res.text());
    });
  });
};

const initVerifying = async () => {
  const errHtml = await getErrHtml();
  const succHtml = await getSeccHtml();
  const url = new URLSearchParams(window.location.search);
  const uid = url.get("uid");
  const token = url.get("token");
  console.log(uid, token);
  if (!token || !uid) {
    fun_sign.alert_message("Missing informations");
    return;
  }
  fetch(`https://${window.location.host}/api/verify_account/${uid}/${token}`, {
    method: "GET",
    credentials: "include",
  }).then((res) => {
    console.log(res);
    if (res.status != 200) {
      document.getElementById("verifyContainer").innerHTML = errHtml;
      return;
    }
    res.json().then((res) => {
      document.getElementById("verifyContainer").innerHTML = succHtml;
    });
  });
};



function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const handleResetPassConfirm = async (e) => {
  e.preventDefault();
  const data = {
    new_password: document.getElementById("new_password_reset").value,
    confirm_password: document.getElementById("confirm_password_reset").value,
  };

  if (!data.new_password || !data.confirm_password) {
    fun_sign.alert_message("Missing value", "Please enter all fields.");
    return;
  }
  const url = new URLSearchParams(window.location.search);
  const uid = url.get("uid");
  const token = url.get("token");
  if (!token || !uid) {
    fun_sign.alert_message(
      "ERROR",
      "Missing information. Please provide a valid token and uid."
    );
    await wait(1000);
    history.pushState(null, "", "/password_reset");
    urlLocationHandler();
    return;
  }
  try {
    const res = await fetch(
      `https://${window.location.host}/api/reset-password/${uid}/${token}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include",
      }
    );
    const responseData = await res.json();
    if (!res.ok) {
      console.log(responseData.error);
      if (responseData.error === "Token has expired.") {
        fun_sign.alert_message("ERROR", responseData.error);
        await wait(1000);
        history.pushState(null, "", "/password_reset");
        urlLocationHandler();
      }
      console.error("Error response:", responseData);
      fun_sign.alert_message("ERROR", responseData.error);
      return;
    } else {
      fun_sign.alert_message("Success", "Password reset successfully!");
      await wait(1000);
      history.pushState(null, "", "/signin");
      urlLocationHandler();
    }
  } catch (error) {
    fun_sign.alert_message("ERROR", responseData.error);
  }
};

const initResetPassConfirm = () => {
  fun_sign.initFeedBack();
  const resetPasswordForm = document.getElementById("resetPasswordForm");
  resetPasswordForm.addEventListener("submit", handleResetPassConfirm);
};

export default { initVerifying, initResetPassConfirm };
