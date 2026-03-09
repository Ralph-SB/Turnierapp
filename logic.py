"""
TournamentEngine – Monrad System, 8–16 players.
- Weniger als 16 Spieler → BYE-Freilose in Runde 1
- Court 1 + Court 2 Zuweisung
- Spielzeiten 10:00–17:30

Zeitplan (2 Courts parallel):
  R1:  8 Matches → 4 Slots à 2 Courts  → 10:00 – 11:40
  R2:  8 Matches → 4 Slots à 2 Courts  → 12:00 – 13:40  (20 min Pause)
  R3:  8 Matches → 4 Slots à 2 Courts  → 14:00 – 15:40  (20 min Pause)
  R4:  8 Matches → 4 Slots à 2 Courts  → 16:00 – 17:30  (20 min Pause)

Jedes Spiel = 25 min Slot (max ~20 min Spielzeit + 5 min Wechsel).
"""

import copy
from datetime import datetime, timedelta

ROUND_START = {"R1": "10:00", "R2": "12:00", "R3": "14:00", "R4": "16:00"}
SLOT_MINUTES = 25


def _time_str(base: str, slot_index: int) -> str:
    h, m = map(int, base.split(":"))
    dt = datetime(2000, 1, 1, h, m) + timedelta(minutes=slot_index * SLOT_MINUTES)
    return dt.strftime("%H:%M")


def _assign_schedule(matches: list, round_key: str):
    base = ROUND_START.get(round_key, "10:00")
    real_matches = [m for m in matches if not m.get("is_bye")]
    slot = 0
    for i, m in enumerate(real_matches):
        court = 1 if i % 2 == 0 else 2
        if i % 2 == 0 and i > 0:
            slot += 1
        m["court"] = court
        m["time"] = _time_str(base, slot)
    for m in matches:
        if m.get("is_bye"):
            m["court"] = None
            m["time"] = None


class TournamentEngine:
    def __init__(self, data: dict):
        self.data = copy.deepcopy(data) if data else {}

    def initialize(self, players: list) -> dict:
        n = len(players)
        full = list(players) + ["BYE"] * (16 - n)
        self.data = {
            "players": {str(i + 1): full[i] for i in range(16)},
            "num_players": n,
            "rounds": {},
            "current_round": 1,
            "created_at": datetime.now().isoformat(),
        }
        self._build_round_1()
        return self.data

    @staticmethod
    def _make_match(round_key, match_id, p1, p2, bracket, label,
                    court=None, time=None):
        is_bye = (p2 == "BYE") or (p1 == "BYE")
        return {
            "id": match_id,
            "round": round_key,
            "bracket": bracket,
            "label": label,
            "p1": p1,
            "p2": p2,
            "court": court,
            "time": time,
            "sets_p1": [],
            "sets_p2": [],
            "sets_won_p1": 0,
            "sets_won_p2": 0,
            "winner": None,
            "loser": None,
            "is_bye": is_bye,
        }

    def _idx(self, rk):
        return {m["id"]: m for m in self.data["rounds"].get(rk, [])}

    def _is_real(self, seed):
        return seed not in (None, "TBD", "BYE", "")

    def _w(self, rk, mid):
        m = self._idx(rk).get(mid)
        if not m:
            return "TBD"
        if m.get("is_bye"):
            return m["p1"] if self._is_real(m["p1"]) else "BYE"
        return m["winner"] if m.get("winner") else "TBD"

    def _l(self, rk, mid):
        m = self._idx(rk).get(mid)
        if not m:
            return "TBD"
        if m.get("is_bye"):
            return "BYE"
        return m["loser"] if m.get("loser") else "TBD"

    def _make_bye_or_real(self, rid, mid, p1, p2, bracket, label):
        """Erstellt ein Match und behandelt BYEs automatisch."""
        r1 = self._is_real(p1)
        r2 = self._is_real(p2)
        if not r1 and not r2:
            m = self._make_match(rid, mid, "BYE", "BYE", bracket, label)
            m["is_bye"] = True
            return m
        elif not r1:
            m = self._make_match(rid, mid, p2, "BYE", bracket, label + " – Freilos")
            m["winner"] = p2; m["loser"] = "BYE"; m["is_bye"] = True
            return m
        elif not r2:
            m = self._make_match(rid, mid, p1, "BYE", bracket, label + " – Freilos")
            m["winner"] = p1; m["loser"] = "BYE"; m["is_bye"] = True
            return m
        return self._make_match(rid, mid, p1, p2, bracket, label)

    def _build_round_1(self):
        players = self.data["players"]
        pairs = [(1,16),(2,15),(3,14),(4,13),(5,12),(6,11),(7,10),(8,9)]
        matches = []
        for i, (a, b) in enumerate(pairs):
            pa = str(a); pb = str(b)
            name_a = players.get(pa, "BYE")
            name_b = players.get(pb, "BYE")
            real_a = name_a != "BYE"
            real_b = name_b != "BYE"
            if not real_a and not real_b:
                m = self._make_match("R1", f"R1_M{i+1}", "BYE", "BYE",
                                     "winners", f"R1 Match {i+1}")
                m["is_bye"] = True
            elif not real_b:
                m = self._make_match("R1", f"R1_M{i+1}", pa, "BYE",
                                     "winners", f"R1 Match {i+1} – Freilos")
                m["winner"] = pa; m["loser"] = "BYE"; m["is_bye"] = True
            elif not real_a:
                m = self._make_match("R1", f"R1_M{i+1}", pb, "BYE",
                                     "winners", f"R1 Match {i+1} – Freilos")
                m["winner"] = pb; m["loser"] = "BYE"; m["is_bye"] = True
            else:
                m = self._make_match("R1", f"R1_M{i+1}", pa, pb,
                                     "winners", f"R1 Match {i+1}")
            matches.append(m)
        _assign_schedule(matches, "R1")
        self.data["rounds"]["R1"] = matches

    def _build_round_2(self):
        wm = []
        for i, (ma, mb) in enumerate([
            ("R1_M1","R1_M2"),("R1_M3","R1_M4"),
            ("R1_M5","R1_M6"),("R1_M7","R1_M8")
        ]):
            p1, p2 = self._w("R1", ma), self._w("R1", mb)
            wm.append(self._make_bye_or_real(
                "R2", f"R2_WM{i+1}", p1, p2, "winners", f"WB Runde 2 – Match {i+1}"))

        losers_raw = [self._l("R1", f"R1_M{k}") for k in range(1, 9)]
        losers = [l for l in losers_raw if self._is_real(l)]
        # Auf 8 auffüllen
        while len(losers) < 8:
            losers.append("BYE")

        lm = []
        for i, (a, b) in enumerate([(0,3),(1,2),(4,7),(5,6)]):
            lm.append(self._make_bye_or_real(
                "R2", f"R2_LM{i+1}", losers[a], losers[b],
                "losers", f"LB Runde 2 – Match {i+1}"))

        all_m = wm + lm
        _assign_schedule(all_m, "R2")
        self.data["rounds"]["R2"] = all_m

    def _build_round_3(self):
        wsf = []
        for i, (ma, mb) in enumerate([("R2_WM1","R2_WM2"),("R2_WM3","R2_WM4")]):
            wsf.append(self._make_bye_or_real(
                "R3", f"R3_WSF{i+1}", self._w("R2", ma), self._w("R2", mb),
                "winners", f"WB Halbfinale {i+1}"))

        lsf = []
        for i in range(1, 5):
            lsf.append(self._make_bye_or_real(
                "R3", f"R3_LSF{i}",
                self._l("R2", f"R2_WM{i}"), self._w("R2", f"R2_LM{i}"),
                "losers", f"LB Halbfinale {i}"))

        con = [
            self._make_bye_or_real("R3","R3_CON1",
                self._l("R2","R2_LM1"), self._l("R2","R2_LM2"),
                "consolation","Trost-Halbfinale A (Plätze 9–12)"),
            self._make_bye_or_real("R3","R3_CON2",
                self._l("R2","R2_LM3"), self._l("R2","R2_LM4"),
                "consolation","Trost-Halbfinale B (Plätze 13–16)"),
        ]

        all_m = wsf + lsf + con
        _assign_schedule(all_m, "R3")
        self.data["rounds"]["R3"] = all_m

    def _build_round_4(self):
        matches = [
            self._make_bye_or_real("R4","R4_FINAL",
                self._w("R3","R3_WSF1"), self._w("R3","R3_WSF2"),
                "final","🥇 FINALE – Platz 1 vs 2"),
            self._make_bye_or_real("R4","R4_3RD",
                self._l("R3","R3_WSF1"), self._l("R3","R3_WSF2"),
                "final","🥉 Platz 3 Match"),
            self._make_bye_or_real("R4","R4_5TH",
                self._w("R3","R3_LSF1"), self._w("R3","R3_LSF2"),
                "losers","Platz 5 Match"),
            self._make_bye_or_real("R4","R4_7TH",
                self._w("R3","R3_LSF3"), self._w("R3","R3_LSF4"),
                "losers","Platz 7 Match"),
            self._make_bye_or_real("R4","R4_9TH",
                self._w("R3","R3_CON1"), self._w("R3","R3_CON2"),
                "consolation","Platz 9 Match"),
            self._make_bye_or_real("R4","R4_11TH",
                self._l("R3","R3_LSF1"), self._l("R3","R3_LSF2"),
                "consolation","Platz 11 Match"),
            self._make_bye_or_real("R4","R4_13TH",
                self._l("R3","R3_CON1"), self._l("R3","R3_CON2"),
                "consolation","Platz 13 Match"),
            self._make_bye_or_real("R4","R4_15TH",
                self._l("R3","R3_LSF3"), self._l("R3","R3_LSF4"),
                "consolation","Platz 15 Match"),
        ]
        _assign_schedule(matches, "R4")
        self.data["rounds"]["R4"] = matches

    def get_current_round(self) -> int:
        return self.data.get("current_round", 1)

    def can_advance(self) -> bool:
        cr = self.get_current_round()
        if cr >= 4:
            return False
        key = f"R{cr}"
        if key not in self.data.get("rounds", {}):
            return False
        for m in self.data["rounds"][key]:
            if m.get("is_bye"):
                continue
            if not m.get("winner"):
                return False
        return True

    def advance_round(self):
        cr = self.get_current_round()
        for m in self.data.get("rounds", {}).get(f"R{cr}", []):
            if m.get("is_bye") and not m.get("winner") and self._is_real(m.get("p1","")):
                m["winner"] = m["p1"]
                m["loser"] = "BYE"
        builders = {1: self._build_round_2, 2: self._build_round_3,
                    3: self._build_round_4}
        if cr in builders:
            builders[cr]()
        self.data["current_round"] = cr + 1

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

    def get_pending_matches(self) -> list:
        result = []
        for rk in ["R1","R2","R3","R4"]:
            for m in self.data.get("rounds", {}).get(rk, []):
                if m.get("is_bye"):
                    continue
                if (not m.get("winner")
                        and self._is_real(m.get("p1",""))
                        and self._is_real(m.get("p2",""))):
                    result.append(m)
        return result

    def count_finished_players(self) -> int:
        finished = set()
        for m in self.data.get("rounds", {}).get("R4", []):
            if m.get("winner") and self._is_real(m["winner"]):
                finished.add(m["winner"])
            if m.get("loser") and self._is_real(m["loser"]):
                finished.add(m["loser"])
        return len(finished)

    def compute_standings(self) -> list:
        players = self.data.get("players", {})
        stats = {}
        for seed, name in players.items():
            if name == "BYE":
                continue
            stats[seed] = {
                "seed": seed, "name": name, "wins": 0, "losses": 0,
                "sets_won": 0, "sets_lost": 0, "matches": 0,
                "final_rank": None
            }
        for matches in self.data.get("rounds", {}).values():
            for m in matches:
                if not m.get("winner") or m.get("is_bye"):
                    continue
                p1, p2 = m["p1"], m["p2"]
                w, l = m["winner"], m["loser"]
                sw1, sw2 = m["sets_won_p1"], m["sets_won_p2"]
                for p, sw, sl in [(p1, sw1, sw2), (p2, sw2, sw1)]:
                    if p in stats:
                        stats[p]["matches"] += 1
                        stats[p]["sets_won"] += sw
                        stats[p]["sets_lost"] += sl
                if w in stats:
                    stats[w]["wins"] += 1
                if l in stats:
                    stats[l]["losses"] += 1

        rank_map = {
            "R4_FINAL":(1,2),"R4_3RD":(3,4),
            "R4_5TH":(5,6),"R4_7TH":(7,8),
            "R4_9TH":(9,10),"R4_11TH":(11,12),
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

    def get_schedule(self) -> list:
        result = []
        for rk in ["R1","R2","R3","R4"]:
            for m in self.data.get("rounds", {}).get(rk, []):
                if not m.get("is_bye") and m.get("time"):
                    result.append(m)
        result.sort(key=lambda m: (m.get("time","99:99"), m.get("court", 9)))
        return result
