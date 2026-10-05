import random

import streamlit as st

from questions import FACHS, OFFEN, QUESTIONS, SECTIONS

st.set_page_config(page_title="BiLa Lern-App", page_icon="🌾", layout="centered")
st.title("BiLa Abschlussprüfung – Lern-App")
st.caption("Multiple-Choice-Trainer zu allen Prüfungsteilen der Abschlussjahre "
           "2020–2023. Antworten belegt aus dem Unterrichtsmaterial in bila_25-27/.")


@st.cache_data
def fragenpool(sections):
    return [q for q in QUESTIONS if q["section"] in sections]


def neue_frage(pool):
    """Zieht die nächste unbeantwortete Frage und mischt die Antwortoptionen."""
    idx = st.session_state["reihenfolge"].pop()
    q = dict(pool[idx])
    optionen = [q["antwort"]] + q["falsch"] if "antwort" in q else []
    random.shuffle(optionen)
    return idx, q, optionen


def start(pool):
    st.session_state["reihenfolge"] = list(range(len(pool)))
    random.shuffle(st.session_state["reihenfolge"])
    st.session_state["fragen"] = []
    st.session_state["aktuelle"] = None
    st.session_state["wahl"] = None


def ist_offen(q):
    return "antwort" not in q


st.sidebar.header("Einstellung")
fachs = st.sidebar.multiselect("Prüfungsfach", list(FACHS), default=list(FACHS),
                               format_func=lambda f: FACHS[f])
kategorien = [s for s in SECTIONS if s == OFFEN or s.split("|")[0] in fachs]
auswahl = st.sidebar.multiselect(
    "Kategorie", kategorien, default=[s for s in kategorien if s != OFFEN],
    format_func=lambda s: SECTIONS[s],
)
pool = fragenpool(tuple(auswahl)) if auswahl else []

if st.session_state.get("auswahl") != tuple(auswahl):
    st.session_state["auswahl"] = tuple(auswahl)
    start(pool)

if not pool:
    st.warning("Bitte mindestens eine Kategorie auswählen.")
    st.stop()

st.progress(len(st.session_state["fragen"]) / len(pool),
            f"{len(st.session_state['fragen'])} von {len(pool)} Fragen")

# ---------------------------------------------------------------- aktuelle Frage
if st.session_state["aktuelle"] is None:
    if not st.session_state["reihenfolge"]:
        beantwortet = [r for _, r in st.session_state["fragen"] if r is not None]
        if all(ist_offen(q) for q in pool):
            st.success(f"### Fertig – {len(st.session_state['fragen'])} offene Aufgaben durchgegangen")
        else:
            quote = sum(beantwortet) / len(beantwortet) if beantwortet else 0
            st.success(f"### Fertig – {sum(beantwortet)} von {len(beantwortet)} Multiple-Choice-Fragen "
                       f"richtig ({quote:.0%})")
        if st.button("Nochmal von vorn"):
            start(pool)
            st.rerun()
        st.stop()
    idx, q, optionen = neue_frage(pool)
    st.session_state["aktuelle"] = (idx, q, optionen)
    st.session_state["wahl"] = None

idx, q, optionen = st.session_state["aktuelle"]
offen = ist_offen(q)

with st.container(border=True):
    fach = q["section"].split("|")[0]
    st.caption(f"{FACHS.get(fach, 'Offene Fragen')} · {SECTIONS[q['section']]} · {q['topic']} · {q['id']}")
    st.subheader(q["frage"])

    if offen:
        st.info(f"**Lücke:** {q['luecke']}")
        # ponytail: die Notiz lebt nur in der Session; ein Speichern in offene_fragen.md
        # ginge auf Streamlit Cloud nicht, weil das Dateisystem dort schreibgeschützt ist
        st.text_area("Eigene Antwort", key=f"notiz_{q['id']}", height=90)
        st.session_state["wahl"] = None
    else:
        with st.form("antwort"):
            wahl = st.radio("Antwort", optionen, label_visibility="collapsed")
            geprueft = st.form_submit_button("Antwort prüfen")

        if geprueft:
            st.session_state["wahl"] = wahl
        wahl = st.session_state["wahl"]

        if wahl is not None:
            richtig = wahl == q["antwort"]
            if richtig:
                st.success("Richtig.")
            else:
                st.error("Falsch.")
                st.info(f"Richtig wäre: **{q['antwort']}**")
            if q["hinweis"]:
                st.write(f"**Hinweis:** {q['hinweis']}")
            st.caption(f"Quelle: {q['quelle']}")

    if offen or wahl is not None:
        if st.button("Nächste Frage →"):
            st.session_state["fragen"].append((idx, None if offen else richtig))
            st.session_state["aktuelle"] = None
            st.session_state["wahl"] = None
            st.rerun()
