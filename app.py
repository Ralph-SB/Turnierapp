import streamlit as st
import json
import os
from datetime import datetime
from logic import TournamentEngine
from ui_components import render_bracket, render_standings, render_match_card

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Squash Club Championship",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0e1a !important;
    color: #e8eaf6 !important;
  }

  .main { background-color: #0a0e1a; }
  .block-container { padding-top: 1.5rem !important; max-width: 1400px; }

  /* ── Header ── */
  .app-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1225 50%, #1a1f35 100%);
    border: 1px solid #2a3f6f;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,120,255,0.15);
  }
  .app-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4fc3f7, #29b6f6, #0288d1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: 2px;
  }
  .app-subtitle {
    color: #7986cb;
    font-size: 0.95rem;
    margin-top: 4px;
    letter-spacing: 3px;
    text-transform: uppercase;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e2d4f;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #7986cb;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 8px 20px;
    border: none;
  }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    color: #fff !important;
  }

  /* ── Cards ── */
  .card {
    background: #111827;
    border: 1px solid #1e2d4f;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  }
  .card-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #4fc3f7;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid #1e2d4f;
    padding-bottom: 0.5rem;
  }

  /* ── Match cards ── */
  .match-container {
    background: #0d1225;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    transition: border-color 0.2s;
  }
  .match-container:hover { border-color: #2196f3; }
  .match-round-label {
    font-family: 'Rajdhani', sans-serif;
    color: #7986cb;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.3rem;
  }
  .player-name {
    font-weight: 600;
    font-size: 1rem;
    color: #e8eaf6;
  }
  .player-name.winner { color: #4caf50; }
  .player-seed {
    color: #546e7a;
    font-size: 0.8rem;
    font-weight: 400;
  }
  .score-badge {
    background: #1e3a5f;
    border-radius: 6px;
    padding: 2px 8px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #4fc3f7;
    min-width: 30px;
    text-align: center;
  }
  .score-badge.winner-score { background: #1b5e20; color: #81c784; }
  .score-badge.loser-score  { background: #1a1f35; color: #546e7a; }

  /* ── Bracket ── */
  .bracket-round-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #29b6f6;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2px;
    background: #111827;
    border: 1px solid #1e2d4f;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    margin-bottom: 0.5rem;
  }
  .bracket-section-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 1rem 0 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
  }
  .bracket-winners { color: #ffd54f; background: rgba(255,213,79,0.08); border-left: 3px solid #ffd54f; }
  .bracket-losers  { color: #ef9a9a; background: rgba(239,154,154,0.06); border-left: 3px solid #ef9a9a; }

  /* ── Standings table ── */
  .standings-table { width: 100%; border-collapse: collapse; }
  .standings-table th {
    background: #1565c0;
    color: #fff;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 12px;
    text-align: left;
  }
  .standings-table td {
    padding: 8px 12px;
    border-bottom: 1px solid #1e2d4f;
    font-size: 0.9rem;
  }
  .standings-table tr:nth-child(even) td { background: #111827; }
  .standings-table tr:nth-child(odd)  td { background: #0d1225; }
  .standings-table tr:hover td { background: #1a2744; }
  .rank-gold   { color: #ffd700; font-weight: 700; }
  .rank-silver { color: #c0c0c0; font-weight: 700; }
  .rank-bronze { color: #cd7f32; font-weight: 700; }
  .rank-normal { color: #7986cb; }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0);
    box-shadow: 0 4px 12px rgba(21,101,192,0.4);
    transform: translateY(-1px);
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20);
  }

  /* ── Inputs ── */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    color: #e8eaf6 !important;
    border-radius: 8px !important;
  }

  /* ── Status badges ── */
  .status-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .status-pending   { background: #1a2744; color: #7986cb; border: 1px solid #1e3a5f; }
  .status-live      { background: rgba(255,193,7,0.15); color: #ffc107; border: 1px solid #ffc107; animation: pulse 2s infinite; }
  .status-completed { background: rgba(76,175,80,0.15); color: #4caf50; border: 1px solid #4caf50; }

  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }

  /* ── Section divider ── */
  .section-divider {
    border: none;
    border-top: 1px solid #1e2d4f;
    margin: 1.5rem 0;
  }

  /* ── Warning box ── */
  .stAlert { border-radius: 10px !important; }

  /* ── Info metric ── */
  .metric-box {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
  }
  .metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #4fc3f7;
  }
  .metric-label {
    font-size: 0.75rem;
    color: #546e7a;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  
  /* hide streamlit branding */
  #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── State helpers ─────────────────────────────────────────────────────────────
DATA_FILE = "tournament_data.json"

def load_state():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_state(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if "tournament" not in st.session_state:
    st.session_state.tournament = load_state()
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "admin_pw_ok" not in st.session_state:
    st.session_state.admin_pw_ok = False

ADMIN_PASSWORD = "squash2024"   # ← change here

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">🎯 SQUASH CLUB CHAMPIONSHIP</div>
  <div class="app-subtitle">Monrad System · 16 Players · Best of 5 Sets</div>
</div>
""", unsafe_allow_html=True)

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_live, tab_bracket, tab_admin = st.tabs([
    "📊 Live Standings", "🏆 Tournament Bracket", "⚙️ Admin"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – LIVE STANDINGS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_live:
    t = st.session_state.tournament
    if not t:
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem;">
          <div style="font-size:3rem;">🎯</div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;color:#4fc3f7;margin-top:0.5rem;">
            Tournament not started yet
          </div>
          <div style="color:#546e7a;margin-top:0.5rem;">
            Go to the Admin tab to set up the tournament.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        engine = TournamentEngine(t)
        
        # ── Metrics row
        total_matches = sum(len(r) for r in t.get("rounds", {}).values())
        played = sum(
            1 for r in t.get("rounds", {}).values()
            for m in r if m.get("winner")
        )
        players_done = engine.count_finished_players()
        
        c1, c2, c3, c4 = st.columns(4)
        for col, val, label in zip(
            [c1, c2, c3, c4],
            [16, total_matches, played, players_done],
            ["Players", "Total Matches", "Matches Played", "Players Placed"]
        ):
            col.markdown(f"""
            <div class="metric-box">
              <div class="metric-value">{val}</div>
              <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        
        # ── Current matches (pending)
        pending = engine.get_pending_matches()
        if pending:
            st.markdown('<div class="card-header">⚡ Current Matches</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(pending), 3))
            for i, m in enumerate(pending[:6]):
                with cols[i % 3]:
                    render_match_card(m, players=t["players"], show_score=True)
        
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        
        # ── Standings
        st.markdown('<div class="card-header">🏅 Current Standings</div>', unsafe_allow_html=True)
        render_standings(engine.compute_standings(), t["players"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – BRACKET
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bracket:
    t = st.session_state.tournament
    if not t:
        st.info("Start the tournament in the Admin tab first.")
    else:
        engine = TournamentEngine(t)
        
        # ── Edit mode toggle
        col_a, col_b = st.columns([3, 1])
        with col_b:
            if not st.session_state.edit_mode:
                with st.expander("🔐 Edit Mode"):
                    pw = st.text_input("Password", type="password", key="edit_pw")
                    if st.button("Unlock"):
                        if pw == ADMIN_PASSWORD:
                            st.session_state.edit_mode = True
                            st.rerun()
                        else:
                            st.error("Wrong password")
            else:
                st.markdown('<div class="status-badge status-live">✏️ Edit Mode ON</div>', unsafe_allow_html=True)
                if st.button("🔒 Lock"):
                    st.session_state.edit_mode = False
                    st.rerun()
        
        render_bracket(t, engine, st.session_state.edit_mode, save_state)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
with tab_admin:
    # Password gate
    if not st.session_state.admin_pw_ok:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🔐 Admin Login</div>', unsafe_allow_html=True)
        pw_input = st.text_input("Enter admin password", type="password", key="admin_pw")
        if st.button("Login"):
            if pw_input == ADMIN_PASSWORD:
                st.session_state.admin_pw_ok = True
                st.rerun()
            else:
                st.error("Wrong password!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card-header">⚙️ Tournament Setup</div>', unsafe_allow_html=True)

        t = st.session_state.tournament
        
        if not t:
            st.markdown("### Enter 16 Players (seeded #1 = strongest)")
            
            default_names = [
                "Max Müller", "Anna Schmidt", "Tom Weber", "Lisa Fischer",
                "Jan Bauer", "Sara Meyer", "Felix Wagner", "Julia Schulz",
                "Lukas Hoffmann", "Marie Koch", "Nico Richter", "Lena Klein",
                "Paul Wolf", "Mia Schröder", "Leon Neumann", "Lea Braun"
            ]
            
            players = []
            cols = st.columns(2)
            for i in range(16):
                with cols[i % 2]:
                    name = st.text_input(
                        f"#{i+1} Seed",
                        value=default_names[i],
                        key=f"player_{i}"
                    )
                    players.append(name.strip())
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Start Tournament", type="primary"):
                if all(players) and len(set(players)) == 16:
                    engine = TournamentEngine({})
                    new_t = engine.initialize(players)
                    st.session_state.tournament = new_t
                    save_state(new_t)
                    st.success("✅ Tournament started!")
                    st.rerun()
                else:
                    st.error("Please enter 16 unique player names.")
        else:
            st.success("✅ Tournament is running!")
            
            engine = TournamentEngine(t)
            st.markdown("### Advance Rounds")
            st.markdown("After all matches in the current round are played, click to generate next round:")
            
            current_round = engine.get_current_round()
            st.info(f"Current round: **Round {current_round}**")
            
            if engine.can_advance():
                if st.button("⏭️ Generate Next Round"):
                    engine.advance_round()
                    st.session_state.tournament = engine.data
                    save_state(engine.data)
                    st.success("Next round generated!")
                    st.rerun()
            else:
                st.warning("Complete all matches in current round first.")
            
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            
            # Change admin password
            with st.expander("🔑 Change Admin Password"):
                st.info(f"Current password: `{ADMIN_PASSWORD}` (change in app.py line 8)")
            
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            
            # Reset
            with st.expander("⚠️ Danger Zone"):
                st.warning("This will permanently delete all tournament data!")
                confirm = st.text_input("Type 'RESET' to confirm")
                if st.button("🗑️ Reset Tournament"):
                    if confirm == "RESET":
                        st.session_state.tournament = {}
                        if os.path.exists(DATA_FILE):
                            os.remove(DATA_FILE)
                        st.success("Tournament reset.")
                        st.rerun()
                    else:
                        st.error("Type 'RESET' to confirm.")
        
        if st.button("🔓 Logout"):
            st.session_state.admin_pw_ok = False
            st.rerun()
