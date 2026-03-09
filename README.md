# 🎯 Squash Club Championship

**Monrad System · 16 Players · Best-of-5 Sets**

A full-featured tournament management app built with Python + Streamlit.

---

## Features

- **Monrad Bracket**: 16 players, 4 rounds, every player guaranteed 4 matches
- **Live Bracket View**: Public URL for all club members
- **Score Entry**: Password-protected edit mode (default: `squash2024`)
- **Live Standings**: Real-time rankings after every result
- **Dark Squash Theme**: Mobile-responsive, sportliche UI

---

## Local Setup

```bash
pip install streamlit
streamlit run app.py
```

---

## 🚀 Deployment on Streamlit Community Cloud (Free)

### Step 1 – Push to GitHub
1. Create a new **public** repository on [github.com](https://github.com)
2. Upload all files:
   - `app.py`
   - `logic.py`
   - `ui_components.py`
   - `requirements.txt`
3. Push to `main` branch

### Step 2 – Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository and branch (`main`)
5. Set **Main file path** to `app.py`
6. Click **"Deploy!"**

### Step 3 – Share the URL
After ~60 seconds, your app is live at:
```
https://<your-app-name>.streamlit.app
```
Share this URL with all club members – they can view the bracket live!

---

## Admin Password

The default password is `squash2024`.

To change it, edit line 8 in `app.py`:
```python
ADMIN_PASSWORD = "your_new_password"
```

---

## Tournament Flow

| Round | Winners Bracket | Losers Bracket | Consolation |
|-------|----------------|----------------|-------------|
| R1    | 8 matches (seeds 1v16, 2v15, ...) | – | – |
| R2    | 4 matches (WB winners) | 4 matches (R1 losers) | – |
| R3    | 2 semi-finals | 4 matches (WB losers + LB winners) | 4 matches (LB losers) |
| R4    | Final (1st/2nd) + 3rd place | 5th–8th place | 9th–16th place |

Every player is guaranteed exactly **4 matches**.

---

## Data Persistence

Tournament data is saved locally to `tournament_data.json`.  
On Streamlit Cloud this persists within the same session — for a club event this is perfect since the app runs continuously during the tournament day.
