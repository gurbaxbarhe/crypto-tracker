// JS file for functionality

const messages = document.getElementById("messages");
const subscribebtn = document.getElementById("subscribebtn");
let statusMessage = document.getElementById("statusMessageOpen");
let ws;

function initializeWebSocket() {
    ws = new WebSocket("ws://localhost:8000/crypto_listings/markets/ws");

    ws.onopen = function() {
        console.log("Connection opened");
        statusMessage.textContent = "Connection is open, subscribe to data";
        subscribebtn.disabled = false; // Enable button to fetch data
    };

    ws.onmessage = function(event) {
        const parsedData = JSON.parse(event.data);
        messages.textContent = JSON.stringify(parsedData, null, 4);  // Make the data in JSON format look pretty
    };

    ws.onclose = function() {
        console.log("Connection closed");
        statusMessage.textContent = "Connection closed";
        statusMessage.id = "statusMessageClosed";  // Change button to red
        subscribebtn.disabled = true; // Disable the button if the connection is closed
    };

    ws.onerror = function(error) {
        console.error("Error:", error);
        ws.close(); // Close the connection if an error occurs
    };
}

function subscribe() {
    if (ws.readyState === WebSocket.OPEN) {
        const subscriptionMessage = {
            event: "subscribe",
            channel: "rates"
        };
        console.log("Subscription message:", subscriptionMessage);  // Log the subscription message to check received
        ws.send(JSON.stringify(subscriptionMessage));

        // Update last updated time when button is clicked such that users knows latest time of data fetch
        const lastUpdatedElement = document.getElementById("lastUpdatedTime");
        const currentTime = new Date().toLocaleString();  // Get current time
        lastUpdatedElement.textContent = `Latest data fetch: ${currentTime}`;
    } else {
        console.log("Connection is not open, please refresh");
    }
}

// Initialize WebSocket on page load
initializeWebSocket(); 