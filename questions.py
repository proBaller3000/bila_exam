import q_pflanze
import q_tiere
import q_wiso

FACHS = {
    "pflanze": "Pflanzenproduktion",
    "tier": "Tierproduktion",
    "wiso": "Wirtschafts- und Sozialkunde",
}

_MODULE = {"pflanze": q_pflanze, "tier": q_tiere, "wiso": q_wiso}

SECTIONS = {
    f"{fach}|{key}": label
    for fach, modul in _MODULE.items()
    for key, label in modul.SECTIONS.items()
}

QUESTIONS = [
    {**q, "fach": fach, "section": f"{fach}|{q['section']}"}
    for fach, modul in _MODULE.items()
    for q in modul.QUESTIONS
]
