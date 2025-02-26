import { urlLocationHandler } from "./url-router.js";

export const CGR_ = () => {
    const createForm = document.getElementById("create_form_name");
  
    if (createForm) {
        createForm.addEventListener("submit", (event) => {
            event.preventDefault();
            const roomName = document.getElementById('create_room_name').value;
            
            if (roomName.trim() !== '') {
                createGameRoom(roomName);
            } else {
                alert('Please enter a room name.');
            }
        });
    } else {
        console.error("Create form not found");
    }
};

function createGameRoom(roomName) {
    const formData = new FormData();
    formData.append("roomName", roomName);

    fetch(`https://${window.location.host}/api/create_friends_game/`, {
        method: "POST",
        credentials: 'include',
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(res => {
        alert(res.message);
        if (res.message === "Game room Joined successfully" || res.message === "Game room created successfully") {
            history.pushState({ roomName: res.room_name }, "", "/friends_mode");
            urlLocationHandler();
        } else {
            alert('Failed to create game room');
        }
    })
    .catch(err => {
        console.error("Error creating game room:", err);
        alert('Error creating game room');
    });
}