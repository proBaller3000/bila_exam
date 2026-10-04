import random

import streamlit as st

from questions import FACHS, QUESTIONS, SECTIONS

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
    optionen = [q["antwort"]] + q["falsch"]
    random.shuffle(optionen)
    return idx, q, optionen


def start(pool):
    st.session_state["reihenfolge"] = list(range(len(pool)))
    st.session_state["fragen"] = []
    st.session_state["richtig"] = 0
    st.session_state["aktuelle"] = None
    st.session_state["wahl"] = None


st.sidebar.header("Einstellung")
fachs = st.sidebar.multiselect("Prüfungsfach", list(FACHS), default=list(FACHS),
                               format_func=lambda f: FACHS[f])
kategorien = [s for s in SECTIONS if s.split("|")[0] in fachs]
auswahl = st.sidebar.multiselect("Kategorie", kategorien, default=kategorien,
                                 format_func=lambda s: f"{FACHS[s.split('|')[0]]} · {SECTIONS[s]}")
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
        richtig = st.session_state["richtig"]
        gesamt = len(st.session_state["fragen"])
        st.success(f"### Fertig – {richtig} von {gesamt} richtig ({richtig / gesamt:.0%})")
        if st.button("Nochmal von vorn"):
            start(pool)
            st.rerun()
        st.stop()
    idx, q, optionen = neue_frage(pool)
    st.session_state["aktuelle"] = (idx, q, optionen)
    st.session_state["wahl"] = None

idx, q, optionen = st.session_state["aktuelle"]

with st.container(border=True):
    fach = q["section"].split("|")[0]
    st.caption(f"{FACHS[fach]} · {SECTIONS[q['section']]} · {q['topic']} · {q['id']}")
    st.subheader(q["frage"])

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
        if st.button("Nächste Frage →"):
            st.session_state["fragen"].append((idx, richtig))
            if richtig:
                st.session_state["richtig"] += 1
            st.session_state["aktuelle"] = None
            st.session_state["wahl"] = None
            st.rerun()
