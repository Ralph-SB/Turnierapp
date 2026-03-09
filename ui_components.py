"""
UI components for the Squash Championship app.
"""

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def player_label(seed: str, players: dict, size: str = "normal") -> str:
    if seed in ("TBD", "BYE", "BYE2", None):
        return f'<span style="color:#546e7a;font-style:italic;">{seed or "TBD"}</span>'
    name = players.get(seed, f"Seed {seed}")
    if size == "small":
        return (f'<span style="color:#e8eaf6;font-weight:600;">{name}</span>'
                f'<span style="color:#546e7a;font-size:0.75rem;margin-left:4px;">#{seed}</span>')
    return (f'<span style="font-weight:700;color:#e8eaf6;">{name}</span>'
            f'<span style="color:#546e7a;font-size:0.8rem;margin-left:6px;">#{seed}</span>')


def bracket_color(bracket: str) -> str:
    return {"winners": "#ffd54f", "losers": "#ef9a9a",
            "final": "#80deea", "consolation": "#a5d6a7"}.get(bracket, "#7986cb")


# ─────────────────────────────────────────────────────────────────────────────
# Match card (read-only)
# ─────────────────────────────────────────────────────────────────────────────

def render_match_card(match: dict, players: dict = None, show_score: bool = True):
    if players is None:
        players = {}
    p1, p2 = match["p1"], match["p2"]
    w = match.get("winner")
    color = bracket_color(match.get("bracket", ""))

    def set_score_html(sets_p, sets_q, is_winner):
        if not sets_p:
            return ""
        parts = []
        for a, b in zip(sets_p, sets_q):
            cls = "winner-score" if a > b else "loser-score"
            parts.append(f'<span class="score-badge {cls}">{a}</span>')
        return " ".join(parts)

    p1_win = w == p1
    p2_win = w == p2

    p1_name = players.get(p1, p1) if p1 not in ("TBD","BYE","BYE2") else p1
    p2_name = players.get(p2, p2) if p2 not in ("TBD","BYE","BYE2") else p2

    score_p1 = set_score_html(match.get("sets_p1",[]), match.get("sets_p2",[]), p1_win)
    score_p2 = set_score_html(match.get("sets_p2",[]), match.get("sets_p1",[]), p2_win)

    sw1 = match.get("sets_won_p1", 0)
    sw2 = match.get("sets_won_p2", 0)

    status_html = ""
    if w:
        status_html = '<span class="status-badge status-completed">Done</span>'
    elif p1 not in ("TBD", None) and p2 not in ("TBD", "BYE", None):
        status_html = '<span class="status-badge status-live">Live</span>'
    else:
        status_html = '<span class="status-badge status-pending">Pending</span>'

    st.markdown(f"""
    <div class="match-container">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="color:{color};font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;">{match.get('label','')}</span>
        {status_html}
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin:4px 0;">
        <span class="player-name {'winner' if p1_win else ''}">{p1_name}
          <span style="color:#546e7a;font-size:0.75rem;">#{p1 if p1 not in ('TBD','BYE','BYE2') else ''}</span>
        </span>
        <div style="display:flex;align-items:center;gap:4px;">
          <span style="color:{'#4caf50' if p1_win else '#7986cb'};font-family:'Rajdhani',sans-serif;font-size:1.2rem;font-weight:700;min-width:24px;text-align:right;">{sw1 if w else ''}</span>
          {score_p1}
        </div>
      </div>
      <div style="border-top:1px solid #1e2d4f;margin:4px 0;"></div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin:4px 0;">
        <span class="player-name {'winner' if p2_win else ''}">{p2_name}
          <span style="color:#546e7a;font-size:0.75rem;">#{p2 if p2 not in ('TBD','BYE','BYE2') else ''}</span>
        </span>
        <div style="display:flex;align-items:center;gap:4px;">
          <span style="color:{'#4caf50' if p2_win else '#7986cb'};font-family:'Rajdhani',sans-serif;font-size:1.2rem;font-weight:700;min-width:24px;text-align:right;">{sw2 if w else ''}</span>
          {score_p2}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Score entry form
# ─────────────────────────────────────────────────────────────────────────────

def render_score_entry(match: dict, players: dict, engine, save_fn):
    """Compact score entry widget."""
    p1 = match["p1"]
    p2 = match["p2"]
    if p2 in ("BYE", "BYE2"):
        return
    if p1 in ("TBD", None) or p2 in ("TBD", None):
        st.caption("⏳ Waiting for previous round")
        return

    p1_name = players.get(p1, p1)
    p2_name = players.get(p2, p2)

    with st.form(key=f"form_{match['id']}"):
        st.markdown(f"**{p1_name} (#{p1})  vs  {p2_name} (#{p2})**")
        st.caption("Enter scores for each set played (best of 5 – first to win 3 sets)")

        sets_p1 = []
        sets_p2 = []
        cols = st.columns(5)
        num_sets = 0
        for s in range(5):
            with cols[s]:
                st.markdown(f"<div style='text-align:center;color:#7986cb;font-size:0.8rem;'>Set {s+1}</div>",
                            unsafe_allow_html=True)
                a = st.number_input("", min_value=0, max_value=30,
                                    value=0, key=f"{match['id']}_s{s}_p1", label_visibility="collapsed")
                b = st.number_input("", min_value=0, max_value=30,
                                    value=0, key=f"{match['id']}_s{s}_p2", label_visibility="collapsed")
                if a > 0 or b > 0:
                    sets_p1.append(a)
                    sets_p2.append(b)
                    num_sets = s + 1

        submitted = st.form_submit_button("💾 Save Result")
        if submitted:
            if len(sets_p1) < 1:
                st.error("Enter at least 1 set score.")
            else:
                # Validate: best of 5, first to 3
                w1 = sum(1 for a, b in zip(sets_p1, sets_p2) if a > b)
                w2 = sum(1 for a, b in zip(sets_p1, sets_p2) if b > a)
                if w1 < 3 and w2 < 3:
                    st.warning("No winner yet – make sure one player reaches 3 set wins.")
                engine.record_result(match["round"], match["id"], sets_p1, sets_p2)
                save_fn(engine.data)
                st.session_state.tournament = engine.data
                st.success("✅ Result saved!")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Bracket display
# ─────────────────────────────────────────────────────────────────────────────

def render_bracket(t: dict, engine, edit_mode: bool, save_fn):
    players = t.get("players", {})
    rounds  = t.get("rounds", {})

    section_configs = [
        ("R1", "🎯 Round 1 – First Round", None),
        ("R2", "🔵 Round 2", None),
        ("R3", "🔶 Round 3 – Semi Finals", None),
        ("R4", "🏆 Round 4 – Finals", None),
    ]

    for rk, title, _ in section_configs:
        if rk not in rounds:
            continue

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111827,#0d1225);
                    border:1px solid #1e3a5f;border-radius:12px;
                    padding:0.8rem 1.2rem;margin:1rem 0 0.5rem;">
          <span style="font-family:'Rajdhani',sans-serif;font-size:1.3rem;
                       font-weight:700;color:#4fc3f7;text-transform:uppercase;
                       letter-spacing:2px;">{title}</span>
        </div>
        """, unsafe_allow_html=True)

        matches = rounds[rk]

        # Group by bracket type
        groups = {}
        for m in matches:
            b = m.get("bracket", "other")
            groups.setdefault(b, []).append(m)

        bracket_order = ["final", "winners", "losers", "consolation"]
        bracket_labels = {
            "final": "🏆 Finals",
            "winners": "🥇 Winners Bracket",
            "losers": "🥈 Losers Bracket",
            "consolation": "🎯 Consolation",
        }

        for btype in bracket_order:
            if btype not in groups:
                continue
            bmatches = groups[btype]
            color = bracket_color(btype)

            st.markdown(f"""
            <div style="color:{color};font-family:'Rajdhani',sans-serif;
                        font-size:0.9rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:2px;margin:0.5rem 0 0.3rem;
                        padding-left:0.5rem;border-left:3px solid {color};">
              {bracket_labels.get(btype, btype)}
            </div>
            """, unsafe_allow_html=True)

            num_cols = min(len(bmatches), 4)
            cols = st.columns(num_cols)

            for i, match in enumerate(bmatches):
                with cols[i % num_cols]:
                    render_match_card(match, players, show_score=True)
                    if edit_mode and not match.get("winner"):
                        with st.expander("✏️ Enter Score"):
                            render_score_entry(match, players, engine, save_fn)
                    elif edit_mode and match.get("winner"):
                        with st.expander("🔄 Correct Score"):
                            st.caption("Override existing result:")
                            render_score_entry(match, players, engine, save_fn)


# ─────────────────────────────────────────────────────────────────────────────
# Standings table
# ─────────────────────────────────────────────────────────────────────────────

def render_standings(rows: list, players: dict):
    if not rows:
        st.info("No results yet.")
        return

    rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}

    # Build one big HTML string with inline styles (no CSS classes needed)
    html_rows = ""
    for i, r in enumerate(rows):
        rank  = r.get("display_rank", i + 1)
        icon  = rank_icons.get(rank, "")
        seed  = r["seed"]
        name  = players.get(seed, r.get("name", seed))

        if rank == 1:
            rank_color = "#ffd700"
        elif rank == 2:
            rank_color = "#c0c0c0"
        elif rank == 3:
            rank_color = "#cd7f32"
        else:
            rank_color = "#7986cb"

        row_bg = "#111827" if i % 2 == 0 else "#0d1225"

        html_rows += (
            f'<tr style="background:{row_bg};">'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;">'
            f'  <span style="color:{rank_color};font-weight:700;">{icon} {rank}</span>'
            f'</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'           font-weight:600;color:#e8eaf6;">{name}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;color:#546e7a;">#{seed}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;color:#7986cb;text-align:center;">{r["matches"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;color:#4caf50;font-weight:700;text-align:center;">{r["wins"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;color:#ef5350;text-align:center;">{r["losses"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;color:#4fc3f7;text-align:center;">{r["sets_won"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;color:#78909c;text-align:center;">{r["sets_lost"]}</td>'
            f'</tr>'
        )

    th_style = (
        'style="background:#1565c0;color:#fff;padding:10px 12px;'
        'text-align:left;font-size:0.82rem;text-transform:uppercase;'
        'letter-spacing:1px;font-weight:600;"'
    )

    html = (
        '<div style="overflow-x:auto;">'
        '<table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;font-size:0.9rem;">'
        '<thead><tr>'
        f'<th {th_style}>#</th>'
        f'<th {th_style}>Player</th>'
        f'<th {th_style}>Seed</th>'
        f'<th {th_style} style="text-align:center;">Matches</th>'
        f'<th {th_style} style="text-align:center;">W</th>'
        f'<th {th_style} style="text-align:center;">L</th>'
        f'<th {th_style} style="text-align:center;">Sets W</th>'
        f'<th {th_style} style="text-align:center;">Sets L</th>'
        '</tr></thead>'
        f'<tbody>{html_rows}</tbody>'
        '</table></div>'
    )

    st.markdown(html, unsafe_allow_html=True)
