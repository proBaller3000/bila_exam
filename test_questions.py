from collections import Counter

import q_pflanze
import q_tiere
import q_wiso
from questions import FACHS, QUESTIONS, SECTIONS

MODULE = [q_pflanze, q_tiere, q_wiso]


def test_questions():
    ids = [q["id"] for q in QUESTIONS]
    assert len(set(ids)) == len(ids), "doppelte ID"
    assert len(QUESTIONS) >= 150, f"zu wenige Fragen: {len(QUESTIONS)}"
    for q in QUESTIONS:
        assert q["section"] in SECTIONS, q["id"]
        assert q["fach"] in FACHS, q["id"]
        assert len(q["falsch"]) == 3, q["id"]
        assert len(set(q["falsch"])) == len(q["falsch"]), f"Doppelte Falschantwort: {q['id']}"
        assert q["antwort"] not in q["falsch"], q["id"]
        assert q["frage"] and q["antwort"] and q["hinweis"] and q["quelle"], q["id"]
        assert len(q["topic"].split()) <= 4, q["id"]
        for text in [q["frage"], q["antwort"], q["hinweis"], q["quelle"], q["topic"], *q["falsch"]]:
            assert "�" not in text, q["id"]
            assert not any("一" <= c <= "鿿" for c in text), q["id"]


def test_alle_kategorien_belegt():
    for fach in FACHS:
        belegt = {s for s, q in ((q["section"], q) for q in QUESTIONS) if q["fach"] == fach}
        assert belegt == {s for s in SECTIONS if s.startswith(f"{fach}|")}, fach


if __name__ == "__main__":
    test_questions()
    test_alle_kategorien_belegt()
    for fach, name in FACHS.items():
        n = len([q for q in QUESTIONS if q["fach"] == fach])
        print(f"OK – {name}: {n} Fragen")
    print(f"OK – gesamt: {len(QUESTIONS)} Fragen in {len(SECTIONS)} Kategorien")
    print(sorted(Counter(q["section"] for q in QUESTIONS).items(), key=lambda kv: -kv[1]))
