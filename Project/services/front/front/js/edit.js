import fun_sign from "./signin.js";
import { urlLocationHandler } from "./url-router.js";

const edit = () => {
  const logoLink = document.querySelector(".logo");

  if (logoLink) {
    logoLink.addEventListener("click", (e) => {
      e.preventDefault();
      history.pushState(null, "", "/home");
      urlLocationHandler();
    });
  }
  fun_sign.initFeedBack();
  const profilePhoto = document.getElementById("profilePhoto");
  const openImageModal = document.getElementById("openImageModal");
  const imageUploadModal = document.getElementById("imageUploadModal");
  const photoUpload = document.getElementById("photoUpload");
  const uploadProfileImage = document.getElementById("uploadProfileImage");

  const openTwoFactorModal = document.getElementById("openTwoFactorModal");
  const twoFactorModal = document.getElementById("twoFactorModal");

  const updateUserInfoBtn = document.getElementById("updateUserInfoBtn");
  const updatePasswordBtn = document.getElementById("updatePasswordBtn");

  const usernameField = document.getElementById("Username_edit");
  const firstNameField = document.getElementById("FirstName_edit");
  const lastNameField = document.getElementById("LastName_edit");
  const emailField = document.getElementById("email_edit");
  const passwordField = document.getElementById("Password_edit");
  const confirmPasswordField = document.getElementById("Confirm_Password_edit");
  const deactivateTwoFactor = document.getElementById("deactivateTwoFactor");

  fetch(`https://${window.location.host}/api/profile/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message === "Profile retrieved successfully") {
        if (usernameField) usernameField.value = data.data.username;
        if (firstNameField) firstNameField.value = data.data.first_name;
        if (lastNameField) lastNameField.value = data.data.last_name;
        if (emailField) emailField.value = data.data.email;
        if (data.data.active_2fa == true) {
          deactivateTwoFactor.textContent = "Désactiver";
        } else {
          deactivateTwoFactor.textContent = "Activate";
        }

        // if (data.data.active_2fa == true) activateTwoFactor.disabled = true;
        // else deactivateTwoFactor.disabled = true;

        if (profilePhoto && data.data.avatar) {
          const avatarUrl = data.data.avatar;
          if (avatarUrl) {
            profilePhoto.src = avatarUrl;
            profilePhoto.style.display = "block";
          } else {
            profilePhoto.src = "/path/to/default/avatar.jpg";
          }
        }
      } else {
        fun_sign.alert_message(
          "Erreur lors du chargement des données du profil."
        );
      }
    })
    .catch((error) => {
      console.error("Erreur:", error);
      fun_sign.alert_message(
        "Une erreur est survenue lors du chargement des données du profil."
      );
    });
  if (openImageModal && imageUploadModal) {
    openImageModal.addEventListener("click", () => {
      imageUploadModal.style.display = "flex";
    });

    const imageModalClose = imageUploadModal.querySelector(".modal-close");
    if (imageModalClose) {
      imageModalClose.addEventListener("click", () => {
        imageUploadModal.style.display = "none";
      });
    }

    imageUploadModal.addEventListener("click", (e) => {
      if (e.target === imageUploadModal) {
        imageUploadModal.style.display = "none";
      }
    });
  }

  if (openTwoFactorModal && twoFactorModal) {
    openTwoFactorModal.addEventListener("click", () => {
      twoFactorModal.style.display = "flex";
    });

    const twoFactorModalClose = twoFactorModal.querySelector(".modal-close");
    if (twoFactorModalClose) {
      twoFactorModalClose.addEventListener("click", () => {
        twoFactorModal.style.display = "none";
      });
    }

    twoFactorModal.addEventListener("click", (e) => {
      if (e.target === twoFactorModal) {
        twoFactorModal.style.display = "none";
      }
    });
    //! to remeber
    if (deactivateTwoFactor) {
      deactivateTwoFactor.addEventListener("click", () => {
        const Data = {
          active_2fa:
            deactivateTwoFactor.textContent === "Désactiver" ? "false" : "true",
        };
        fetch(`https://${window.location.host}/api/active_2fa/`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(Data),
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
            deactivateTwoFactor.textContent =
              deactivateTwoFactor.textContent === "Désactiver"
                ? "Activate"
                : "Désactiver";
            // activateTwoFactor.disabled = false;
            // deactivateTwoFactor.disabled = true;
            twoFactorModal.style.display = "none";
            fun_sign.alert_message("Success", "successfully updated");
          })
          .catch((error) => {
            fun_sign.alert_message("ERREOR", "CHECK YOUR INPUT");
          });
      });
    }
  }

  if (updateUserInfoBtn) {
    updateUserInfoBtn.addEventListener("click", () => {
      const Data = {
        username: usernameField.value,
        email: emailField.value,
        first_name: firstNameField.value,
        last_name: lastNameField.value,
      };
      fetch(`https://${window.location.host}/api/update/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(Data),
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
          fun_sign.alert_message("Success", "user was successfully updated");
          setTimeout(() => {
            history.pushState(null, "", "/profile");
            urlLocationHandler();
          }, 2000);
        })
        .catch((error) => {
          // console.log(errorData);
          fun_sign.alert_message("Error", error.message);
        });
    });
  }

  if (updatePasswordBtn) {
    updatePasswordBtn.addEventListener("click", () => {
      const password = passwordField.value;
      const confirmPassword = confirmPasswordField.value;
      const data = {
        new_password: password,
        confirm_password: confirmPassword,
      };
      if (password !== confirmPassword) {
        fun_sign.alert_message("ERROR", "the passwords are not the same");
        return;
      } else if (!password || !confirmPassword) {
        fun_sign.alert_message("ERROR", "empty field");
        return;
      }

      fetch(`https://${window.location.host}/api/update_password/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include",
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((responseData) => {
              fun_sign.alert_message("ERROR", responseData.error);
              throw new Error(responseData.error);
            });
          }
          return response.json();
        })
        .then((responseData) => {
          fun_sign.alert_message("Success", "Password reset successfully!");
          setTimeout(() => {
            history.pushState(null, "", "/home");
            urlLocationHandler();
          }, 2000);
          return;
        })
        .catch((error) => {
          fun_sign.alert_message("ERROR", error.message);
          return;
        });
    });
  }

  if (uploadProfileImage && photoUpload) {
    uploadProfileImage.addEventListener("click", () => {
      const file = photoUpload.files[0];
      console.log(file);

      if (file) {
        const formData = new FormData();
        formData.append("avatar", file);
        console.log(formData.get("avatar"));

        fetch(`https://${window.location.host}/api/upload_avatar/`, {
          method: "POST",
          body: formData,
          credentials: "include",
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
            if (data.avatar_url) {
              fun_sign.alert_message(
                "Photo de profil mise à jour avec succès !"
              );
              if (imageUploadModal) {
                imageUploadModal.style.display = "none";
              }
            } else {
              fun_sign.alert_message(
                "Erreur lors du téléchargement de la photo"
              );
            }
          })
          .catch((error) => {
            console.error("Erreur:", error);
            fun_sign.alert_message(
              "Une erreur est survenue lors du téléchargement de l'image."
            );
          });
      } else {
        fun_sign.alert_message("Veuillez sélectionner une image");
      }
    });
  }

  const openImageUploadBtn = document.getElementById("openImageUploadBtn");

  openImageUploadBtn.addEventListener("click", () => {
    photoUpload.click();
  });

  photoUpload.addEventListener("change", (e) => {
    console.log(e.currentTarget.files[0]);
    if (e.currentTarget.files.length > 0) {
      openImageUploadBtn.textContent = e.currentTarget.files[0].name;
      profilePhoto.src = URL.createObjectURL(e.target.files[0]);
    } else openImageUploadBtn.textContent = "Click to select an image";
  });
};

export default edit;
