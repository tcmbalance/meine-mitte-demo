
import streamlit as st
from datetime import date

st.set_page_config(page_title="Meine Mitte V8", page_icon="🌿", layout="centered")

# DEMO ONLY: fictional local session data
if "client" not in st.session_state:
    st.session_state.client = {
        "name": "Maria", "day": 1, "approved": False,
        "focus": "Feuchtigkeit", "filters": ["Kälte", "Mitte stärken", "Stagnation beobachten"],
        "history": [], "breakfast_status": None, "alerts": [], "open_review": None, "decision": None, "active_recipe_filters": [], "breakfast_preference": "ausprobieren"
    }
if "view" not in st.session_state:
    st.session_state.view = "katharina"

C = st.session_state.client
C.setdefault("breakfast_preference", "ausprobieren")

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

def recipe_card(recipe, intro=""):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(recipe["name"])
    if intro:
        st.write(intro)
    st.write(recipe["desc"])
    st.markdown("**Du brauchst:**")
    for item in recipe.get("ingredients_text", []):
        st.write(f"• {item}")
    st.markdown("**So geht's:**")
    for i, step in enumerate(recipe.get("steps", []), start=1):
        st.write(f"{i}. {step}")
    st.markdown('</div>', unsafe_allow_html=True)

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
        "name": "Cremiger Hirse-Birnen-Brei",
        "desc": "Warm, weich und mit sanft gegarter Birne.",
        "ingredients_text": ["45 g Hirse", "220–250 ml Wasser oder aktuell passender Pflanzendrink", "1 kleine Birne", "1 TL Mandelmus, wenn gut vertragen"],
        "steps": ["Hirse heiß abspülen.", "Mit der Flüssigkeit aufkochen und etwa 15 Minuten weich garen.", "Birne klein schneiden und die letzten 5–7 Minuten mitgaren.", "Mandelmus bei Bedarf einrühren und in Ruhe essen."],
        "tags": {"warm_gekuechelt", "mild", "suess"}, "ingredients": {"Hirse", "Birne", "Mandelmus"},
    },
    {
        "name": "Pikantes Reisfrühstück mit Ei und Zucchini",
        "desc": "Warm, pikant und mit Kauanteil – auch mit vorgekochtem Reis praktisch.",
        "ingredients_text": ["120–150 g gekochter Reis", "1 kleine Zucchini", "1 Ei", "1 TL Öl", "eine kleine Prise Salz"],
        "steps": ["Zucchini klein schneiden und mit wenig Wasser sanft dünsten.", "Reis zugeben und vollständig erwärmen.", "Ei einrühren oder separat weich garen und dazugeben.", "Warm und ohne Eile essen."],
        "tags": {"warm_gekuechelt", "pikant", "kauanteil"}, "ingredients": {"Reis", "Ei", "Zucchini"},
    },
    {
        "name": "Warmer Hafer-Apfel-Brei",
        "desc": "Ein einfaches warmes Getreidefrühstück für Tage, an denen Hafer aktuell in die Auswahl passt.",
        "ingredients_text": ["45 g Haferflocken", "220 ml Wasser oder passender Pflanzendrink", "1 kleiner Apfel", "1 TL Nussmus, wenn gut vertragen"],
        "steps": ["Haferflocken mit der Flüssigkeit etwa 5 Minuten weich kochen.", "Apfel klein schneiden und mitgaren.", "Nussmus am Ende einrühren.", "Warm und in Ruhe essen."],
        "tags": {"warm_gekuechelt", "suess"}, "ingredients": {"Hafer", "Apfel", "Nussmus"},
    },
    {
        "name": "Cremige Polenta mit Birnenkompott",
        "desc": "Eine weiche süße Polenta-Variante mit warm gegarter Birne.",
        "ingredients_text": ["45 g feine Polenta", "250 ml Wasser oder aktuell passender Pflanzendrink", "1 kleine Birne", "1 TL Mandelmus, wenn gut vertragen"],
        "steps": ["Birne klein schneiden und mit 2–3 EL Wasser weich dünsten.", "Polenta nach Packungsangabe weich und cremig kochen.", "Birnenkompott daraufgeben.", "Bei Bedarf Mandelmus einrühren und langsam essen."],
        "tags": {"warm_gekuechelt", "mild", "suess"}, "ingredients": {"Polenta", "Birne", "Mandelmus"},
    },
    {
        "name": "Mildes Reis-Congee mit Birne",
        "desc": "Sehr weich und suppig – eine schlichte Variante, wenn der Bauch gerade Ruhe möchte.",
        "ingredients_text": ["50 g Rundkornreis", "450–550 ml Wasser", "1/2 bis 1 kleine Birne"],
        "steps": ["Reis mit Wasser aufkochen.", "Bei sehr kleiner Hitze 35–45 Minuten weich und suppig kochen; bei Bedarf Wasser ergänzen.", "Birne klein schneiden und gegen Ende mitgaren.", "Eine eher kleine Portion langsam essen und die Reaktion beobachten."],
        "tags": {"warm_gekuechelt", "mild", "suppig", "suess"}, "ingredients": {"Reis", "Birne"},
    },
    {
        "name": "Mildes Reis-Gemüse-Congee",
        "desc": "Eine warme pikante, suppige Variante mit weich gegartem Gemüse.",
        "ingredients_text": ["50 g Rundkornreis", "450–550 ml Wasser", "1 kleine Karotte", "ein kleines Stück Zucchini", "eine kleine Prise Salz"],
        "steps": ["Reis mit Wasser aufkochen und bei kleiner Hitze weich und suppig garen.", "Karotte und Zucchini sehr klein schneiden.", "Gemüse die letzten 15 Minuten mitgaren.", "Mild abschmecken und warm essen."],
        "tags": {"warm_gekuechelt", "mild", "suppig", "pikant"}, "ingredients": {"Reis", "Karotte", "Zucchini"},
    },
    {
        "name": "Warme Buchweizen-Apfel-Schale",
        "desc": "Eine weitere süße Getreidevariante für Abwechslung in der Rotation.",
        "ingredients_text": ["45 g Buchweizenflocken", "220 ml Wasser oder aktuell passender Pflanzendrink", "1 kleiner Apfel", "1 TL Mandelmus, wenn gut vertragen"],
        "steps": ["Buchweizenflocken mit der Flüssigkeit weich kochen.", "Apfel klein schneiden und mitgaren.", "Mandelmus am Ende einrühren.", "Warm und bewusst essen."],
        "tags": {"warm_gekuechelt", "mild", "suess"}, "ingredients": {"Buchweizen", "Apfel", "Mandelmus"},
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

def choose_breakfast(day, prefer_simple=False, active_filters=None, preference=None):
    # V7: Ausschlussfilter greifen vor jeder weiteren Auswahl.
    filters = list(active_filters) if active_filters is not None else derive_recipe_filters()
    allowed = [r for r in RECIPE_LIBRARY if recipe_is_allowed(r, filters)]

    if preference in {"suess", "pikant"}:
        preferred = [r for r in allowed if preference in r["tags"]]
        if preferred:
            allowed = preferred

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
    st.caption("V8 – klare Rezeptkarten, Frühstücksvorliebe und wärmere Klientinnensprache. Keine echten Klientinnendaten.")

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

    st.markdown("**Wie magst du dein Frühstück grundsätzlich lieber?**")
    pref_label = st.radio(
        "Frühstücksvorliebe",
        ["süß und weich/breiig", "pikant und mit Kauanteil", "beides", "ich möchte ausprobieren"],
        index={"suess": 0, "pikant": 1, "beides": 2, "ausprobieren": 3}.get(C.get("breakfast_preference"), 3),
        label_visibility="collapsed",
    )
    C["breakfast_preference"] = {
        "süß und weich/breiig": "suess",
        "pikant und mit Kauanteil": "pikant",
        "beides": "beides",
        "ich möchte ausprobieren": "ausprobieren",
    }[pref_label]

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
            # V7-Reihenfolge:
            # 1. Thermik-/Ausschlussfilter
            # 2. erlaubte Rezeptauswahl
            # 3. Verträglichkeit/Vereinfachung
            # 4. Portions- und Essverhalten
            recipe = choose_breakfast(
                C["day"],
                prefer_simple=not large_fast,
                active_filters=filters,
                preference=C.get("breakfast_preference"),
            )

            # Zusätzliche Sicherung: Ein durch aktive Filter gesperrtes
            # Rezept darf nicht angezeigt werden.
            if not recipe_is_allowed(recipe, filters):
                recipe = {
                    "name": "Frühstück fachlich prüfen",
                    "desc": "Die bisherige Variante passt nicht zu den aktuell aktiven Rezeptfiltern.",
                    "tags": set(),
                    "ingredients": set(),
                }

            if large_fast:
                recipe_card(
                    recipe,
                    "Heute darf dein Frühstück etwas ruhiger und leichter sein. "
                    "Wir probieren eine kleinere Portion und geben deinem Körper beim Essen mehr Zeit."
                )
                st.caption("Kleinere Portion · langsam essen · kurze Pause bei angenehmer Sättigung.")
            else:
                recipe_card(
                    recipe,
                    "Heute probieren wir eine sanftere Frühstücksvariante und beobachten, wie sie dir bekommt."
                )

            if "HITZEFILTER" in filters:
                st.info("Der aktuelle Hitzehinweis wird heute zuerst berücksichtigt: Hafer und Haferdrink sowie automatisch stark wärmende Zutaten und Gewürze werden aus der heutigen Auswahl herausgefiltert.")

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
        recipe = choose_breakfast(
            C["day"],
            prefer_simple=C.get("breakfast_status") == "pause",
            active_filters=filters,
            preference=C.get("breakfast_preference"),
        )
        if C.get("breakfast_status") == "pause":
            recipe_card(
                recipe,
                "Heute bekommt dein Bauch eine sanftere Frühstücksvariante. Beobachte einfach, wie sie dir bekommt."
            )
        else:
            recipe_card(recipe, "Hier ist dein Frühstück für heute.")
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
