import re
from pathlib import Path

import q_pflanze
import q_tiere
import q_wiso

FACHS = {
    "pflanze": "Pflanzenproduktion",
    "tier": "Tierproduktion",
    "wiso": "Wirtschafts- und Sozialkunde",
}

OFFEN = "offen|fragen"

_MODULE = {"pflanze": q_pflanze, "tier": q_tiere, "wiso": q_wiso}

SECTIONS = {
    f"{fach}|{key}": label
    for fach, modul in _MODULE.items()
    for key, label in modul.SECTIONS.items()
}
SECTIONS[OFFEN] = "Offene Fragen"


def _feld(block, name):
    m = re.search(rf"\*\*{name}:\*\*\s*(.+?)(?=\n\*\*|\Z)", block, re.S)
    return " ".join(m.group(1).split()) if m else ""


# ponytail: offene Fragen werden beim Start einmal gelesen, ein Bearbeiten
# von offene_fragen.md erfordert deshalb einen Neustart der App
def _offene_fragen():
    datei = Path(__file__).parent / "offene_fragen.md"
    if not datei.exists():
        return []
    fragen = []
    for block in re.split(r"^### ", datei.read_text(encoding="utf-8"), flags=re.M)[1:]:
        kopf = block.splitlines()[0].partition(" ")
        frage = _feld(block, "Frage")
        if not frage:
            continue
        titel = kopf[2].lstrip(" ·").strip()
        fragen.append(dict(
            id=kopf[0], section=OFFEN, fach="offen",
            topic=titel.split("· Prüfung")[0].split("(")[0].strip(" ·"),
            frage=frage, hinweis="", quelle=titel,
            luecke=_feld(block, "Lücke"),
        ))
    return fragen


QUESTIONS = [
    {**q, "fach": fach, "section": f"{fach}|{q['section']}"}
    for fach, modul in _MODULE.items()
    for q in modul.QUESTIONS
] + _offene_fragen()
