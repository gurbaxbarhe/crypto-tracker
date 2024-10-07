"""
The purpose of this file is to create a WebSocket that enables connection to the crypto_listings/markets/ws endpoint. 
It fetches data from api.py function get_assets() and then displays the data on a simply webpage.

NEXT STEPS
1) This is not a wss connection as stated in the requirements, it is a ws. I am still trying to change it to that 
with an HTTPS setup. I attempted this with the encrypted keys and cert I made but I was not implementing the logic correctly on
the server side.

2) Implement React instead of JS. Easier to work with components like data tables to nicely display data, can pass paramaters as 
props such as switching from USD to CAD, etc.
"""

# Imports
import asyncio  # To support asynchronous tasks
import json
from pathlib import Path

from api import get_assets
from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crypto Market Listing", version="1.0")

# Find frontend directory and and relevant files
frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")

# Store previous asset data to compare changes
previous_data = None


# WebSocket endpoint
@app.websocket("/crypto_listings/markets/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send_fresh_data(vs_currency="cad"):
        """
        Fetches the latest asset data from api.py and sends to client (frontend in this case) if there's a change
        """
        try:
            global previous_data  # Defining placeholder for data to check if there are any chances
            fresh_data = get_assets(vs_currency)

            # Check if there is a change in data
            if fresh_data != previous_data:
                response_data = {
                    "channel": "rates",
                    "event": "data",
                    "data": fresh_data,
                }
                await websocket.send_text(json.dumps(response_data, indent=4))
                previous_data = fresh_data  # Update previous data

        except Exception as e:
            print(f"Error fetching data: {e}")

    # Background task to continuously check API for changes
    async def continuous_check():
        while True:
            await send_fresh_data()
            await asyncio.sleep(
                10
            )  # Check every 10 seconds. For real-world applications, this would be far faster

    try:
        # Start continuous check when the WebSocket connection opens
        task = asyncio.create_task(continuous_check())

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Check for subscription event
            if (
                message.get("event") == "subscribe"
                and message.get("channel") == "rates"
            ):
                vs_currency = message.get("vs_currency", "cad")
                print("Subscription made, fetching new data...")
                await send_fresh_data(vs_currency)

    except WebSocketDisconnect:
        print("Client is disconnected")
        task.cancel()  # Stop the background task when client disconnects


# Serve the HTML page
@app.get("/")
async def get():
    index_file = frontend_path / "index.html"
    return HTMLResponse(content=index_file.read_text())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        # Uncomment and add SSL setup if using HTTPS
        # ssl_keyfile=".certifications/cert.pem",
        # ssl_certfile=".certifications/cert.pem",
    )
