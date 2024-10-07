"""
The purpose of this file is to create a WebSocket that enables connection to the crypto_listings/markets/ws endpoint. 
It fetches data from api.py function get_assets() and then displays the data on a simply webpage.

NEXT STEPS
1) This is not a wss connection as stated in the requirements, it is a ws. I am still trying to change it to that 
with an HTTPS setup. I attempted this with the encrypted keys and cert I made but I was not implementing the logic correctly on
the server side.

2) At the moment, the data is fetched whenever the "Subscribe" button is clicked on the UI. This should only change when there is 
a change in the data, aka an async function named "check_api()" that checks if there are any changes. If there are it merges these  

3) Implement React instead of JS. Easier to work with components like data tables to nicely display data, can pass paramaters as 
props such as switching from USD to CAD, etc.
"""

# Imports
import json
from pathlib import Path

from api import get_assets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Crypto Market Listing", version="1.0")

# Find frontend directory and and relevant files (cannot directly call it for whatever reason)
frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")


# WebSocket endpoint for handling subscriptions called crypto_listings/markets/ws
@app.websocket("/crypto_listings/markets/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send_fresh_data(vs_currency="cad"):
        """
        Fetches the latest asset data from api.py and sends to client
        """
        try:
            fresh_data = get_assets(vs_currency)
            response_data = {
                "channel": "rates",
                "event": "data",
                "data": fresh_data,
            }
            await websocket.send_text(json.dumps(response_data, indent=4))
        except Exception as e:
            print(f"Error fetching data: {e}")

    try:
        while True:
            # Client will click subscribe to load data
            data = await websocket.receive_text()
            message = json.loads(data)

            # Check if the message is a subscription event
            if (
                message.get("event") == "subscribe"
                and message.get("channel") == "rates"
            ):
                vs_currency = message.get("vs_currency", "cad")
                print("Subscription made, now fetching new data...")
                # Fetch and send data
                await send_fresh_data(vs_currency)

    except WebSocketDisconnect:
        print("Client disconnected")


# HTML page when accessing the root URL
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
        # ssl_keyfile=".certifications/cert.pem",
        # ssl_certfile=".certifications/cert.pem",
    )
