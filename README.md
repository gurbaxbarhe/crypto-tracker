# crypto_tracker
A cryptocurrency tracking application that provides updates on prices, popularity, and news

Documentation
Link to API: [https://docs.coingecko.com/reference/coins-markets]

Activate VM
```bash
cd backend/
source venv/Scripts/activate
```

Install backend requirements
```bash
cd backend/
pip install -r requirements.txt
```

Run app
```bash
cd backend/src/
fastapi dev app.py
```
Link to application, upon hosting: [http://127.0.0.1:8000/]

Reload app
```bash
cd backend/src/
uvicorn app:app --reload
```


# Next Steps
Going to continue to do the following for my learning:

1) This is not a WSS connection as stated in the requirements, it is a WS. This is P1 and critical to-do as crypto data must be delivered safely.

2) Currently, the data is fetched whenever the "Subscribe" button is clicked on the UI. This should only change when there is a change in the data, aka an async function named "check_api()" that checks if there are any changes. If there are it merges these  

3) Implement React instead of JS. It is easier to work with components like tables to nicely display data and pass paramaters as props such as switching from USD to CAD, etc.
