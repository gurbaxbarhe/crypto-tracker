# Crypto Tracker
A cryptocurrency tracking application that provides updates on prices, popularity, and news

<h3 align="left">Documentation</h3>
Link to API: [https://docs.coingecko.com/reference/coins-markets]

&nbsp;

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


Reload app
```bash
cd backend/src/
uvicorn app:app --reload
```
