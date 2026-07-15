
import streamlit as st
from datetime import date

st.set_page_config(page_title="Meine Mitte V6", page_icon="🌿", layout="centered")

# DEMO ONLY: fictional local session data
if "client" not in st.session_state:
    st.session_state.client = {
        "name": "Maria", "day": 1, "approved": False,
        "focus": "Feuchtigkeit", "filters": ["Kälte", "Mitte stärken", "Stagnation beobachten"],
        "history": [], "breakfast_status": None, "alerts": [], "open_review": None, "decision": None, "active_recipe_filters": []
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

def derive_recipe_filters():
    filters = []
    recent = C["history"][-3:]
    heat_signals = 0
    for h in recent:
        if "Hitzegefühl / starkes Schwitzen" in h.get("reaction", []):
            heat_signals += 1
        if h.get("questions", {}).get("thermal") == "mehr Hitze / Schwitzen":
            heat_signals += 1
        if h.get("body") == "warm und angenehm":
            pass

    # Katharina-Regel: ein aktueller konkreter Hitze-/Schwitzhinweis
    # aktiviert vorläufig den Rezeptfilter, ohne daraus allein ein fixes TCM-Muster abzuleiten.
    if heat_signals >= 1:
        filters.append("HITZEFILTER")

    C["active_recipe_filters"] = filters
    return filters

RECIPE_LIBRARY = [
    {
        "name": "Warmes Hirse-Birnen-Frühstück",
        "desc": "Hirse weich kochen, Birne mitgaren und mild halten.",
        "tags": {"warm_gekuechelt", "mild", "suess"},
        "ingredients": {"Hirse", "Birne"},
    },
    {
        "name": "Pikantes Reisfrühstück mit Ei",
        "desc": "Warmen Reis mit mild gedünstetem Gemüse und Ei kombinieren.",
        "tags": {"warm_gekuechelt", "pikant"},
        "ingredients": {"Reis", "Ei", "mildes Gemüse"},
    },
    {
        "name": "Hafer-Apfel-Frühstück",
        "desc": "Hafer gekocht mit Apfel.",
        "tags": {"warm_gekuechelt", "suess"},
        "ingredients": {"Hafer", "Apfel"},
    },
    {
        "name": "Warmes Polenta-Frühstück",
        "desc": "Polenta weich kochen und mild ergänzen.",
        "tags": {"warm_gekuechelt", "mild"},
        "ingredients": {"Polenta"},
    },
    {
        "name": "Mildes Reis-Congee mit Birne",
        "desc": "Reis sehr weich und eher suppig kochen; eine kleine Menge Birne mitgaren.",
        "tags": {"warm_gekuechelt", "mild", "suppig", "suess"},
        "ingredients": {"Reis", "Birne"},
    },
    {
        "name": "Mildes Reis-Gemüse-Congee",
        "desc": "Reis sehr weich und suppig kochen und mit mildem gedünstetem Gemüse ergänzen.",
        "tags": {"warm_gekuechelt", "mild", "suppig", "pikant"},
        "ingredients": {"Reis", "mildes Gemüse"},
    },
]

HEAT_EXCLUSIONS = {
    "Hafer", "Haferdrink", "Ingwer", "Zimt",
    "stark wärmende Gewürze", "erhitzende Getränke"
}

def recipe_is_allowed(recipe, filters):
    if "HITZEFILTER" in filters:
        if recipe["ingredients"] & HEAT_EXCLUSIONS:
            return False
    return True

def choose_breakfast(day, prefer_simple=False):
    filters = derive_recipe_filters()
    allowed = [r for r in RECIPE_LIBRARY if recipe_is_allowed(r, filters)]
    if prefer_simple:
        simple = [r for r in allowed if "mild" in r["tags"] and "suppig" in r["tags"]]
        if simple:
            allowed = simple
    if not allowed:
        return {
            "name": "Frühstück fachlich prüfen",
            "desc": "Für die aktiven Filter ist aktuell keine freigegebene Variante hinterlegt.",
            "tags": set(), "ingredients": set()
        }
    return allowed[(day - 1) % len(allowed)]

def katharina():
    st.title("Katharina-Dashboard 🪴")
    st.caption("V6 – erst aktuelle Filter prüfen, dann Frühstück auswählen. Keine echten Klientinnendaten.")

    x,y,z = st.columns(3)
    x.metric("Tag", f"{C['day']}/14")
    y.metric("Status", "freigegeben" if C["approved"] else "prüfen")
    z.metric("Hinweise", len(C["alerts"]))

    card("Vorläufiges Kurzbild",
         "Hinweise auf Feuchtigkeit stehen im Vordergrund. Kälte bleibt als Thermikfilter aktiv. "
         "Die Mitte wird mitgestärkt. Anspannung und Stagnation werden nicht ausschließlich über Ernährung begleitet.")

    st.subheader("Vorgeschlagene Richtung")
    st.write("**14-Tage-Schwerpunkt:** Feuchtigkeit angehen")
    st.write("**Aktive TCM-Arbeitsfilter:** " + " · ".join(C["filters"]))
    derive_recipe_filters()
    if "HITZEFILTER" in C.get("active_recipe_filters", []):
        st.warning(
            "**Aktiver Rezeptfilter: HITZEHINWEIS** – Hafer und Haferdrink werden vorläufig nicht ausgewählt. "
            "Ingwer, Zimt und stark wärmende/erhitzende Komponenten werden nicht automatisch empfohlen. "
            "Das ist noch keine endgültige Musterdiagnose."
        )
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

    if C.get("open_review"):
        st.subheader("🌿 Offener Katharina-Blick")
        review = C["open_review"]
        st.warning(
            f"Seit Tag {review['since']}: Maria berichtet wiederholt über körperlich ungünstige Reaktionen. "
            f"Aktuell genannt: {', '.join(review['reactions']) or 'keine Details'}."
        )
        st.markdown("""
**Die bisherige Richtung wird nicht automatisch verworfen.**

**Bitte mitdenken:** Menge und Esstempo · Zeitpunkt der Reaktion · Frühstück zu kompakt? · verwendetes Getreide und Zutaten · Stuhlentwicklung · Wärme-/Kälteempfinden.
        """)
        st.write("**Vorschlag:** Vor einer weiteren Rezeptrotation gezielt rückfragen und dann fachlich entscheiden.")
        d1,d2,d3 = st.columns(3)
        with d1:
            if st.button("Richtung beibehalten", use_container_width=True):
                C["decision"]="Richtung beibehalten"; C["open_review"]=None; C["breakfast_status"]="pause"; st.rerun()
        with d2:
            if st.button("Rezept anpassen", use_container_width=True):
                C["decision"]="Rezept anpassen"; C["open_review"]=None; C["breakfast_status"]="question_first"; st.rerun()
        with d3:
            if st.button("Schwerpunkt neu prüfen", use_container_width=True):
                C["decision"]="Schwerpunkt neu prüfen"; C["open_review"]=None; C["breakfast_status"]="hold"; st.rerun()

    if C.get("decision"):
        st.success(f"**Katharinas letzte Entscheidung:** {C['decision']}")

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

    question_answers = {}
    filters = derive_recipe_filters()

    if C.get("breakfast_status") == "question_first":
        card("Heute frage ich zuerst kurz nach",
             "Katharina möchte nicht einfach die nächste Frühstücksvariante ausprobieren. Vier kurze Antworten helfen bei der Anpassung.")
        question_answers["timing"] = st.radio("Wann beginnt Völlegefühl oder Druck meistens?",
            ["direkt beim/kurz nach dem Essen", "30–90 Minuten später", "erst deutlich später", "unterschiedlich"], index=None)
        question_answers["amount"] = st.radio("Wie war die Frühstücksmenge für dich?",
            ["eher klein", "passend", "eher groß"], index=None)
        question_answers["pace"] = st.radio("Wie hast du gegessen?",
            ["ruhig und langsam", "normal", "eher schnell / nebenbei"], index=None)
        question_answers["thermal"] = st.radio("Was ist dir thermisch aufgefallen?",
            ["mehr Kälte", "angenehm warm", "mehr Hitze / Schwitzen", "nichts Besonderes"], index=None)

        if all(question_answers.values()):
            # Antworten sofort in die heutige Auswahl einbeziehen.
            if question_answers["thermal"] == "mehr Hitze / Schwitzen" and "HITZEFILTER" not in filters:
                filters.append("HITZEFILTER")
                C["active_recipe_filters"] = filters

            large_fast = (
                question_answers["amount"] == "eher groß"
                and question_answers["pace"] == "eher schnell / nebenbei"
            )
            recipe = choose_breakfast(C["day"], prefer_simple=not large_fast)

            if large_fast:
                card("Dein angepasstes Frühstück heute",
                     f"Wir wechseln nicht blind die ganze Richtung. Heute testen wir zuerst eine kleinere Portion und ruhigeres Essen.<br><br>"
                     f"<b>{recipe['name']}</b><br>{recipe['desc']}<br>"
                     f"<span class='small'>Kleinere Portion · langsam essen · kurze Pause bei angenehmer Sättigung.</span>")
            else:
                card("Dein angepasstes Frühstück heute",
                     f"<b>{recipe['name']}</b><br>{recipe['desc']}<br>"
                     f"<span class='small'>Die Zusammensetzung wurde nach den aktuellen Filtern vereinfacht.</span>")

            if "HITZEFILTER" in filters:
                st.info("Heute werden Hafer/Haferdrink sowie automatisch stark wärmende Zutaten und Gewürze aus der Auswahl herausgefiltert.")

            food = st.radio("Wie ist dir das angepasste Frühstück bekommen?",
                            ["gut", "geschmacklich nicht meins", "körperlich nicht gut"], index=None)
            reaction = []
        else:
            st.info("Beantworte bitte die vier kurzen Fragen. Danach erscheint noch heute deine angepasste Frühstücksrichtung.")
            food = None
            reaction = []

    elif C.get("breakfast_status") == "hold":
        card("Katharina prüft die Begleitrichtung",
             "Hier wurde ausdrücklich „Schwerpunkt neu prüfen“ gewählt. Deshalb wird keine neue Rezeptlogik automatisch freigegeben.")
        food = "Schwerpunktprüfung"
        reaction = []

    else:
        recipe = choose_breakfast(C["day"], prefer_simple=C.get("breakfast_status") == "pause")
        title, desc = recipe["name"], recipe["desc"]
        if C.get("breakfast_status") == "pause":
            card("Heute passen wir dein Frühstück an",
                 f"Die Grundrichtung bleibt, aber die Auswahl wurde zuerst durch die aktuellen Filter geprüft.<br><br>"
                 f"<b>{title}</b><br>{desc}")
        else:
            card("Dein Frühstück heute",
                 f"<b>{title}</b><br>{desc}<br><span class='small'>Warm gekocht bedeutet nicht automatisch thermisch stark wärmend.</span>")
        if "HITZEFILTER" in filters:
            st.info("Aktueller Hitzehinweis berücksichtigt: Hafer und Haferdrink sind heute nicht in der Auswahl.")
        food = st.radio("Wie ist dir das Frühstück bekommen?",
                        ["gut", "geschmacklich nicht meins", "körperlich nicht gut"], index=None)
        reaction = []

    if food == "körperlich nicht gut":
        reaction = st.multiselect("Was ist dir aufgefallen?", [
            "Völlegefühl / Druck", "Blähungen", "Bauchschmerzen", "Übelkeit",
            "weicher Stuhl / Durchfall", "trockener / schwieriger Stuhl",
            "stärkeres Kältegefühl", "Hitzegefühl / starkes Schwitzen",
            "Müdigkeit / Schwere", "Unruhe / Herzklopfen", "etwas anderes"
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

    ready_questions = C.get("breakfast_status") != "question_first" or all(question_answers.values())
    if st.button("Tag speichern", type="primary", disabled=not (sleep and body and food and impulse and ready_questions)):
        entry = {"day": C["day"], "sleep": sleep, "body": body, "food": food, "reaction": reaction, "impulse": impulse, "questions": question_answers}
        C["history"].append(entry)

        # Simplified demo re-check logic
        if food == "gut" and C.get("breakfast_status") in ("pause", "question_first"):
            C["breakfast_status"] = None

        if food == "körperlich nicht gut":
            C["breakfast_status"] = "pause"
            heat = ("Hitzegefühl / starkes Schwitzen" in reaction or question_answers.get("thermal") == "mehr Hitze / Schwitzen")
            previous_bad = sum(1 for h in C["history"] if h["food"] == "körperlich nicht gut") >= 2
            if previous_bad and not C.get("open_review"):
                all_reactions = []
                for h in C["history"]:
                    all_reactions.extend(h.get("reaction", []))
                C["open_review"] = {"since": C["day"], "reactions": sorted(set(all_reactions)), "heat": heat}
                C["breakfast_status"] = "hold"

        if C["day"] < 14: C["day"] += 1
        st.success("Gespeichert 🌿 Morgen wird dein heutiger Verlauf mitberücksichtigt.")
        st.rerun()

def app():
    if st.session_state.view == "katharina": katharina()
    else: maria()

app()
