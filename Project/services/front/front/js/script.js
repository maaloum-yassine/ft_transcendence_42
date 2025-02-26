const FriendManager = (() => {
  let users = [];
  let friendRequests = [];
  let currentMode = "users";

  let toggleBtn, userListContainer, searchInput;

  // Fetch all users excluding the authenticated user's friends

  const fetchNonFriends = async () => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/fetch_non_friends/`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      console.log("Non-Friends:", data.non_friends);
      users = data.non_friends.map((user) => ({
        id: user.id,
        name: user.username,
        image: user.avatar
          ? `https://${window.location.host}/media/${user.avatar}`
          : `https://${window.location.host}/media/avatars/default_avatar.png`,
        invitation_sent: user.invitation_sent,
      }));
      if (currentMode === "users") renderList(users);
    } catch (error) {
      console.error("Failed to fetch non-friends:", error);
    }
  };

  // Fetch friend requests
  const fetchFriendRequests = async () => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/list_requst_friend/`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log("API Response:", data);

      // Handle cases where 'requests' might be undefined
      const requests = data.requests || [];
      friendRequests = requests.map((request) => ({
        id: request.id || null,
        name: request.username || "Unknown",
        image: request.avatar || "https://via.placeholder.com/50",
      }));

      if (currentMode === "friendRequests") renderList(friendRequests);
    } catch (error) {
      console.error("Failed to fetch friend requests:", error);
    }
  };

  const acceptFriendRequest = async (username) => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/accept_friend_request/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ username_friend: username }),
        }
      );
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      console.log(`Friend request accepted for ${username}:`, data);
      alert(`Friend request accepted for ${username}!`);
      await fetchFriendRequests();
    } catch (error) {
      alert(`Failed to accept friend request for ${username}.`);
    }
  };

  // Reject a friend request
  const removeFriend = async (username) => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/remove_friend/`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ username_friend: username }),
        }
      );
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      console.log(`Friend successfully removed:`, data);
      alert(`Friend successfully removed: ${username}`);
      await fetchFriendRequests();
    } catch (error) {
      alert(`Failed to remove friend: ${username}.`);
    }
  };

  // Send friend invitation
  const sendInvite = async (username) => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/send_friend_request/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ username_friend: username }),
        }
      );
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      console.log(`Invite sent to user ${username}:`, data);
      alert(`Invite sent to user ${username}!`);
      fetchNonFriends(); // Refresh user list
    } catch (error) {
      alert(`Invitation is already sent/received from ${username}.`);
    }
  };

  // Render user/friend request list
  const renderList = (dataList) => {
    if (dataList.length === 0) {
      userListContainer.innerHTML = `
                  <h2>${
                    currentMode === "users"
                      ? "List of Users"
                      : "Friend Requests"
                  }</h2>
                  <p style="text-align: center; color: gray;">${
                    currentMode === "users"
                      ? "No users found."
                      : "No friend requests."
                  }</p>
              `;
      return;
    }

    userListContainer.innerHTML = `
              <h2>${
                currentMode === "users" ? "List of Users" : "Friend Requests"
              }</h2>
              ${dataList
                .map(
                  (data) => `
                  <div class="user">
                      <img src="${data.image}" alt="${
                    data.name
                  }" class="user-image">
                      <p>${data.name}</p>
                      ${
                        currentMode === "users"
                          ? `
                          <button class="action-btn chat-user-btn" data-username="${
                            data.name
                          }" 
                              style="display: ${
                                data.invitation_sent ? "none" : "inline-block"
                              };">
                              Invite
                          </button>
                      `
                          : ""
                      }
                      ${
                        currentMode === "friendRequests"
                          ? `
                          <button class="action-btn chat-user-btn visible" data-username="${data.name}">
                              Accept
                          </button>
                          <button class="reject-btn visible" data-username="${data.name}">
                              Reject
                          </button>
                      `
                          : ""
                      }
                  </div>
              `
                )
                .join("")}
          `;

    document.querySelectorAll(".action-btn.chat-user-btn").forEach((button) => {
      button.addEventListener("click", () => {
        const username = button.getAttribute("data-username");
        if (currentMode === "users") {
          sendInvite(username);
        } else {
          acceptFriendRequest(username);
        }
      });
    });

    document.querySelectorAll(".reject-btn").forEach((button) => {
      button.addEventListener("click", () => {
        const username = button.getAttribute("data-username");
        removeFriend(username);
      });
    });
  };

  // Main function to initialize the friend manager
  const initialize = async () => {
    toggleBtn = document.querySelector("button");
    userListContainer = document.getElementById("user-list");
    searchInput = document.getElementById("search-input");

    if (!toggleBtn || !userListContainer || !searchInput) {
      console.error("Required DOM elements not found");
      return;
    }

    toggleBtn.addEventListener("click", async () => {
      currentMode = currentMode === "users" ? "friendRequests" : "users";
      searchInput.value = "";
      if (currentMode === "users") {
        await fetchNonFriends();
      } else {
        await fetchFriendRequests();
      }
      toggleBtn.textContent =
        currentMode === "users"
          ? "Switch to Friend Requests"
          : "Switch to Users Requests";
    });

    searchInput.addEventListener("input", (event) => {
      const searchTerm = event.target.value.trim();
      const dataList = currentMode === "users" ? users : friendRequests;
      const filteredList = dataList.filter((item) =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      renderList(filteredList);
    });

    // Initial fetch
    await fetchNonFriends();
    await fetchFriendRequests();
  };

  return { initialize };
})();

export default FriendManager;
