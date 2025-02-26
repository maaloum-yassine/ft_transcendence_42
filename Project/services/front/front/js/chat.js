import fun_sign from "./signin.js";

const ChatManager = (() => {
  let friends = [];
  let filteredFriends = [];
  let notificationSocket = null;
  let chatSocket = null;
  let sender = null;
  let receiver = null;
  let senderName = null;
  let receiverName = null;
  let activeChatSelected = false;
  const messageQueue = [];
  let onlineUsers = new Set();

  const createWebSocket = (url) => {
    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    return new WebSocket(`${protocol}${window.location.host}${url}`);
  };

  const isMessageEmpty = (message) => {
    return !message.trim();
  };

  const scrollToBottom = (element) => {
    element.scrollTop = element.scrollHeight;
  };
  const getElement = (selector) => document.querySelector(selector);
  const getElements = (selector) => document.querySelectorAll(selector);

  const disableMessageInput = () => {
    const messageInput = getElement("#message-input");
    if (messageInput) {
      messageInput.disabled = true;
      messageInput.placeholder = "Please select a friend to start chatting...";
    }
  };

  const enableMessageInput = () => {
    const messageInput = getElement("#message-input");
    if (messageInput) {
      messageInput.disabled = false;
      messageInput.placeholder = "Type a message...";
      messageInput.focus();
    }
  };

  const createFriendElement = (friend) => {
    return `
		<li class="selectable-item friend" 
    data-id="${friend.id}"
    data-name="${friend.name || "Unnamed"}"
    data-authid="${friend.auth_user_id}"
    data-authname="${friend.auth_user_name}">
    <div class="avatarContainer">
    <img src="${friend.imageURL || "default-avatar.jpg"}" 
    class="avatar" 
    alt="${friend.name || "No avatar"}">
    </div>
    ${friend.name || "Unnamed"}
    <span class="connected-icon connected connected${friend.id}" 
				style="display: ${friend.isOnline ? "block" : "none"}">🟢</span>
		  <span class="notification-bell notification${friend.id}" 
      style="display: none">🔔</span>
      </li>
      `;
  };

  const updateContactInfo = (contactInfo, friend) => {
    contactInfo.innerHTML = `
      <h1 class="friend_name">${friend.name || "Unnamed"}</h1>
      <nav class="user-panel" aria-label="User actions">
      <a href="/friend_profile?id=${
        friend.id
      }" class="chat-button" aria-label="View profile">
      View profile
      </a>
      <a href="#" class="chat-button" aria-label="Invite to a game">
      Invite to a game
      </a>
      <a href="#" id="block" class="chat-button" aria-label="Block">
      Block
      </a>
      </nav>
      `;
  };

  const createMessageElement = (messageData) => {
    const newDiv = document.createElement("div");
    newDiv.classList.add("message", messageData.type);
    newDiv.textContent = messageData.text;
    return newDiv;
  };

  const formatMessage = (msg, currentSender) => {
    const isCurrentUser = msg.senderj != currentSender;
    return {
      text: `${isCurrentUser ? msg.authuser : "me"}: ${msg.message}`,
      type: isCurrentUser ? "sent" : "received",
    };
  };

  const fetchFriends = async () => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/list_friends/`,
        {
          method: "GET",
          credentials: "include",
        }
      );
      if (!response.ok) {
        throw new Error(`Failed to fetch data, status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching data:", error);
      throw error;
    }
  };

  const isBlockFriend = async (friendId) => {
    try {
      const response = await fetch(
        `https://${window.location.host}/api/check_block_status/?id=${friendId}`,
        {
          method: "GET",
          credentials: "include", // Include cookies for authentication if required
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        console.error(
          "Error fetching block status:",
          errorData.error || response.statusText
        );
        return false;
      }

      const data = await response.json();
      return data.is_blocked;
    } catch (error) {
      console.error("Error fetching block status:", error);
      return false; 
    }
  };
  const blockFriend = async (friendId) => {
    const response = await fetch(
      `https://${window.location.host}/api/block_friend/${friendId}/`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      }
    );

    if (!response.ok) {
      throw new Error("Failed to block friend");
    }
    return response;
  };

  const initializeWebSockets = () => {
    const connectSocket = createWebSocket("/ws/second/");
    sender = getElement(".friend")?.getAttribute("data-authid") || null;
    if (sender) {
      notificationSocket = createWebSocket(`/ws/${sender}/`);
    }
    setupSocketEventListeners(connectSocket);
  };

  const handleBeforeUnload = () => {
    if (chatSocket) {
      chatSocket.close();
    }
  };

  const handlePopState = () => {
    if (chatSocket) {
      chatSocket.close();
    }
  };

  const setupSocketEventListeners = (connectSocket) => {
    connectSocket.onopen = () => {
      if (sender) {
        connectSocket.send(
          JSON.stringify({
            sender,
            status: "connected",
          })
        );
      }
    };

    if (notificationSocket) {
      setupNotificationSocket();
    }

    setupConnectSocketMessages(connectSocket);
    setupFriendClickHandlers();

    setupMessageInput();
    disableMessageInput();
  };

  const setupNotificationSocket = () => {
    if (!notificationSocket) return;

    notificationSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const paragraph = getElement(`span.notification${data.sender}`);
      if (paragraph) {
        paragraph.style.display = "block";
      }
    };
  };

  const setupConnectSocketMessages = (connectSocket) => {
    connectSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      friends = friends.map((friend) => ({
        ...friend,
        isOnline: data.connected_users.some(
          (user) => user.user_id === friend.id
        ),
      }));
      if (filteredFriends.length > 0) {
        filteredFriends = filteredFriends.map((friend) => ({
          ...friend,
          isOnline: data.connected_users.some(
            (user) => user.user_id === friend.id
          ),
        }));
      }

      populateFriendList(
        filteredFriends.length > 0 ? filteredFriends : friends
      );
    };
  };

  const setupChatSocket = (friend) => {
    receiver = friend.id;
    sender = friend.auth_user_id;
    receiverName = friend.name;
    senderName = friend.auth_user_name;
    activeChatSelected = true;

    const url =
      receiver && sender
        ? `/ws/chat/${Number(receiver) > Number(sender) ? receiver : sender}/${
            Number(receiver) > Number(sender) ? sender : receiver
          }/`
        : null;

    if (!url) return;

    if (chatSocket) {
      chatSocket.close();
    }

    chatSocket = createWebSocket(url);
    setupChatSocketEventListeners();
    enableMessageInput();
  };

  const setupChatSocketEventListeners = () => {
    if (!chatSocket) return;

    chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      updateChatWindow(data);
    };

    chatSocket.onopen = () => {
      while (messageQueue.length > 0) {
        const message = messageQueue.shift();
        if (message) sendMessage(message);
      }
    };
  };

  const updateChatWindow = (data) => {
    const chatWindow = getElement("#chat-window");
    if (!chatWindow) return;

    if (data.type === "previous_messages") {
      chatWindow.innerHTML = "";
      data.messages.forEach((msg) => {
        appendMessageToChatWindow(msg, chatWindow, data.type);
      });
    } else {
      appendMessageToChatWindow(data, chatWindow, data.type);
    }
    scrollToBottom(chatWindow);
  };

  const appendMessageToChatWindow = (msg, chatWindow, type) => {
    const messageData = formatMessage(msg, sender);
    const messageElement = createMessageElement(messageData);
    if (!messageData.text.startsWith("me:") && type !== "previous_messages") {
      const audio = new Audio("../templates/chat/notification.mp3");
      audio.play().catch((error) => {
        console.error("Error playing audio:", error);
      });
    }
    chatWindow.appendChild(messageElement);
  };

  const sendMessage = (message) => {
    if (
      !chatSocket ||
      !sender ||
      !receiver ||
      !senderName ||
      !activeChatSelected
    )
      return;

    const messageData = {
      message,
      senderj: sender,
      reciever: receiver,
      authuser: senderName,
    };

    chatSocket.send(JSON.stringify(messageData));
  };

  const queueMessage = (message) => {
    messageQueue.push(message);
  };

  const sendNotification = () => {
    if (!receiver) return;

    const notificationSocket = createWebSocket(`/ws/${receiver}/`);
    notificationSocket.onopen = () => {
      if (sender) {
        notificationSocket.send(
          JSON.stringify({
            sender,
          })
        );
      }
    };
  };

  const processFriendsData = (userData) => {
    if (!userData || !Array.isArray(userData) || userData.length === 0) {
      getElement("#friends").innerHTML = "No users found.";
      return;
    }

    const authUser = userData[0];
    const authUserId = authUser.id_auth;
    const authUserName = authUser.auth_username;

    friends = userData.map((user) => ({
      id: user.id_friend,
      name: user.username || "",
      email: user.email || "",
      phone: user.phone || "",
      imageURL: user.avatar || "default-avatar.jpg",
      auth_user_id: authUserId,
      auth_user_name: authUserName,
      isOnline: false,
    }));

    filteredFriends = friends.filter((friend) => friend.id !== undefined);
    populateFriendList(filteredFriends);
  };

  const initializeFriendsList = () => {
    const searchInput = getElement(".searchTerm");
    const searchButton = getElement(".searchButton");

    const handleSearch = () => {
      const searchValue = searchInput.value.toLowerCase().trim();
      if (Array.isArray(friends)) {
        filteredFriends =
          searchValue === ""
            ? friends.filter((friend) => friend.id !== undefined)
            : friends.filter(
                (friend) =>
                  friend.id !== undefined &&
                  friend.name.toLowerCase().includes(searchValue)
              );
        populateFriendList(filteredFriends);
      }
    };

    if (searchButton) {
      searchButton.addEventListener("click", (e) => {
        e.preventDefault();
        handleSearch();
      });
    }

    if (searchInput) {
      searchInput.addEventListener("input", handleSearch);
    }
  };

  const populateFriendList = (friendsList) => {
    const container = getElement("#friends");
    if (!container) {
      console.error("The 'friends' container was not found in the DOM.");
      return;
    }

    container.innerHTML =
      friendsList.length === 0
        ? "<li>No matching users found.</li>"
        : friendsList.map((friend) => createFriendElement(friend)).join("");

    setupFriendClickHandlers();
  };

  const setupFriendClickHandlers = () => {
    getElements(".friend").forEach((element) => {
      element.addEventListener("click", () => {
        const friendData = {
          id: element.getAttribute("data-id"),
          name: element.getAttribute("data-name"),
          auth_user_id: element.getAttribute("data-authid"),
          auth_user_name: element.getAttribute("data-authname"),
          imageURL: element.querySelector("img.avatar").src,
          isOnline:
            element.querySelector(".connected-icon").style.display === "block",
        };
        selectFriend(friendData, element);
      });
    });
  };
  function randomInteger(max) {
    return Math.floor(Math.random() * max);
  }
  const selectFriend = (friend, element) => {
    const notificationElement = getElement(`span.notification${friend.id}`);
    if (notificationElement) {
      notificationElement.style.display = "none";
    }
    updateChatInterface(friend);

    const contactImage = getElement("#contact-image");
    if (contactImage) {
      contactImage.src = friend.imageURL || "default-image.png";
    }
    createActionLinks(friend);
    setupChatSocket(friend);
    setupBlockButton(friend, element);
  };

  const createActionLinks = (friend) => {
    const contactInfo = getElement("#contact-details");
    if (!contactInfo) {
      console.error("Contact info container not found.");
      return;
    }

    contactInfo.innerHTML = `<h1 class="friend_name">${
      friend.name || "Unnamed"
    }</h1>`;
    // <img src="${friend.imageURL || "default-avatar.jpg"}"
    // 		 class="avatar"
    // 		 alt="${friend.name || "No avatar"}">
    const divProfile = document.createElement("div");
    divProfile.className = "avatarContainer";

    const imgprofile = document.createElement("img");
    imgprofile.src = `${friend.imageURL || "default-avatar.jpg"}`;
    imgprofile.alt = `"${friend.name || "No avatar"}"`;
    imgprofile.id = "contact-image";

    const viewProfileLink = document.createElement("a");
    viewProfileLink.href = `/friend_profile?id=${friend.id}`;
    viewProfileLink.className = "chat-button";
    viewProfileLink.setAttribute("aria-label", "View profile");
    viewProfileLink.textContent = "View profile";

    const inviteToGameLink = document.createElement("a");
    inviteToGameLink.href = "#";
    inviteToGameLink.className = "chat-button";
    inviteToGameLink.setAttribute("aria-label", "Invite to a game");
    inviteToGameLink.textContent = "Invite to a game";
    inviteToGameLink.onclick = () => {
    sendMessage("https://127.0.0.1/create_friends_game");
    sendMessage("The Game is created with the id  " + randomInteger(100000000));
    fun_sign.initFeedBack();
    fun_sign.alert_message(`Invitation sent to ${friend.name}`);
    sendNotification();
    };

    // Create "Block" link
    const blockLink = document.createElement("a");
    blockLink.href = "#";
    blockLink.id = "block";
    blockLink.className = "chat-button";
    blockLink.setAttribute("aria-label", "Block");
    blockLink.textContent = "Block";
    blockLink.onclick = async (e) => {
      e.preventDefault();
      try {
        await blockFriend(friend.id);
        handleSuccessfulBlock(friend, contactInfo);
      } catch (error) {
        fun_sign.alert_message(
          "There was an error blocking the friend. Please try again later."
        );
        fun_sign.initFeedBack();
      }
    };
    contactInfo.appendChild(imgprofile);
    contactInfo.appendChild(viewProfileLink);
    contactInfo.appendChild(inviteToGameLink);
    contactInfo.appendChild(blockLink);
  };
  const deleteAll = (parentId) => {
    const parentElement = document.getElementById(parentId);
    if (!parentElement) {
      console.error(`Parent element with ID "${parentId}" not found.`);
      return;
    }

    Array.from(parentElement.children).forEach((child) => {
      parentElement.removeChild(child);
    });
  };

  const updateChatInterface = (friend) => {
    const chatWindow = getElement("#chat-window");
    const contactInfo = getElement("#contact-info");
    const contactImage = getElement("#contact-image");

    if (contactInfo) {
      contactInfo.dataset.id_friend = friend.id;
      updateContactInfo(contactInfo, friend);
    }

    if (contactImage) {
      contactImage.src = friend.imageURL || "default-image.png";
    }
  };

  const setupBlockButton = (friend, element) => {
    const blockButton = getElement("#block");
    if (blockButton) {
      blockButton.onclick = async () => {
        try {
          await blockFriend(friend.id);
          handleSuccessfulBlock(friend, element);
        } catch (error) {
          fun_sign.initFeedBack();
          fun_sign.alert_message(
            "There was an error blocking the friend. Please try again later."
          );
        }
      };
    }
  };
  const removeFriendElement = (receiver) => {
    const friendElement = document.querySelector(
      `.friend[data-id="${receiver}"]`
    );
    if (friendElement) {
      friendElement.remove(); // Remove the friend element
    } else {
      console.error(`No element found with data-id="${receiver}"`);
    }
  };
  const handleSuccessfulBlock = (friend, element) => {
    fun_sign.initFeedBack();
    fun_sign.alert_message(`You have successfully blocked ${friend.name}`);
    element.style.display = "none";

    const contactImage = getElement("#contact-image");
    const chatWindow = getElement("#chat-window");
    if (!chatWindow) return;
    chatWindow.innerHTML = "";
    activeChatSelected = false;
    contactImage.src = "";
    disableMessageInput();

    const parentElement = document.getElementById("contact-details");
    if (!parentElement) {
      console.error("No element found with id contact-details");
      return;
    }

    const imageElement = document.getElementById("contact-image");
    if (!imageElement) {
      console.error("No image element found with id contact-image");
      return;
    }

    Array.from(parentElement.children).forEach((child) => {
      if (child !== imageElement) {
        parentElement.removeChild(child);
      }
    });

    const paragraph = document.createElement("p");
    paragraph.textContent = "Select a contact to see details.";
    parentElement.appendChild(paragraph);
  };

  const setupMessageInput = () => {
    const messageInput = getElement("#message-input");
    const messagesend = document.getElementById("send-button");

    if (!messageInput) return;

    messageInput.onkeyup = async (e) => {
      const bfriend = await isBlockFriend(receiver);


      if (!bfriend) 
      {
        if (e.keyCode === 13 && activeChatSelected) 
        {
          await handleMessageSend(messageInput); 
        }
      } else {
        const imge = document.getElementById("contact-image");
        fun_sign.initFeedBack();
        fun_sign.alert_message("the user is blocked");
      
        removeFriendElement(receiver);
        deleteAll("chat-window");
        const img = document.getElementById("contact-image");
        img.src = "";
        img.alt = "";
        const panelOptions = document.querySelectorAll("a.chat-button");
        panelOptions.forEach((option) => {
          option.remove();
        });
        const nick = document.getElementsByClassName("friend_name")[0];
        if (nick) nick.remove();
        friends = friends.filter((friend) => friend.id !== receiver);
        filteredFriends = filteredFriends.filter(
          (friend) => friend.id !== receiver
        );
      }
    };

    if (messagesend) {
      messagesend.onclick = async () => {
        const bfriend = await isBlockFriend(receiver);
        if (!bfriend) {
          if (activeChatSelected) await handleMessageSend(messageInput); 
        } else {
          removeFriendElement(receiver);
          deleteAll("chat-window");
          const img = document.getElementById("contact-image");
          img.src = "";
          img.alt = "";
          const panelOptions = document.querySelectorAll("a.chat-button"); 
          panelOptions.forEach((option) => {
            option.remove();
          });
          const nick = document.getElementsByClassName("friend_name")[0];
          if (nick) nick.remove();
          friends = friends.filter((friend) => friend.id !== receiver);
          filteredFriends = filteredFriends.filter(
            (friend) => friend.id !== receiver
          );
        }
      };
    }
  };

  async function handleMessageSend(messageInput) {
    const message = messageInput.value;
    if (isMessageEmpty(message) || !activeChatSelected) return;

    if (chatSocket?.readyState === WebSocket.OPEN) {
      sendMessage(message);
      messageInput.value = "";
    } else {
      queueMessage(message);
    }

    sendNotification();
  }

  const initialize = async () => {
    try {
      const userData = await fetchFriends();
      processFriendsData(userData);
      initializeWebSockets();
      initializeFriendsList();
      window.addEventListener("beforeunload", handleBeforeUnload);
      window.addEventListener("popstate", handlePopState);
    } catch (error) {
      console.error("Failed to initialize chat manager:", error);
      getElement("#friends").innerHTML =
        "An error occurred while fetching your friends.";
    }
  };

  return {
    initialize,
  };
})();

export default ChatManager;
