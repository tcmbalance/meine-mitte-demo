
import streamlit as st
from datetime import date

st.set_page_config(page_title="Meine Mitte V4", page_icon="🌿", layout="centered")

# DEMO ONLY: fictional local session data
if "client" not in st.session_state:
    st.session_state.client = {
        "name": "Maria", "day": 1, "approved": False,
        "focus": "Feuchtigkeit", "filters": ["Kälte", "Mitte stärken", "Stagnation beobachten"],
        "history": [], "breakfast_status": None, "alerts": []
    }
if "view" not in st.session_state:
    st.session_state.view = "katharina"

C = st.session_state.client

st.markdown("""
<style>
.block-container{max-width:780px;padding-top:1.5rem}
.card{border:1px solid #e2e6df;border-radius:18px;padding:18px;margin:12px 0;background:#fff}
.small{opacity:.7;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

a,b = st.columns(2)
with a:
    if st.button("🪴 Katharina", use_container_width=True): st.session_state.view="katharina"; st.rerun()
with b:
    if st.button("🌿 Maria", use_container_width=True): st.session_state.view="maria"; st.rerun()

def card(title, body):
    st.markdown(f'<div class="card"><h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)

def breakfast_for(day):
    rotation = [
        ("Warmes Hirse-Birnen-Frühstück", "Hirse weich kochen, Birne mitgaren und mild würzen."),
        ("Pikantes Reisfrühstück mit Ei", "Warmen Reis mit gedünstetem Gemüse und Ei kombinieren."),
        ("Hafer-Apfel-Frühstück", "Hafer gekocht mit Apfel; mild und warm servieren."),
        ("Warmes Polenta-Frühstück", "Polenta weich kochen und passend süß oder pikant ergänzen.")
    ]
    return rotation[(day-1) % len(rotation)]

def katharina():
    st.title("Katharina-Dashboard 🪴")
    st.caption("V4 – 14-Tage-Demo mit Verlaufsblick und automatischer Anpassung. Keine echten Klientinnendaten.")

    x,y,z = st.columns(3)
    x.metric("Tag", f"{C['day']}/14")
    y.metric("Status", "freigegeben" if C["approved"] else "prüfen")
    z.metric("Hinweise", len(C["alerts"]))

    card("Vorläufiges Kurzbild",
         "Hinweise auf Feuchtigkeit stehen im Vordergrund. Kälte bleibt als Thermikfilter aktiv. "
         "Die Mitte wird mitgestärkt. Anspannung und Stagnation werden nicht ausschließlich über Ernährung begleitet.")

    st.subheader("Vorgeschlagene Richtung")
    st.write("**14-Tage-Schwerpunkt:** Feuchtigkeit angehen")
    st.write("**Aktive Filter:** " + " · ".join(C["filters"]))
    st.write("**Begleitachsen:** Ernährung/Mitte hoch · Entspannung mittel · Bewegung/Qi-Fluss mittel")

    if not C["approved"]:
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("✅ Freigeben", use_container_width=True):
                C["approved"] = True; st.rerun()
        with c2:
            if st.button("✏️ Ändern", use_container_width=True):
                st.info("In der echten Version öffnet sich hier die fachliche Bearbeitung.")
        with c3:
            if st.button("❓ Rückfrage", use_container_width=True):
                st.info("In der echten Version wird eine gezielte Rückfrage vorbereitet.")
    else:
        st.success("Begleitrichtung für die Demo freigegeben.")

    if C["history"]:
        last = C["history"][-1]
        st.subheader("Was ist seit gestern passiert?")
        reaction_text = ", ".join(last.get("reaction", [])) if last.get("reaction") else "keine besondere Reaktion gemeldet"
        st.markdown(
            f"""
            **Maria – jetzt Tag {C['day']}**  
            🔸 Schlaf: {last['sleep']}  
            🔸 Körpergefühl: {last['body']}  
            🔸 Frühstück: {last['food']}  
            🔸 Reaktion: {reaction_text}
            """
        )

        if last["food"] == "körperlich nicht gut":
            st.info(
                "**Systemeinschätzung:** Die gestrige Frühstücksvariante wird pausiert. "
                "Die Begleitrichtung bleibt vorerst bestehen, aber die Zusammensetzung wird verändert. "
                "Verdauungsreaktion und Thermik werden weiter beobachtet."
            )
            st.write("**Nächster Schritt:** warm und gekocht beibehalten, Frühstücksart wechseln und Reaktion erneut prüfen.")
            if not C["alerts"]:
                st.success("**Katharina-Blick:** aktuell Beobachtung – noch keine zwingende persönliche Intervention.")
        else:
            st.success("**Systemeinschätzung:** bisher kein Anlass für eine sofortige Richtungsänderung.")

    if C["alerts"]:
        st.subheader("Katharina-Blick empfohlen")
        for alert in C["alerts"]:
            st.warning(alert)

    st.subheader("Verlauf")
    if not C["history"]:
        st.caption("Noch keine Tagesrückmeldungen.")
    else:
        for h in reversed(C["history"]):
            st.markdown(f"**Tag {h['day']}** – Schlaf: {h['sleep']} · Körper: {h['body']} · Frühstück: {h['food']}")
            if h.get("reaction"): st.write("Reaktion:", ", ".join(h["reaction"]))
            st.divider()

def maria():
    st.title(f"Guten Morgen, {C['name']} 🌿")
    st.caption(f"Tag {C['day']} von 14 · fiktive Demo")

    if not C["approved"]:
        card("Katharina schaut noch kurz drüber",
             "Deine erste Begleitrichtung ist noch nicht freigegeben. In der Demo kannst du in die Katharina-Ansicht wechseln.")
        return

    st.write("Heute reichen mir zwei kurze Antworten.")
    sleep = st.radio("Wie war dein Schlaf?", ["erholsam", "eher okay", "unruhig", "schlecht"], index=None)
    body = st.radio("Wie fühlt sich dein Körper heute an?", ["warm und angenehm", "eher kalt", "schwer / träge", "leicht", "innerlich gestaut / angespannt"], index=None)

    title, desc = breakfast_for(C["day"])
    if C.get("breakfast_status") == "pause":
        alternatives = [
            ("Warmes Reis-Congee, mild", "Reis sehr weich kochen und heute bewusst schlicht halten."),
            ("Pikantes Hirse-Gemüse-Frühstück", "Hirse warm mit mild gedünstetem Gemüse kombinieren."),
            ("Warme Polenta, mild pikant", "Polenta weich kochen und mit mildem gedünstetem Gemüse ergänzen.")
        ]
        title, desc = alternatives[(C["day"]-2) % len(alternatives)]
        card("Heute passen wir dein Frühstück an",
             f"Gestern hat dein Körper deutlich reagiert. Deshalb wiederholen wir die Variante nicht.<br><br>"
             f"<b>{title}</b><br>{desc}<br><span class='small'>Warm und gekocht bleibt die Richtung – die Zusammensetzung wechselt.</span>")
    else:
        card("Dein Frühstück heute", f"<b>{title}</b><br>{desc}<br><span class='small'>Nicht direkt kalt aus dem Kühlschrank. In Ruhe essen.</span>")

    food = st.radio("Wie ist dir das Frühstück bekommen?",
                    ["gut", "geschmacklich nicht meins", "körperlich nicht gut"], index=None)

    reaction = []
    if food == "körperlich nicht gut":
        reaction = st.multiselect("Was ist dir aufgefallen?", [
            "Völlegefühl / Druck", "Blähungen", "Übelkeit", "weicher Stuhl / Durchfall",
            "trockener / schwieriger Stuhl", "stärkeres Kältegefühl",
            "Hitzegefühl / starkes Schwitzen", "Müdigkeit / Schwere"
        ])

    st.subheader("Dein kleiner Impuls")
    if body == "innerlich gestaut / angespannt":
        st.info("Heute wäre eher ein kurzer Regulations- oder Bewegungsimpuls passend als noch ein weiterer Ernährungstipp.")
        impulse = st.radio("Was fühlt sich gut an?", ["EFT – Video folgt später", "Körper abklopfen", "Sanft bewegen", "Heute nichts"], index=None)
    elif body == "eher kalt":
        st.info("Heute darf der Morgen sanft und angenehm warm beginnen.")
        impulse = st.radio("Was fühlt sich gut an?", ["Nierenbereich reiben & ruhig atmen", "Körper abklopfen", "Heute nichts"], index=None)
    else:
        impulse = st.radio("Möchtest du heute einen kleinen Impuls?", ["Körper abklopfen", "Ruhig atmen", "Heute nichts"], index=None)

    if st.button("Tag speichern", type="primary", disabled=not (sleep and body and food and impulse)):
        entry = {"day": C["day"], "sleep": sleep, "body": body, "food": food, "reaction": reaction, "impulse": impulse}
        C["history"].append(entry)

        # Simplified demo re-check logic
        if food == "gut" and C.get("breakfast_status") == "pause":
            C["breakfast_status"] = None

        if food == "körperlich nicht gut" and reaction:
            C["breakfast_status"] = "pause"
            heat = "Hitzegefühl / starkes Schwitzen" in reaction or "trockener / schwieriger Stuhl" in reaction
            previous_bad = sum(1 for h in C["history"] if h["food"] == "körperlich nicht gut") >= 2
            if heat and previous_bad:
                C["alerts"].append(
                    f"Tag {C['day']}: wiederholte ungünstige Frühstücksreaktion plus Hitzehinweis. "
                    "Gesamtbild vor stärker wärmender Richtung neu prüfen."
                )
            elif previous_bad:
                C["alerts"].append(
                    f"Tag {C['day']}: wiederholte körperlich ungünstige Reaktion. Rezept pausieren und Rezept-/Muster-Recheck durchführen."
                )

        if C["day"] < 14: C["day"] += 1
        st.success("Gespeichert 🌿 Morgen wird dein heutiger Verlauf mitberücksichtigt.")
        st.rerun()

def app():
    if st.session_state.view == "katharina": katharina()
    else: maria()

app()
