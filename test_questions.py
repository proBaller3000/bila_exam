from collections import Counter

from questions import QUESTIONS, SECTIONS


def test_questions():
    ids = [q["id"] for q in QUESTIONS]
    assert len(set(ids)) == len(ids), "doppelte ID"
    for q in QUESTIONS:
        assert q["section"] in SECTIONS, q["id"]
        assert len(q["falsch"]) >= 2, q["id"]
        assert len(set(q["falsch"])) == len(q["falsch"]), f"Doppelte Falschantwort: {q['id']}"
        assert q["antwort"] not in q["falsch"], q["id"]
        assert q["frage"] and q["antwort"] and q["hinweis"] and q["quelle"], q["id"]


def test_alle_teile_belegt():
    assert set(Counter(q["section"] for q in QUESTIONS)) == set(SECTIONS)


if __name__ == "__main__":
    test_questions()
    test_alle_teile_belegt()
    print(f"OK – {len(QUESTIONS)} Fragen")
