import fun_sign from "./signin.js";

const BlockedUserManager = (() => {
  let blockedUsers = [];
  let userListContainer;

  // Fetch blocked users from the API endpoint
  const fetchBlockedUsers = async () => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/blocked-users/`,
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
      console.log("Blocked Users:", data.blocked_users);

      // Map the blocked users into a more usable format
      blockedUsers = data.blocked_users.map((user) => ({
        id: user.id,
        username: user.username,
        avatar: user.avatar
          ? `${user.avatar}`
          : `https://${window.location.host}/media/avatars/default_avatar.png`, // Default avatar if none exists
      }));

      // Render the list of blocked users
      renderList(blockedUsers);
    } catch (error) {
      console.error("Failed to fetch blocked users:", error);
    }
  };

  // Unblock a user
  const unblockUser = async (userId) => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/unblock_user/?friend_id=${userId}`,
        {
          method: "PATCH",
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
      console.log(`User with ID ${userId} unblocked:`, data);
      fun_sign.alert_message(`User has been unblocked!`);
      fun_sign.initFeedBack();
      await fetchBlockedUsers(); // Refresh blocked users list
    } catch (error) {
      console.error(`Failed to unblock user with ID ${userId}:`, error);
    }
  };

  // Remove a user
  const removeUser = async (username) => {
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
      console.log(`User ${username} removed:`, data);
      fun_sign.alert_message(`User ${username} has been removed!`);
      fun_sign.initFeedBack();

      await fetchBlockedUsers(); // Refresh blocked users list
    } catch (error) {
      console.error(`Failed to remove user ${username}:`, error);
    }
  };

  // Render the blocked users list
  const renderList = (dataList) => {
    if (dataList.length === 0) {
      userListContainer.innerHTML = `
		  <h2>Blocked Users</h2>
		  <p style="text-align: center; color: white;">No blocked users found.</p>
		`;
      return;
    }

    userListContainer.innerHTML = `
		<h2>Blocked Users</h2>
		${dataList
      .map(
        (data) => `
			  <div class="blocked-user">
				<div class="user-info">
				  <img src="${data.avatar}" alt="${data.username}" class="user-image" />
				  <p class="username">${data.username}</p>
				</div>
				<div class="actions">
				  <button class="button" data-id="${data.id}">Unblock</button>
				  <button class="button" data-username="${data.username}">Remove</button>
				</div>
			  </div>
			`
      )
      .join("")}
	  `;

    // Add event listeners to unblock buttons
    document.querySelectorAll(".button").forEach((button) => {
      button.addEventListener("click", () => {
        const userId = button.getAttribute("data-id"); // Fetch the user ID
        unblockUser(userId); // Pass the user ID to the unblock function
      });
    });

    // Add event listeners to remove buttons
    document.querySelectorAll(".button").forEach((button) => {
      button.addEventListener("click", () => {
        const username = button.getAttribute("data-username"); // Fetch the username
        removeUser(username); // Pass the username to the remove function
      });
    });
  };

  // Main function to initialize the blocked user manager
  const initialize = async () => {
    userListContainer = document.getElementById("user-list");

    if (!userListContainer) {
      console.error("Required DOM element not found");
      return;
    }

    // Fetch and render the blocked users list
    await fetchBlockedUsers();
  };

  return { initialize };
})();

export default BlockedUserManager;
