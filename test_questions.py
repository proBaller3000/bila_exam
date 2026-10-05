import re
from collections import Counter
from pathlib import Path

import q_pflanze
import q_tiere
import q_wiso
from questions import FACHS, OFFEN, QUESTIONS, SECTIONS

MODULE = [q_pflanze, q_tiere, q_wiso]
MCQ = [q for q in QUESTIONS if q["section"] != OFFEN]
OFFEN_FRAGEN = [q for q in QUESTIONS if q["section"] == OFFEN]


def test_mcq():
    ids = [q["id"] for q in MCQ]
    assert len(set(ids)) == len(ids), "doppelte ID"
    assert len(MCQ) >= 150, f"zu wenige Fragen: {len(MCQ)}"
    for q in MCQ:
        assert q["section"] in SECTIONS, q["id"]
        assert q["fach"] in FACHS, q["id"]
        assert len(q["falsch"]) == 3, q["id"]
        assert len(set(q["falsch"])) == len(q["falsch"]), f"Doppelte Falschantwort: {q['id']}"
        assert q["antwort"] not in q["falsch"], q["id"]
        assert q["frage"] and q["antwort"] and q["hinweis"] and q["quelle"], q["id"]
        assert len(q["topic"].split()) <= 4, q["id"]
        assert "�" not in q["frage"], q["id"]
        assert not any("一" <= c <= "鿿" for c in q["frage"]), q["id"]


def test_alle_kategorien_belegt():
    for fach in FACHS:
        belegt = {q["section"] for q in MCQ if q["fach"] == fach}
        assert belegt == {s for s in SECTIONS if s.startswith(f"{fach}|")}, fach
    assert OFFEN_FRAGEN, "keine offenen Fragen gefunden"


def test_offene_fragen():
    ids = [q["id"] for q in OFFEN_FRAGEN]
    assert len(set(ids)) == len(ids), "doppelte ID"
    for q in OFFEN_FRAGEN:
        assert q["frage"] and q["luecke"] and q["quelle"], q["id"]
        assert "antwort" not in q and "falsch" not in q, q["id"]


def test_offene_fragen_ohne_antwort():
    text = Path("offene_fragen.md").read_text(encoding="utf-8")
    bloecke = re.split(r"^### ", text, flags=re.M)[1:]
    assert all(all(not f.strip() for f in re.findall(r"\*\*Antwort:\*\*([^*]*)", b)) for b in bloecke), \
        "Antwortfeld ausgefuellt"
    assert len(bloecke) == len(OFFEN_FRAGEN), "nicht alle Eintraege eingelesen"


if __name__ == "__main__":
    test_mcq()
    test_alle_kategorien_belegt()
    test_offene_fragen()
    test_offene_fragen_ohne_antwort()
    for fach, name in FACHS.items():
        n = len([q for q in MCQ if q["fach"] == fach])
        print(f"OK – {name}: {n} Fragen")
    print(f"OK – gesamt: {len(MCQ)} Multiple-Choice-Fragen in {len(SECTIONS) - 1} Kategorien")
    print(f"OK – {SECTIONS[OFFEN]}: {len(OFFEN_FRAGEN)} Aufgaben")
    print(sorted(Counter(q["section"] for q in MCQ).items(), key=lambda kv: -kv[1]))
