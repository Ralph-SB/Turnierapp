"""
TournamentEngine – Monrad System for 16 players.

R1 (8 matches): Seeds 1v16, 2v15, 3v14, 4v13, 5v12, 6v11, 7v10, 8v9

R2 (8 matches):
  WB (4): R1-winners paired: M1w/M2w, M3w/M4w, M5w/M6w, M7w/M8w
  LB (4): R1-losers reseeded: L1vL4, L2vL3, L5vL8, L6vL7

R3 (8 matches):
  WB Semis (2): R2_WM1w vs R2_WM2w,  R2_WM3w vs R2_WM4w
  LB Semis (4): R2_WMx-loser vs R2_LMx-winner  (x=1..4)
  Consolation (2):
    R3_CON1: R2_LM1-loser vs R2_LM2-loser   (places 9-12 semi)
    R3_CON2: R2_LM3-loser vs R2_LM4-loser   (places 13-16 semi)

R4 (8 matches):
  R4_FINAL  → 1st / 2nd   (R3_WSF1w vs R3_WSF2w)
  R4_3RD    → 3rd / 4th   (R3_WSF1L vs R3_WSF2L)
  R4_5TH    → 5th / 6th   (R3_LSF1w vs R3_LSF2w)
  R4_7TH    → 7th / 8th   (R3_LSF3w vs R3_LSF4w)
  R4_9TH    → 9th / 10th  (R3_CON1w vs R3_CON2w)
  R4_11TH   → 11th / 12th (R3_LSF1L vs R3_LSF2L)
  R4_13TH   → 13th / 14th (R3_CON1L vs R3_CON2L)
  R4_15TH   → 15th / 16th (R3_LSF3L vs R3_LSF4L)

Every player is guaranteed exactly 4 matches.
"""

import copy


class TournamentEngine:
    def __init__(self, data: dict):
        self.data = copy.deepcopy(data) if data else {}

    # ── Initialize ────────────────────────────────────────────────
    def initialize(self, players: list) -> dict:
        self.data = {
            "players": {str(i + 1): players[i] for i in range(16)},
            "rounds": {},
            "current_round": 1,
            "created_at": __import__("datetime").datetime.now().isoformat(),
        }
        self._build_round_1()
        return self.data

    # ── Helpers ───────────────────────────────────────────────────
    @staticmethod
    def _make_match(round_key, match_id, p1, p2, bracket, label):
        return {
            "id": match_id,
            "round": round_key,
            "bracket": bracket,
            "label": label,
            "p1": p1,
            "p2": p2,
            "sets_p1": [],
            "sets_p2": [],
            "sets_won_p1": 0,
            "sets_won_p2": 0,
            "winner": None,
            "loser": None,
        }

    def _idx(self, round_key):
        return {m["id"]: m for m in self.data["rounds"].get(round_key, [])}

    def _w(self, rk, mid):
        m = self._idx(rk).get(mid)
        return m["winner"] if m and m["winner"] else "TBD"

    def _l(self, rk, mid):
        m = self._idx(rk).get(mid)
        return m["loser"] if m and m["loser"] else "TBD"

    # ── Round builders ────────────────────────────────────────────
    def _build_round_1(self):
        pairs = [(1,16),(2,15),(3,14),(4,13),(5,12),(6,11),(7,10),(8,9)]
        self.data["rounds"]["R1"] = [
            self._make_match("R1", f"R1_M{i+1}", str(a), str(b),
                             "winners", f"R1 Match {i+1}")
            for i, (a, b) in enumerate(pairs)
        ]

    def _build_round_2(self):
        wm = []
        for i, (ma, mb) in enumerate([("R1_M1","R1_M2"),("R1_M3","R1_M4"),
                                        ("R1_M5","R1_M6"),("R1_M7","R1_M8")]):
            wm.append(self._make_match("R2", f"R2_WM{i+1}",
                                       self._w("R1", ma), self._w("R1", mb),
                                       "winners", f"WB Round 2 – Match {i+1}"))

        losers = [self._l("R1", f"R1_M{k}") for k in range(1, 9)]
        lm = []
        for i, (a, b) in enumerate([(0,3),(1,2),(4,7),(5,6)]):
            lm.append(self._make_match("R2", f"R2_LM{i+1}",
                                       losers[a], losers[b],
                                       "losers", f"LB Round 2 – Match {i+1}"))
        self.data["rounds"]["R2"] = wm + lm

    def _build_round_3(self):
        wsf = []
        for i, (ma, mb) in enumerate([("R2_WM1","R2_WM2"),("R2_WM3","R2_WM4")]):
            wsf.append(self._make_match("R3", f"R3_WSF{i+1}",
                                        self._w("R2", ma), self._w("R2", mb),
                                        "winners", f"WB Semi-Final {i+1}"))

        lsf = []
        for i in range(1, 5):
            lsf.append(self._make_match("R3", f"R3_LSF{i}",
                                        self._l("R2", f"R2_WM{i}"),
                                        self._w("R2", f"R2_LM{i}"),
                                        "losers", f"LB Semi {i}"))

        con = [
            self._make_match("R3", "R3_CON1",
                             self._l("R2","R2_LM1"), self._l("R2","R2_LM2"),
                             "consolation", "Consolation Semi A (Places 9–12)"),
            self._make_match("R3", "R3_CON2",
                             self._l("R2","R2_LM3"), self._l("R2","R2_LM4"),
                             "consolation", "Consolation Semi B (Places 13–16)"),
        ]
        self.data["rounds"]["R3"] = wsf + lsf + con

    def _build_round_4(self):
        self.data["rounds"]["R4"] = [
            self._make_match("R4","R4_FINAL",
                             self._w("R3","R3_WSF1"), self._w("R3","R3_WSF2"),
                             "final", "🥇 FINAL – Place 1 vs 2"),
            self._make_match("R4","R4_3RD",
                             self._l("R3","R3_WSF1"), self._l("R3","R3_WSF2"),
                             "final", "🥉 3rd Place Match"),
            self._make_match("R4","R4_5TH",
                             self._w("R3","R3_LSF1"), self._w("R3","R3_LSF2"),
                             "losers", "5th Place Match"),
            self._make_match("R4","R4_7TH",
                             self._w("R3","R3_LSF3"), self._w("R3","R3_LSF4"),
                             "losers", "7th Place Match"),
            self._make_match("R4","R4_9TH",
                             self._w("R3","R3_CON1"), self._w("R3","R3_CON2"),
                             "consolation", "9th Place Match"),
            self._make_match("R4","R4_11TH",
                             self._l("R3","R3_LSF1"), self._l("R3","R3_LSF2"),
                             "consolation", "11th Place Match"),
            self._make_match("R4","R4_13TH",
                             self._l("R3","R3_CON1"), self._l("R3","R3_CON2"),
                             "consolation", "13th Place Match"),
            self._make_match("R4","R4_15TH",
                             self._l("R3","R3_LSF3"), self._l("R3","R3_LSF4"),
                             "consolation", "15th Place Match"),
        ]

    # ── Advancement ───────────────────────────────────────────────
    def get_current_round(self) -> int:
        return self.data.get("current_round", 1)

    def can_advance(self) -> bool:
        cr = self.get_current_round()
        if cr >= 4:
            return False
        key = f"R{cr}"
        if key not in self.data.get("rounds", {}):
            return False
        return all(m.get("winner") for m in self.data["rounds"][key])

    def advance_round(self):
        cr = self.get_current_round()
        builders = {1: self._build_round_2, 2: self._build_round_3,
                    3: self._build_round_4}
        if cr in builders:
            builders[cr]()
        self.data["current_round"] = cr + 1

    # ── Record result ─────────────────────────────────────────────
    def record_result(self, round_key: str, match_id: str,
                      sets_p1: list, sets_p2: list):
        for m in self.data.get("rounds", {}).get(round_key, []):
            if m["id"] == match_id:
                m["sets_p1"] = sets_p1
                m["sets_p2"] = sets_p2
                w1 = sum(1 for a, b in zip(sets_p1, sets_p2) if a > b)
                w2 = sum(1 for a, b in zip(sets_p1, sets_p2) if b > a)
                m["sets_won_p1"] = w1
                m["sets_won_p2"] = w2
                if w1 >= 3:
                    m["winner"], m["loser"] = m["p1"], m["p2"]
                elif w2 >= 3:
                    m["winner"], m["loser"] = m["p2"], m["p1"]
                else:
                    m["winner"] = m["loser"] = None
                break

    # ── Queries ───────────────────────────────────────────────────
    def get_pending_matches(self) -> list:
        result = []
        for rk in ["R1","R2","R3","R4"]:
            for m in self.data.get("rounds", {}).get(rk, []):
                if (not m.get("winner")
                        and m.get("p1") not in (None, "TBD")
                        and m.get("p2") not in (None, "TBD")):
                    result.append(m)
        return result

    def count_finished_players(self) -> int:
        finished = set()
        for m in self.data.get("rounds", {}).get("R4", []):
            if m.get("winner"):
                finished.add(m["winner"])
            if m.get("loser") and m["loser"] not in (None, "TBD"):
                finished.add(m["loser"])
        return len(finished)

    def compute_standings(self) -> list:
        players = self.data.get("players", {})
        stats = {
            seed: {"seed": seed, "name": name, "wins": 0, "losses": 0,
                   "sets_won": 0, "sets_lost": 0, "matches": 0,
                   "final_rank": None}
            for seed, name in players.items()
        }

        for matches in self.data.get("rounds", {}).values():
            for m in matches:
                if not m.get("winner"):
                    continue
                p1, p2 = m["p1"], m["p2"]
                w, l = m["winner"], m["loser"]
                sw1, sw2 = m["sets_won_p1"], m["sets_won_p2"]
                for p, sw, sl in [(p1, sw1, sw2), (p2, sw2, sw1)]:
                    if p in stats:
                        stats[p]["matches"] += 1
                        stats[p]["sets_won"]  += sw
                        stats[p]["sets_lost"] += sl
                if w in stats:
                    stats[w]["wins"] += 1
                if l in stats:
                    stats[l]["losses"] += 1

        rank_map = {
            "R4_FINAL":(1,2), "R4_3RD":(3,4),
            "R4_5TH":(5,6),   "R4_7TH":(7,8),
            "R4_9TH":(9,10),  "R4_11TH":(11,12),
            "R4_13TH":(13,14),"R4_15TH":(15,16),
        }
        r4 = self._idx("R4")
        for mid, (rw, rl) in rank_map.items():
            if mid in r4:
                m = r4[mid]
                if m.get("winner") and m["winner"] in stats:
                    stats[m["winner"]]["final_rank"] = rw
                if m.get("loser") and m["loser"] in stats:
                    stats[m["loser"]]["final_rank"] = rl

        rows = sorted(
            stats.values(),
            key=lambda r: (
                r["final_rank"] if r["final_rank"] is not None else 99,
                -r["wins"],
                -(r["sets_won"] / max(r["sets_lost"], 1))
            )
        )
        for i, r in enumerate(rows):
            r["display_rank"] = r["final_rank"] if r["final_rank"] is not None else i + 1
        return rows
