
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Meine Mitte – Prototyp",
    page_icon="🌿",
    layout="centered"
)

# -----------------------------
# Demo data – only fictional
# -----------------------------
CLIENT = {
    "name": "Maria",
    "day": 4,
    "focus": "Feuchtigkeit",
    "filters": ["Kälte", "Mitte stärken", "Qi-Fluss sanft bewegen"],
    "breakfast": {
        "title": "Warmes Hafer-Birnen-Frühstück",
        "details": "Haferflocken trocken anrösten, mit Mandel- oder Haferdrink köcheln, Birne dazugeben und mild mit Zimt und Kardamom abrunden."
    },
    "impulses": {
        "EFT": "Eine kurze Klopfrunde für 'Ich bin heute zu viel im Kopf'.",
        "Körper abklopfen": "Den Körper sanft von oben nach unten und wieder zurück abklopfen. Locker bleiben, ruhig atmen.",
        "Nieren reiben": "Hände warm reiben, den unteren Rücken sanft wärmen und dabei bei frischer Luft ruhig atmen."
    }
}

if "view" not in st.session_state:
    st.session_state.view = "maria"
if "morning_done" not in st.session_state:
    st.session_state.morning_done = False
if "breakfast_feedback" not in st.session_state:
    st.session_state.breakfast_feedback = None
if "reaction_details" not in st.session_state:
    st.session_state.reaction_details = []
if "selected_impulse" not in st.session_state:
    st.session_state.selected_impulse = None
if "katharina_note" not in st.session_state:
    st.session_state.katharina_note = ""

st.markdown("""
<style>
.block-container {max-width: 760px; padding-top: 2rem;}
div[data-testid="stMetric"] {background: #f7f7f7; border-radius: 14px; padding: 12px;}
.card {padding: 1.1rem; border: 1px solid #e7e7e7; border-radius: 16px; margin-bottom: 1rem;}
.small {font-size: 0.9rem; opacity: 0.75;}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🌿 Maria-Ansicht", use_container_width=True):
        st.session_state.view = "maria"
with col2:
    if st.button("🪴 Katharina-Ansicht", use_container_width=True):
        st.session_state.view = "katharina"

st.divider()

def maria_view():
    st.title("Meine Mitte 🌿")
    st.caption("Demo-Prototyp – fiktive Testperson, keine echten Gesundheitsdaten")

    st.markdown(f"""
    <div class="card">
    <h3>Guten Morgen, {CLIENT['name']} 🌿</h3>
    <p>Du bist heute an Tag <b>{CLIENT['day']} von 14</b>.</p>
    <p>Wir bleiben heute ganz bei kleinen Schritten.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.morning_done:
        st.subheader("Dein kurzer Morgen-Check-in")
        sleep = st.radio(
            "Wie hast du geschlafen?",
            ["Sehr gut 😊", "Ganz okay 🙂", "Eher unruhig 😕", "Schlecht 😴"],
            index=None
        )
        feeling = st.radio(
            "Wie fühlt sich dein Körper heute an?",
            ["Eher kalt 🧊", "Neutral 🌿", "Eher warm 🔥", "Schwer / gestaut", "Leicht / beweglich"],
            index=None
        )
        if st.button("Morgen-Check-in speichern", type="primary", disabled=not (sleep and feeling)):
            st.session_state.morning_done = True
            st.session_state.sleep = sleep
            st.session_state.feeling = feeling
            st.rerun()
    else:
        st.success("Danke, Maria. Für heute Morgen ist schon genug beobachtet. 🌿")
        st.caption(f"Schlaf: {st.session_state.sleep} · Körpergefühl: {st.session_state.feeling}")

    st.divider()
    st.subheader("Dein Frühstück heute")
    st.markdown(f"""
    <div class="card">
    <h3>{CLIENT['breakfast']['title']}</h3>
    <p>{CLIENT['breakfast']['details']}</p>
    <p class="small">Heute einfach in Ruhe essen. Du musst nichts perfekt machen.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("Wie war das Frühstück für dich?")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("😋 Hat geschmeckt", use_container_width=True):
            st.session_state.breakfast_feedback = "geschmeckt"
            st.rerun()
    with c2:
        if st.button("😐 Geschmacklich nicht meins", use_container_width=True):
            st.session_state.breakfast_feedback = "geschmack"
            st.rerun()
    with c3:
        if st.button("😕 Körperlich nicht gut bekommen", use_container_width=True):
            st.session_state.breakfast_feedback = "koerper"
            st.rerun()

    if st.session_state.breakfast_feedback == "geschmeckt":
        st.success("Schön 😊 Dann bleibt diese Variante vorerst in deiner persönlichen Frühstücksauswahl.")
    elif st.session_state.breakfast_feedback == "geschmack":
        st.info("Alles gut. Dann suchen wir eine andere passende Variante, die dir auch wirklich schmeckt.")
        pref = st.radio(
            "Was würde dich morgen mehr ansprechen?",
            ["Süß und weich / breiig", "Pikant und mit etwas zum Kauen", "Überrasch mich mit einer passenden Alternative"],
            index=None
        )
        if pref:
            st.success(f"Notiert: {pref}. Morgen wird die Frühstücksidee entsprechend angepasst.")
    elif st.session_state.breakfast_feedback == "koerper":
        st.warning("Danke, dass du das sagst. Dann bleiben wir nicht stur bei diesem Frühstück.")
        reactions = st.multiselect(
            "Was ist dir aufgefallen?",
            [
                "Völlegefühl / Druck",
                "Blähungen",
                "Übelkeit",
                "Deutlich weicherer Stuhl / Durchfall",
                "Trockener oder schwieriger Stuhl",
                "Stärkeres Kältegefühl",
                "Hitzegefühl / starkes Schwitzen",
                "Müdigkeit / Schwere",
                "Schnell wieder hungrig",
                "Starkes Süßverlangen",
                "Etwas anderes"
            ]
        )
        repeat = st.radio(
            "War das heute zum ersten Mal oder ist dir das mit diesem Frühstück schon öfter aufgefallen?",
            ["Zum ersten Mal", "Zum zweiten Mal", "Mehrmals"],
            index=None
        )
        if reactions and repeat and st.button("Reaktion prüfen", type="primary"):
            st.session_state.reaction_details = reactions
            st.session_state.repeat = repeat
            st.rerun()

    if st.session_state.reaction_details:
        repeated = st.session_state.repeat in ["Zum zweiten Mal", "Mehrmals"]
        heat_cluster = any(x in st.session_state.reaction_details for x in ["Hitzegefühl / starkes Schwitzen", "Trockener oder schwieriger Stuhl"])
        if repeated and heat_cluster:
            st.error("Dein Verlauf hat sich möglicherweise verändert. Katharina bekommt einen Re-Check-Hinweis, bevor die Richtung angepasst wird.")
        elif repeated:
            st.info("Diese Frühstücksvariante wird pausiert. Für morgen wird eine leichtere passende Alternative aus Katharinas Rezeptwelt gewählt.")
        else:
            st.info("Wir beobachten das zunächst. Für morgen bekommst du trotzdem eine andere passende Variante, damit wir nicht stur weitermachen.")

    st.divider()
    st.subheader("Katharinas Impuls für heute")
    impulse_choice = st.radio(
        "Was würde sich heute eher gut anfühlen?",
        ["EFT-Klopfen", "Körper abklopfen", "Nieren reiben & ruhig atmen", "Heute kein Impuls"],
        index=None
    )
    if impulse_choice and impulse_choice != "Heute kein Impuls":
        mapping = {
            "EFT-Klopfen": "EFT",
            "Körper abklopfen": "Körper abklopfen",
            "Nieren reiben & ruhig atmen": "Nieren reiben"
        }
        key = mapping[impulse_choice]
        st.session_state.selected_impulse = key
        st.markdown(f"""
        <div class="card">
        <h4>{impulse_choice}</h4>
        <p>{CLIENT['impulses'][key]}</p>
        <p class="small">Kurz, sanft und ohne Leistungsdruck. Wenn es sich unangenehm anfühlt, hör auf.</p>
        </div>
        """, unsafe_allow_html=True)
        effect = st.radio(
            "Wie war der Impuls für dich?",
            ["Etwas ruhiger", "Unverändert", "Unruhiger", "Unangenehm"],
            index=None
        )
        if effect:
            st.success(f"Notiert: {effect}. Das fließt in deine persönliche Begleitung ein.")
    elif impulse_choice == "Heute kein Impuls":
        st.info("Auch das ist völlig in Ordnung. Heute musst du nichts nachholen.")

    st.divider()
    st.caption("Automatisierte Demo-Nachrichten stammen vom digitalen Begleiter nach Katharinas Methode. Persönliche Nachrichten von Katharina würden gesondert gekennzeichnet.")

def katharina_view():
    st.title("Katharina-Dashboard 🪴")
    st.caption("Demo-Prototyp – fiktive Testperson")

    a, b, c = st.columns(3)
    a.metric("Aktive Begleitungen", "1")
    b.metric("Zur Prüfung", "0")
    c.metric("Re-Check", "1" if st.session_state.reaction_details else "0")

    st.subheader("Maria · Tag 4 von 14")
    st.markdown(f"""
    <div class="card">
    <b>Schwerpunkt:</b> {CLIENT['focus']}<br>
    <b>Aktive Filter:</b> {", ".join(CLIENT['filters'])}<br>
    <b>Aktuelles Frühstück:</b> {CLIENT['breakfast']['title']}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.morning_done:
        st.write("**Heute Morgen**")
        st.write(f"- Schlaf: {st.session_state.sleep}")
        st.write(f"- Körpergefühl: {st.session_state.feeling}")

    if st.session_state.breakfast_feedback:
        st.write("**Frühstücksfeedback**")
        st.write(f"- Status: {st.session_state.breakfast_feedback}")
    if st.session_state.reaction_details:
        st.warning("Muster-/Rezeptprüfung empfohlen")
        st.write("Gemeldete Reaktionen:")
        for r in st.session_state.reaction_details:
            st.write(f"- {r}")
        st.write(f"- Wiederholung: {st.session_state.repeat}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Frühstück wechseln", use_container_width=True):
                st.success("Demo: Frühstückswechsel freigegeben.")
        with col2:
            if st.button("🔎 Re-Check starten", use_container_width=True):
                st.info("Demo: Gesamtbild wird neu geprüft.")
        with col3:
            if st.button("❓ Rückfrage senden", use_container_width=True):
                st.info("Demo: Rückfrage an Maria vorbereitet.")

    st.subheader("Persönliche Nachricht an Maria")
    note = st.text_area(
        "Nachricht",
        value=st.session_state.katharina_note,
        placeholder="Liebe Maria, ich habe kurz über deinen Verlauf geschaut ..."
    )
    if st.button("Persönliche Nachricht vormerken", disabled=not note.strip()):
        st.session_state.katharina_note = note.strip()
        st.success("Demo: Nachricht als persönliche Katharina-Nachricht vorgemerkt.")

    st.subheader("Methoden-Testnotiz")
    st.text_area(
        "Was würdest du fachlich korrigieren?",
        placeholder="Beispiel: Bei dieser Kombination würde ich stärker auf ... achten."
    )
    st.caption("In der späteren Entwicklungsphase werden solche Korrekturen als Methodenregeln dokumentiert.")

if st.session_state.view == "maria":
    maria_view()
else:
    katharina_view()
