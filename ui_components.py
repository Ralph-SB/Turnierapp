"""
UI components for the Squash Championship app.
"""

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def bracket_color(bracket: str) -> str:
    return {"winners": "#ffd54f", "losers": "#ef9a9a",
            "final": "#80deea", "consolation": "#a5d6a7"}.get(bracket, "#7986cb")


def court_badge(court, time):
    if court is None or time is None:
        return ""
    color = "#1e88e5" if court == 1 else "#7b1fa2"
    label = f"Court {court}"
    return (
        f'<span style="background:{color};color:#fff;border-radius:5px;'
        f'padding:2px 8px;font-size:0.72rem;font-weight:700;'
        f'letter-spacing:0.5px;margin-right:4px;">{label}</span>'
        f'<span style="color:#90caf9;font-size:0.78rem;font-weight:600;">'
        f'⏰ {time}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Match card (read-only)
# ─────────────────────────────────────────────────────────────────────────────

def render_match_card(match: dict, players: dict = None, show_score: bool = True):
    if players is None:
        players = {}

    # BYE-Freilos → kompakte Darstellung
    if match.get("is_bye"):
        p1 = match.get("p1", "")
        name = players.get(p1, p1) if p1 not in ("BYE", "TBD", None) else "–"
        st.markdown(
            f'<div class="match-container" style="opacity:0.55;">'
            f'<div style="color:#546e7a;font-size:0.72rem;text-transform:uppercase;'
            f'letter-spacing:1px;margin-bottom:4px;">{match.get("label","")}</div>'
            f'<div style="color:#81c784;font-weight:700;">🎯 Freilos</div>'
            f'<div style="color:#e8eaf6;font-size:0.9rem;">{name}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        return

    p1, p2 = match["p1"], match["p2"]
    w = match.get("winner")
    color = bracket_color(match.get("bracket", ""))

    p1_name = players.get(p1, p1) if p1 not in ("TBD", "BYE", None) else (p1 or "TBD")
    p2_name = players.get(p2, p2) if p2 not in ("TBD", "BYE", None) else (p2 or "TBD")
    p1_win = w == p1
    p2_win = w == p2

    sw1 = match.get("sets_won_p1", 0)
    sw2 = match.get("sets_won_p2", 0)

    # Set scores
    def set_chips(scores_a, scores_b):
        if not scores_a:
            return ""
        parts = []
        for a, b in zip(scores_a, scores_b):
            cls_bg  = "#1b5e20" if a > b else "#1a1f35"
            cls_col = "#81c784" if a > b else "#546e7a"
            parts.append(
                f'<span style="background:{cls_bg};color:{cls_col};'
                f'border-radius:4px;padding:1px 6px;font-size:0.8rem;'
                f'font-weight:700;font-family:monospace;">{a}</span>'
            )
        return " ".join(parts)

    chips_p1 = set_chips(match.get("sets_p1",[]), match.get("sets_p2",[]))
    chips_p2 = set_chips(match.get("sets_p2",[]), match.get("sets_p1",[]))

    if w:
        status = '<span class="status-badge status-completed">Fertig</span>'
    elif p1 not in ("TBD", None) and p2 not in ("TBD", "BYE", None):
        status = '<span class="status-badge status-live">Läuft</span>'
    else:
        status = '<span class="status-badge status-pending">Ausstehend</span>'

    badge = court_badge(match.get("court"), match.get("time"))

    def row(name, seed, is_w, sw, chips):
        seed_str = f"#{seed}" if seed not in ("TBD","BYE",None) else ""
        name_col = "#4caf50" if is_w else "#e8eaf6"
        sw_col   = "#4caf50" if is_w else "#7986cb"
        sw_str   = str(sw) if w else ""
        return (
            f'<div style="display:flex;align-items:center;'
            f'justify-content:space-between;padding:5px 0;">'
            f'<span style="color:{name_col};font-weight:{"700" if is_w else "500"};'
            f'font-size:0.92rem;">{name} '
            f'<span style="color:#546e7a;font-size:0.75rem;">{seed_str}</span></span>'
            f'<div style="display:flex;align-items:center;gap:5px;">'
            f'{chips}'
            f'<span style="color:{sw_col};font-family:Rajdhani,sans-serif;'
            f'font-size:1.15rem;font-weight:700;min-width:18px;text-align:right;">'
            f'{sw_str}</span>'
            f'</div></div>'
        )

    html = (
        f'<div class="match-container">'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:center;margin-bottom:5px;">'
        f'<div>{badge}</div>'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<span style="color:{color};font-size:0.72rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:1px;">'
        f'{match.get("label","")}</span>'
        f'{status}</div></div>'
        f'<div style="border-top:1px solid #1e2d4f;padding-top:5px;">'
        f'{row(p1_name, p1, p1_win, sw1, chips_p1)}'
        f'<div style="border-top:1px dashed #1e2d4f;margin:2px 0;"></div>'
        f'{row(p2_name, p2, p2_win, sw2, chips_p2)}'
        f'</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Score entry form
# ─────────────────────────────────────────────────────────────────────────────

def render_score_entry(match: dict, players: dict, engine, save_fn):
    p1, p2 = match["p1"], match["p2"]
    if match.get("is_bye") or p2 == "BYE":
        return
    if not (p1 not in ("TBD", None) and p2 not in ("TBD", None)):
        st.caption("⏳ Warte auf vorherige Runde")
        return

    p1_name = players.get(p1, p1)
    p2_name = players.get(p2, p2)

    with st.form(key=f"form_{match['id']}"):
        st.markdown(
            f"**{p1_name} (#{p1})** &nbsp;vs&nbsp; **{p2_name} (#{p2})**",
            unsafe_allow_html=True
        )
        st.caption("Satzergebnisse eintragen (Best of 5 – wer zuerst 3 Sätze gewinnt)")
        cols = st.columns(5)
        sets_p1, sets_p2 = [], []
        for s in range(5):
            with cols[s]:
                st.markdown(
                    f"<div style='text-align:center;color:#7986cb;"
                    f"font-size:0.78rem;margin-bottom:2px;'>Satz {s+1}</div>",
                    unsafe_allow_html=True
                )
                a = st.number_input("", min_value=0, max_value=30, value=0,
                                    key=f"{match['id']}_s{s}_p1",
                                    label_visibility="collapsed")
                b = st.number_input("", min_value=0, max_value=30, value=0,
                                    key=f"{match['id']}_s{s}_p2",
                                    label_visibility="collapsed")
                if a > 0 or b > 0:
                    sets_p1.append(a)
                    sets_p2.append(b)

        submitted = st.form_submit_button("💾 Ergebnis speichern")
        if submitted:
            if not sets_p1:
                st.error("Mindestens einen Satz eintragen.")
            else:
                w1 = sum(1 for a, b in zip(sets_p1, sets_p2) if a > b)
                w2 = sum(1 for a, b in zip(sets_p1, sets_p2) if b > a)
                if w1 < 3 and w2 < 3:
                    st.warning("Noch kein Gewinner – ein Spieler muss 3 Sätze gewonnen haben.")
                else:
                    engine.record_result(match["round"], match["id"], sets_p1, sets_p2)
                    save_fn(engine.data)
                    st.session_state.tournament = engine.data
                    st.success("✅ Ergebnis gespeichert!")
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Bracket display
# ─────────────────────────────────────────────────────────────────────────────

def render_bracket(t: dict, engine, edit_mode: bool, save_fn):
    players = t.get("players", {})
    rounds  = t.get("rounds", {})

    round_titles = {
        "R1": "🎯 Runde 1 – Erstrunden",
        "R2": "🔵 Runde 2",
        "R3": "🔶 Runde 3 – Halbfinale",
        "R4": "🏆 Runde 4 – Finale & Platzierungen",
    }
    bracket_order  = ["final", "winners", "losers", "consolation"]
    bracket_labels = {
        "final":       "🏆 Finale",
        "winners":     "🥇 Winners Bracket",
        "losers":      "🥈 Losers Bracket",
        "consolation": "🎯 Trostrunde",
    }

    for rk, title in round_titles.items():
        if rk not in rounds:
            continue

        st.markdown(
            f'<div style="background:linear-gradient(135deg,#111827,#0d1225);'
            f'border:1px solid #1e3a5f;border-radius:12px;'
            f'padding:0.8rem 1.2rem;margin:1rem 0 0.5rem;">'
            f'<span style="font-family:Rajdhani,sans-serif;font-size:1.3rem;'
            f'font-weight:700;color:#4fc3f7;text-transform:uppercase;'
            f'letter-spacing:2px;">{title}</span>'
            f'<span style="color:#546e7a;font-size:0.8rem;margin-left:12px;">'
            f'Start: {_round_time(rk)}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        matches = rounds[rk]
        groups = {}
        for m in matches:
            groups.setdefault(m.get("bracket","other"), []).append(m)

        for btype in bracket_order:
            if btype not in groups:
                continue
            bmatches = groups[btype]
            color = bracket_color(btype)

            st.markdown(
                f'<div style="color:{color};font-family:Rajdhani,sans-serif;'
                f'font-size:0.88rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:2px;margin:0.5rem 0 0.3rem;'
                f'padding-left:0.5rem;border-left:3px solid {color};">'
                f'{bracket_labels.get(btype, btype)}</div>',
                unsafe_allow_html=True
            )

            # Filtere echte Matches (nicht beides BYE)
            visible = [m for m in bmatches
                       if not (m.get("p1") == "BYE" and m.get("p2") == "BYE")]
            if not visible:
                continue

            num_cols = min(len(visible), 4)
            cols = st.columns(num_cols)
            for i, match in enumerate(visible):
                with cols[i % num_cols]:
                    render_match_card(match, players, show_score=True)
                    if edit_mode and not match.get("is_bye"):
                        if not match.get("winner"):
                            with st.expander("✏️ Ergebnis eintragen"):
                                render_score_entry(match, players, engine, save_fn)
                        else:
                            with st.expander("🔄 Ergebnis korrigieren"):
                                render_score_entry(match, players, engine, save_fn)


def _round_time(rk: str) -> str:
    from logic import ROUND_START
    return ROUND_START.get(rk, "")


# ─────────────────────────────────────────────────────────────────────────────
# Schedule view
# ─────────────────────────────────────────────────────────────────────────────

def render_schedule(t: dict, engine):
    """Tagesplan-Ansicht sortiert nach Zeit und Court."""
    players = t.get("players", {})
    matches = engine.get_schedule()

    if not matches:
        st.info("Noch keine Spiele geplant.")
        return

    # Gruppiere nach Zeitblock (Runde)
    from logic import ROUND_START
    round_names = {
        "R1": "Runde 1 · 10:00 – 11:45",
        "R2": "Runde 2 · 12:00 – 13:45",
        "R3": "Runde 3 · 14:00 – 15:45",
        "R4": "Runde 4 · 16:00 – 17:30",
    }

    current_round = None
    for m in matches:
        rk = m.get("round")
        if rk != current_round:
            current_round = rk
            st.markdown(
                f'<div style="background:linear-gradient(90deg,#1565c0,#0d47a1);'
                f'border-radius:8px;padding:6px 14px;margin:12px 0 6px;">'
                f'<span style="font-family:Rajdhani,sans-serif;font-weight:700;'
                f'color:#fff;font-size:1rem;text-transform:uppercase;letter-spacing:2px;">'
                f'{round_names.get(rk, rk)}</span></div>',
                unsafe_allow_html=True
            )

        p1 = m.get("p1","")
        p2 = m.get("p2","")
        p1_name = players.get(p1, p1) if p1 not in ("TBD","BYE",None) else "?"
        p2_name = players.get(p2, p2) if p2 not in ("TBD","BYE",None) else "?"
        w = m.get("winner")
        court = m.get("court")
        time_str = m.get("time","")

        court_col = "#1e88e5" if court == 1 else "#7b1fa2"

        # Ergebnis aufbauen
        if w and w not in ("BYE",):
            winner_name = players.get(w, w)
            sw1 = m.get("sets_won_p1", 0)
            sw2 = m.get("sets_won_p2", 0)
            sets_p1 = m.get("sets_p1", [])
            sets_p2 = m.get("sets_p2", [])

            # Satz-Chips
            chips = ""
            for a, b in zip(sets_p1, sets_p2):
                bg = "#1b5e20" if a > b else "#1a1f35"
                col = "#81c784" if a > b else "#546e7a"
                chips += (f'<span style="background:{bg};color:{col};border-radius:3px;'
                          f'padding:1px 5px;font-size:0.75rem;font-weight:700;'
                          f'font-family:monospace;">{a}:{b}</span> ')

            # Satzstand
            sets_str = f'<span style="color:#4caf50;font-weight:700;">{sw1}</span>' \
                       f'<span style="color:#546e7a;">:</span>' \
                       f'<span style="color:#ef5350;font-weight:700;">{sw2}</span>'

            result_html = (
                f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:2px;">'
                f'<div style="display:flex;align-items:center;gap:5px;">'
                f'<span style="font-size:0.75rem;color:#4caf50;">✅</span>'
                f'<span style="color:#4caf50;font-weight:700;font-size:0.85rem;">{winner_name}</span>'
                f'<span style="color:#7986cb;font-size:0.8rem;margin-left:3px;">{sets_str} Sätze</span>'
                f'</div>'
                f'<div style="display:flex;gap:3px;">{chips}</div>'
                f'</div>'
            )
        else:
            result_html = '<span style="color:#546e7a;font-size:0.8rem;">⏳ Ausstehend</span>'

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;'
            f'background:#111827;border:1px solid #1e2d4f;border-radius:8px;'
            f'padding:9px 12px;margin:3px 0;">'
            f'<span style="background:{court_col};color:#fff;border-radius:5px;'
            f'padding:3px 9px;font-size:0.78rem;font-weight:700;min-width:72px;'
            f'text-align:center;">Court {court}</span>'
            f'<span style="color:#90caf9;font-weight:700;font-size:0.9rem;'
            f'min-width:48px;">{time_str}</span>'
            f'<span style="color:#e8eaf6;font-size:0.9rem;flex:1;">'
            f'<b>{p1_name}</b> <span style="color:#546e7a;font-size:0.75rem;">#{p1}</span>'
            f' <span style="color:#546e7a;">vs</span> '
            f'<b>{p2_name}</b> <span style="color:#546e7a;font-size:0.75rem;">#{p2}</span></span>'
            f'<span style="color:#ffd54f;font-size:0.75rem;font-weight:600;'
            f'min-width:80px;text-align:right;">{m.get("label","")}</span>'
            f'<div style="min-width:200px;text-align:right;">{result_html}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# Standings table
# ─────────────────────────────────────────────────────────────────────────────

def render_standings(rows: list, players: dict):
    if not rows:
        st.info("Noch keine Ergebnisse.")
        return

    rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}
    th = ('style="background:#1565c0;color:#fff;padding:10px 12px;'
          'text-align:left;font-size:0.82rem;text-transform:uppercase;'
          'letter-spacing:1px;font-weight:600;"')
    th_c = ('style="background:#1565c0;color:#fff;padding:10px 12px;'
            'text-align:center;font-size:0.82rem;text-transform:uppercase;'
            'letter-spacing:1px;font-weight:600;"')

    rows_html = ""
    for i, r in enumerate(rows):
        rank  = r.get("display_rank", i + 1)
        icon  = rank_icons.get(rank, "")
        seed  = r["seed"]
        name  = players.get(seed, r.get("name", seed))
        row_bg = "#111827" if i % 2 == 0 else "#0d1225"

        if rank == 1:   rc = "#ffd700"
        elif rank == 2: rc = "#c0c0c0"
        elif rank == 3: rc = "#cd7f32"
        else:           rc = "#7986cb"

        rows_html += (
            f'<tr style="background:{row_bg};">'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;">'
            f'<span style="color:{rc};font-weight:700;">{icon} {rank}</span></td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'font-weight:600;color:#e8eaf6;">{name}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'color:#546e7a;">#{seed}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'color:#7986cb;text-align:center;">{r["matches"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'color:#4caf50;font-weight:700;text-align:center;">{r["wins"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'color:#ef5350;text-align:center;">{r["losses"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'color:#4fc3f7;text-align:center;">{r["sets_won"]}</td>'
            f'<td style="padding:9px 12px;border-bottom:1px solid #1e2d4f;'
            f'color:#78909c;text-align:center;">{r["sets_lost"]}</td>'
            f'</tr>'
        )

    html = (
        '<div style="overflow-x:auto;">'
        '<table style="width:100%;border-collapse:collapse;'
        'font-family:Inter,sans-serif;font-size:0.9rem;">'
        '<thead><tr>'
        f'<th {th}>#</th>'
        f'<th {th}>Spieler</th>'
        f'<th {th}>Setzung</th>'
        f'<th {th_c}>Spiele</th>'
        f'<th {th_c}>S</th>'
        f'<th {th_c}>N</th>'
        f'<th {th_c}>Sätze +</th>'
        f'<th {th_c}>Sätze −</th>'
        '</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
