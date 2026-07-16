
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Meine Mitte 1.0",
    page_icon="🌿",
    layout="centered",
)

# ------------------------------------------------------------
# Meine Mitte 1.0 – saubere Neuprogrammierung als MVP-Demo
# Nur für fiktive Testdaten. Keine echte Gesundheitsdatenbank.
# ------------------------------------------------------------

DEFAULT_CLIENT = {
    "name": "",
    "day": 1,
    "onboarding_complete": False,
    "approved": False,
    "approved_direction": "",
    "approval_note": "",
    "anamnesis": {},
    "assessment": {},
    "morning": {},
    "evening": {},
    "history": [],
    "preferences": {
        "breakfast": "ausprobieren",
        "vegetables": [],
        "dislikes": [],
    },
}

if "client" not in st.session_state:
    st.session_state.client = DEFAULT_CLIENT.copy()

if "view" not in st.session_state:
    st.session_state.view = "client"

C = st.session_state.client

# Ensure nested dictionaries survive future upgrades.
C.setdefault("preferences", {})
C["preferences"].setdefault("breakfast", "ausprobieren")
C["preferences"].setdefault("vegetables", [])
C["preferences"].setdefault("dislikes", [])
C.setdefault("morning", {})
C.setdefault("evening", {})
C.setdefault("history", [])

st.markdown(
    """
    <style>
      .block-container {max-width: 820px; padding-top: 1.4rem; padding-bottom: 3rem;}
      .mm-card {
        border: 1px solid #dfe6df;
        border-radius: 18px;
        padding: 18px;
        margin: 12px 0;
        background: white;
      }
      .mm-soft {
        background: #eef5ee;
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
      }
      .mm-small {opacity: .72; font-size: .9rem;}
      .mm-title {font-size: 1.15rem; font-weight: 700; margin-bottom: .35rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_demo():
    st.session_state.client = DEFAULT_CLIENT.copy()
    st.session_state.view = "client"
    st.rerun()


def client_name():
    return (C.get("name") or "Klientin").strip()


def render_navigation():
    left, right = st.columns(2)
    with left:
        if st.button("🪴 Katharina", use_container_width=True):
            st.session_state.view = "katharina"
            st.rerun()
    with right:
        if st.button(f"🌿 {client_name()}", use_container_width=True):
            st.session_state.view = "client"
            st.rerun()


def add_score(scores, reasons, key, value, reason):
    scores[key] += value
    reasons[key].append(reason)


def assess_anamnesis(a):
    scores = {
        "Feuchtigkeit": 0,
        "Mitte stärken": 0,
        "Hitzehinweise": 0,
        "Kältehinweise": 0,
        "Stagnationshinweise": 0,
    }
    reasons = {key: [] for key in scores}

    for item in a.get("digestion", []):
        if item in {"Völlegefühl / Druck", "Blähungen", "Schwere nach dem Essen"}:
            add_score(scores, reasons, "Feuchtigkeit", 2, item)
            add_score(scores, reasons, "Mitte stärken", 2, item)
        if item in {"weicher Stuhl / Durchfall", "unverdaute Nahrungsbestandteile"}:
            add_score(scores, reasons, "Mitte stärken", 2, item)
            add_score(scores, reasons, "Feuchtigkeit", 1, item)
        if item == "trockener / schwieriger Stuhl":
            add_score(scores, reasons, "Hitzehinweise", 1, item)

    for item in a.get("body", []):
        if item in {"Schwere / Trägheit", "Wassereinlagerungen", "viel Schleim"}:
            add_score(scores, reasons, "Feuchtigkeit", 2, item)
        if item in {"Hitzegefühl", "starkes Schwitzen", "innere Unruhe mit Wärme"}:
            add_score(scores, reasons, "Hitzehinweise", 2, item)
        if item in {"kalte Hände / Füße", "Frieren", "Wärme tut gut"}:
            add_score(scores, reasons, "Kältehinweise", 2, item)
            add_score(scores, reasons, "Mitte stärken", 1, item)

    for item in a.get("food_habits", []):
        if item in {
            "viel Brot / Gebäck",
            "viel Käse",
            "häufig Joghurt / kalte Milchprodukte",
            "häufig Süßigkeiten",
        }:
            add_score(scores, reasons, "Feuchtigkeit", 2, item)
            add_score(scores, reasons, "Mitte stärken", 1, item)
        if item in {"viel Rohkost", "häufig kalte Speisen / Getränke"}:
            add_score(scores, reasons, "Kältehinweise", 1, item)
            add_score(scores, reasons, "Mitte stärken", 1, item)

    if a.get("thermal") == "eher kalt / friere leicht":
        add_score(scores, reasons, "Kältehinweise", 3, "thermisches Empfinden")
    elif a.get("thermal") == "eher heiß / viel Schwitzen":
        add_score(scores, reasons, "Hitzehinweise", 3, "thermisches Empfinden")

    if a.get("sleep") in {"unruhig", "häufiges Erwachen", "Gedankenkreisen / lange Einschlafzeit"}:
        add_score(scores, reasons, "Stagnationshinweise", 1, f"Schlaf: {a.get('sleep')}")

    if a.get("energy") in {"müde / schwer", "Einbruch nach dem Essen"}:
        add_score(scores, reasons, "Mitte stärken", 2, f"Energie: {a.get('energy')}")
        add_score(scores, reasons, "Feuchtigkeit", 1, f"Energie: {a.get('energy')}")

    for item in a.get("emotions", []):
        if item in {"viel Wut / Ärger", "gereizt", "innerlich angespannt", "emotional wechselhaft"}:
            add_score(scores, reasons, "Stagnationshinweise", 1, f"emotionaler Hinweis: {item}")
        if item in {"grübelnd / viele Gedanken", "erschöpft", "antriebslos"}:
            add_score(scores, reasons, "Mitte stärken", 1, f"emotionaler Hinweis: {item}")

    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)

    current_heat_signals = [
        item for item in a.get("body", [])
        if item in {"Hitzegefühl", "starkes Schwitzen", "innere Unruhe mit Wärme"}
    ]
    if a.get("thermal") == "eher heiß / viel Schwitzen":
        current_heat_signals.append("überwiegend heiß / viel Schwitzen")

    relevant_heat = bool(current_heat_signals) and scores["Hitzehinweise"] >= 3
    underlying = next(
        (name for name, value in ranked if name != "Hitzehinweise" and value > 0),
        None,
    )

    contradictions = []
    if scores["Hitzehinweise"] >= 2 and scores["Kältehinweise"] >= 2:
        contradictions.append(
            "Hitze- und Kältehinweise treten gemeinsam auf. Thermik nicht vereinfachen."
        )
    if scores["Feuchtigkeit"] >= 4 and scores["Stagnationshinweise"] >= 3:
        contradictions.append(
            "Feuchtigkeit und Stagnationshinweise treten gemeinsam auf. Ernährung nicht als einzigen Begleitbaustein behandeln."
        )

    return {
        "scores": scores,
        "reasons": reasons,
        "ranked": ranked,
        "relevant_heat": relevant_heat,
        "heat_signals": current_heat_signals,
        "underlying": underlying,
        "contradictions": contradictions,
    }


VEGETABLES = [
    "Artischocke", "Aubergine", "Bambussprossen", "Batate / Süßkartoffel",
    "Blumenkohl", "Brokkoli", "Chicorée", "Chinakohl", "Erbsen", "Fenchel",
    "Fisolen / grüne Bohnen", "Gurke", "Karotte / Möhre", "Kartoffel",
    "Knollensellerie", "Kohlrabi", "Kürbis", "Lauch / Porree", "Mangold",
    "Pak Choi", "Paprika", "Pastinake", "Petersilienwurzel", "Radicchio",
    "Radieschen", "Rettich", "Romanesco", "Rosenkohl", "Rote Bete / Rote Rübe",
    "Rotkohl / Rotkraut", "Rucola", "Schwarzwurzel", "Spargel grün",
    "Spargel weiß", "Spinat", "Spitzkohl", "Steckrübe", "Tomate",
    "Topinambur", "Weißkohl / Weißkraut", "Wirsing", "Zucchini",
    "Zuckererbsen", "Zuckermais", "Zwiebel",
]


BREAKFASTS = {
    "suess": [
        {
            "name": "Mildes Reis-Congee mit Birne",
            "ingredients": ["50 g Rundkornreis", "450–550 ml Wasser", "½–1 kleine Birne"],
            "steps": [
                "Reis mit Wasser aufkochen.",
                "Bei kleiner Hitze 35–45 Minuten weich und suppig kochen.",
                "Birne gegen Ende klein geschnitten mitgaren.",
                "Eine eher kleine Portion langsam essen.",
            ],
        },
        {
            "name": "Cremige Polenta mit Birnenkompott",
            "ingredients": ["45 g feine Polenta", "250 ml Wasser", "1 kleine Birne"],
            "steps": [
                "Birne klein schneiden und mit wenig Wasser weich dünsten.",
                "Polenta cremig kochen.",
                "Birnenkompott dazugeben.",
                "Langsam und in Ruhe essen.",
            ],
        },
        {
            "name": "Cremiger Hirse-Birnen-Brei",
            "ingredients": ["45 g Hirse", "220–250 ml Wasser", "1 kleine Birne"],
            "steps": [
                "Hirse heiß abspülen.",
                "Mit Wasser weich garen.",
                "Birne die letzten Minuten mitgaren.",
                "In Ruhe essen und Sättigung beobachten.",
            ],
        },
    ],
    "pikant": [
        {
            "name": "Mildes Reis-Gemüse-Congee",
            "ingredients": ["50 g Rundkornreis", "450–550 ml Wasser", "mildes Gemüse nach Geschmack"],
            "steps": [
                "Reis weich und suppig kochen.",
                "Gemüse klein schneiden.",
                "Gemüse gegen Ende sanft mitgaren.",
                "Mild abschmecken und warm essen.",
            ],
        },
        {
            "name": "Pikantes Reisfrühstück mit Ei und Gemüse",
            "ingredients": ["120–150 g gekochter Reis", "Gemüse nach Geschmack", "1 Ei"],
            "steps": [
                "Gemüse im Dampfgarer oder im eigenen Saft garen.",
                "Reis vollständig erwärmen.",
                "Ei untermengen oder separat weich garen.",
                "Warm und ohne Eile essen.",
            ],
        },
    ],
}


def select_breakfast():
    pref = C["preferences"].get("breakfast", "ausprobieren")
    assessment = C.get("assessment", {})

    # Katharina-Praxisregel: bei aktuellem relevanten Hitze-/Schwitzhinweis
    # Hafer nicht priorisieren. Diese MVP-Auswahl enthält bewusst keinen Hafer.
    if pref == "pikant":
        pool = BREAKFASTS["pikant"]
    elif pref == "suess":
        pool = BREAKFASTS["suess"]
    elif pref == "beides":
        pool = BREAKFASTS["suess"] + BREAKFASTS["pikant"]
    else:
        pool = BREAKFASTS["suess"] + BREAKFASTS["pikant"]

    return pool[(C["day"] - 1) % len(pool)]


def render_recipe(recipe, intro):
    st.markdown('<div class="mm-card">', unsafe_allow_html=True)
    st.subheader(recipe["name"])
    st.write(intro)
    st.markdown("**Du brauchst:**")
    for item in recipe["ingredients"]:
        st.write(f"• {item}")
    st.markdown("**So geht's:**")
    for index, step in enumerate(recipe["steps"], start=1):
        st.write(f"{index}. {step}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_welcome():
    st.title("🌿 Meine Mitte")
    st.markdown(
        """
        <div class="mm-card">
          <div class="mm-title">Herzlich willkommen.</div>
          <p>In den nächsten 14 Tagen begleite ich dich Schritt für Schritt.</p>
          <p>Wir betrachten Körper, Geist und Seele als zusammengehörig. Schlaf, Verdauung,
          Energie, Gefühle, Bewegung und Ernährung sind Puzzleteile deines persönlichen Gesamtbildes.</p>
          <p>Es geht nicht darum, perfekt zu sein. Es geht darum, deinen Körper besser zu verstehen
          und ihm wieder Energie zu geben.</p>
          <p><strong>Deine Katharina</strong> 🌿</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Begleitung starten", type="primary", use_container_width=True):
        C["started"] = True
        st.rerun()


def render_anamnesis():
    st.title("Deine Erstanamnese 🌿")
    st.write(
        "Jede Antwort ist ein kleines Puzzleteil. Gemeinsam helfen sie uns, dein persönliches Gesamtbild besser zu verstehen."
    )
    st.caption("MVP-Demo: Bitte noch keine echten Gesundheitsdaten eingeben.")

    with st.form("anamnesis"):
        name = st.text_input("Wie darf ich dich ansprechen?")

        concerns = st.multiselect(
            "Was hat dich zu Meine Mitte geführt?",
            [
                "Verdauungsbeschwerden", "schlechter Schlaf", "Müdigkeit / Erschöpfung",
                "wenig Energie", "Hautthemen", "Kinderwunsch", "Wechseljahre",
                "Gewicht verändern / abnehmen", "Blähungen / Völlegefühl",
                "häufiges Frieren", "Hitze / starkes Schwitzen", "Stress / Überforderung",
                "Allergien / Unverträglichkeiten", "etwas anderes",
            ],
        )

        digestion = st.multiselect(
            "Was kennst du von deiner Verdauung?",
            [
                "Völlegefühl / Druck", "Blähungen", "Schwere nach dem Essen",
                "weicher Stuhl / Durchfall", "unverdaute Nahrungsbestandteile",
                "trockener / schwieriger Stuhl", "nichts davon",
            ],
        )

        body = st.multiselect(
            "Was fällt dir körperlich häufiger auf?",
            [
                "Schwere / Trägheit", "Wassereinlagerungen", "viel Schleim",
                "Hitzegefühl", "starkes Schwitzen", "innere Unruhe mit Wärme",
                "kalte Hände / Füße", "Frieren", "Wärme tut gut", "nichts davon",
            ],
        )

        thermal = st.radio(
            "Wie erlebst du dich thermisch meistens?",
            ["eher kalt / friere leicht", "ausgeglichen", "eher heiß / viel Schwitzen", "wechselt stark"],
            index=None,
        )

        sleep = st.radio(
            "Wie ist dein Schlaf meistens?",
            [
                "ruhig", "Gedankenkreisen / lange Einschlafzeit", "unruhig",
                "häufiges Erwachen", "sehr unterschiedlich",
            ],
            index=None,
        )

        energy = st.radio(
            "Wie ist deine Energie im Alltag?",
            ["stabil", "müde / schwer", "Einbruch nach dem Essen", "unruhig / schwer abzuschalten", "wechselhaft"],
            index=None,
        )

        food_habits = st.multiselect(
            "Was gehört derzeit häufig zu deinem Essalltag?",
            [
                "ich frühstücke nicht", "viel Brot / Gebäck", "viel Käse",
                "häufig Joghurt / kalte Milchprodukte", "häufig Süßigkeiten",
                "viel Rohkost", "häufig kalte Speisen / Getränke",
                "überwiegend warm und gekocht",
            ],
        )

        breakfast_label = st.radio(
            "Wie magst du dein Frühstück?",
            ["süß und weich/breiig", "pikant und mit Kauanteil", "beides", "ich möchte ausprobieren"],
            index=None,
        )

        emotions = st.multiselect(
            "Wie geht es dir emotional im Moment?",
            [
                "ausgeglichen", "ängstlich", "unsicher",
                "wenig Selbstvertrauen / wenig Selbstbewusstsein",
                "Panikgefühle", "depressive Verstimmung / niedergeschlagen",
                "viel Wut / Ärger", "gereizt", "innerlich angespannt",
                "grübelnd / viele Gedanken", "traurig", "überfordert",
                "erschöpft", "antriebslos", "emotional wechselhaft",
                "Rückzug / möchte eher allein sein",
            ],
        )

        vegetables = st.multiselect("Welches Gemüse magst du gerne?", VEGETABLES)
        more_vegetables = st.text_input(
            "Dein Gemüse ist nicht dabei?",
            placeholder="Weitere Sorten mit Komma trennen",
        )

        free_note = st.text_area("Gibt es etwas, das Katharina noch wissen sollte?")

        submitted = st.form_submit_button("Anamnese abschließen", type="primary")

    if submitted:
        if not all([name.strip(), thermal, sleep, energy, breakfast_label]):
            st.error("Bitte beantworte noch Name, Thermik, Schlaf, Energie und Frühstücksvorliebe.")
            return

        pref_map = {
            "süß und weich/breiig": "suess",
            "pikant und mit Kauanteil": "pikant",
            "beides": "beides",
            "ich möchte ausprobieren": "ausprobieren",
        }
        extra = [item.strip() for item in more_vegetables.split(",") if item.strip()]

        C["name"] = name.strip()
        C["preferences"]["breakfast"] = pref_map[breakfast_label]
        C["preferences"]["vegetables"] = list(dict.fromkeys(vegetables + extra))
        C["anamnesis"] = {
            "concerns": concerns,
            "digestion": digestion,
            "body": body,
            "thermal": thermal,
            "sleep": sleep,
            "energy": energy,
            "food_habits": food_habits,
            "emotions": emotions,
            "free_note": free_note,
        }
        C["assessment"] = assess_anamnesis(C["anamnesis"])
        C["onboarding_complete"] = True
        C["approved"] = False
        st.session_state.view = "katharina"
        st.rerun()


def render_katharina_dashboard():
    st.title("Katharina-Dashboard 🪴")

    if not C.get("onboarding_complete"):
        st.info("Noch keine Anamnese abgeschlossen.")
        return

    assessment = C["assessment"]
    st.subheader(f"{client_name()} – vorläufiges Gesamtbild")
    st.caption("Interne Orientierung zur fachlichen Freigabe, keine Diagnose.")

    score_text = " · ".join(
        f"{name}: {value}"
        for name, value in assessment["ranked"]
        if value > 0
    )
    st.write("**Gewichtung:** " + (score_text or "noch nicht deutlich"))

    for name, value in assessment["ranked"]:
        if value <= 0:
            continue
        with st.expander(f"{name} – Gewicht {value}"):
            for reason in assessment["reasons"][name]:
                st.write("• " + reason)

    for warning in assessment["contradictions"]:
        st.warning(warning)

    st.subheader("Katharina-Blick – Prioritätsvorschlag")
    if assessment["relevant_heat"]:
        sequence = "Hitze kurzfristig berücksichtigen"
        if assessment["underlying"]:
            sequence += f" → {assessment['underlying']}"
        if assessment["underlying"] != "Mitte stärken" and assessment["scores"]["Mitte stärken"] > 0:
            sequence += " → Mitte stärken"
        st.warning(
            "Aktuelle Hitzehinweise: "
            + ", ".join(assessment["heat_signals"])
            + ". Hitze vorerst nicht weiter fördern."
        )
        st.write("**Vorgeschlagene Reihenfolge:** " + sequence + ".")
    else:
        top = [name for name, value in assessment["ranked"] if value > 0][:3]
        st.info("Vorrangig prüfen: " + " → ".join(top) if top else "Noch keine klare Richtung.")

    emotional = C["anamnesis"].get("emotions", [])
    if emotional:
        st.subheader("Emotionaler Gesamtblick")
        st.warning(
            "Selbstauskunft: " + " · ".join(emotional)
            + ". Als Kontext und möglichen persönlichen Begleitbedarf prüfen; nicht automatisch diagnostizieren."
        )

    directions = [
        "Hitze kurzfristig berücksichtigen, danach Grundmuster weiterführen",
        "Feuchtigkeit angehen + Mitte stärken",
        "Kälte berücksichtigen + Mitte stärken",
        "Mitte stärken und Verdauung beobachten",
        "Stagnation mit Ernährung, Bewegung und Entspannung begleiten",
        "Gesamtbild noch nicht freigeben",
    ]
    selected = st.selectbox(
        "Begleitrichtung",
        directions,
        index=directions.index(C["approved_direction"]) if C.get("approved_direction") in directions else 0,
    )
    note = st.text_area(
        "Katharinas Notiz",
        value=C.get("approval_note", ""),
        placeholder="Zum Beispiel: zwei Wochen Feuchtigkeit angehen, Kälte berücksichtigen, Hitze nicht weiter fördern.",
    )

    left, right = st.columns(2)
    with left:
        if st.button("Begleitung freigeben", type="primary", use_container_width=True):
            C["approved_direction"] = selected
            C["approval_note"] = note
            C["approved"] = True
            C["day"] = 1
            st.session_state.view = "client"
            st.rerun()
    with right:
        if st.button("Noch nicht freigeben", use_container_width=True):
            C["approved"] = False
            C["approved_direction"] = selected
            C["approval_note"] = note
            st.rerun()

    st.subheader("Verlauf")
    if not C["history"]:
        st.caption("Noch keine abgeschlossenen Tage.")
    else:
        for entry in reversed(C["history"]):
            st.markdown(
                f"**Tag {entry['day']}** · Morgen: {entry['morning_summary']} · "
                f"Frühstück: {entry['breakfast_feedback']} · Abend: {entry['evening_summary']}"
            )
            st.divider()


def morning_visit():
    st.title("🌸 Guten Morgen mit Katharina")
    st.markdown(
        f"""
        <div class="mm-card">
          <div class="mm-title">Guten Morgen, {client_name()} 🌿</div>
          <p>Schön, dass du wieder da bist.</p>
          <p>Heute nehmen wir uns zwei Minuten Zeit für dich.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sleep = st.radio(
        "Wie hast du heute geschlafen?",
        ["sehr gut", "gut", "unruhig", "oft aufgewacht", "morgens nicht erholt"],
        index=None,
        key=f"m_sleep_{C['day']}",
    )
    body = st.multiselect(
        "Wie fühlst du dich heute?",
        ["leicht", "voller Energie", "müde", "aufgebläht", "schwer", "unruhig", "ich friere", "mir ist warm"],
        key=f"m_body_{C['day']}",
    )
    hunger = st.radio(
        "Hast du heute Morgen Hunger?",
        ["ja", "ein bisschen", "nein"],
        index=None,
        key=f"m_hunger_{C['day']}",
    )
    concern = st.radio(
        "Gibt es heute etwas, das dich beschäftigt?",
        ["nein", "Stress", "Sorgen", "Traurigkeit", "Wut", "etwas anderes"],
        index=None,
        key=f"m_concern_{C['day']}",
    )

    extra = ""
    if concern == "etwas anderes":
        extra = st.text_input("Magst du es kurz beschreiben?", key=f"m_extra_{C['day']}")

    ready = bool(sleep and body and hunger and concern and (concern != "etwas anderes" or extra.strip()))
    if not ready:
        st.info("Beantworte bitte die vier kurzen Fragen. Danach erscheint dein heutiger Besuch.")
        return None

    answers = {
        "sleep": sleep,
        "body": body,
        "hunger": hunger,
        "concern": concern,
        "extra": extra,
    }
    C["morning"][C["day"]] = answers

    st.subheader("🌿 Warum heute diese Richtung?")
    reasons = []
    if "mir ist warm" in body:
        reasons.append("Heute zeigt dein Körper mehr Wärme. Wir fördern diese Tendenz nicht zusätzlich.")
    if "ich friere" in body:
        reasons.append("Heute darf dein Morgen sanft und angenehm warm beginnen.")
    if "aufgebläht" in body or "schwer" in body:
        reasons.append("Heute halten wir das Frühstück eher ruhig, gekocht und überschaubar.")
    if hunger == "nein":
        reasons.append("Da du wenig Hunger hast, wählen wir eine kleinere Portion.")
    if not reasons:
        reasons.append("Heute bleiben wir bei kleinen, gut verträglichen Schritten.")
    for reason in reasons:
        st.write(reason)

    st.subheader("🌸 Katharinas Tagesimpuls")
    if concern in {"Stress", "Sorgen", "Traurigkeit", "Wut"} or "unruhig" in body:
        st.info("Atme vor dem Frühstück ruhig aus und spüre beide Füße am Boden.")
    elif "ich friere" in body:
        st.info("Reibe deine Hände warm und lege sie kurz auf deinen unteren Rücken.")
    elif "aufgebläht" in body or "schwer" in body:
        st.info("Iss langsam und lege den Löffel zwischendurch einmal ab.")
    else:
        st.info("Ein kleiner bewusster Schritt reicht heute vollkommen.")

    st.markdown(
        """
        <div class="mm-soft">
          <strong>💚 Katharinas Gedanke</strong>
          <p>Du musst heute nicht perfekt sein. Kleine Schritte dürfen leicht sein.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return answers


def kitchen_idea():
    liked = C["preferences"].get("vegetables", [])
    if not liked:
        liked = ["Zucchini", "Karotte / Möhre", "Kürbis"]
    index = (C["day"] - 1) % len(liked)
    selected = [liked[index]]
    if len(liked) > 1:
        selected.append(liked[(index + 1) % len(liked)])

    st.subheader("🥕 Katharinas Mittagsidee")
    st.write(
        "Heute wünsche ich dir etwas Warmes und Einfaches. Das Gemüse darf nach deinem Geschmack ausgewählt werden."
    )
    st.write("**Heute kombinieren:** Reis · " + " und ".join(selected))

    st.markdown("**Gemüse im eigenen Saft:**")
    st.write("1. Gemüse klein schneiden und direkt in einen Topf mit gut schließendem Deckel geben.")
    st.write("2. Eine kleine Prise Himalayasalz dazugeben.")
    st.write("3. Je nach Begleitrichtung einige Butterflocken ergänzen oder bewusst weglassen.")
    st.write("4. Bei mittlerer bis eher sanfter Hitze 5–10 Minuten unter Beobachtung garen.")
    st.write("5. Deckel möglichst geschlossen lassen, damit der Dampf im Topf bleibt.")
    st.write("6. Mit Reis kombinieren; ein Ei kann passend zur individuellen Richtung ergänzt werden.")


def evening_check():
    st.title("🌙 Katharinas Abendblick")
    st.write("Schön, dass du heute noch einmal kurz da bist.")

    breakfast_feedback = st.radio(
        "Wie ist dir dein Frühstück bekommen?",
        ["sehr gut", "ganz okay", "nicht so gut", "körperlich deutlich ungünstig"],
        index=None,
        key=f"e_breakfast_{C['day']}",
    )
    digestion = st.radio(
        "Wie war deine Verdauung heute?",
        ["ruhig / unauffällig", "etwas aufgebläht", "schwer / träge", "weicher Stuhl", "trockener Stuhl", "sehr unterschiedlich"],
        index=None,
        key=f"e_digestion_{C['day']}",
    )
    energy = st.radio(
        "Wie war deine Energie heute?",
        ["stabil", "eher gut", "müde", "Einbruch nach dem Essen", "unruhig / angespannt"],
        index=None,
        key=f"e_energy_{C['day']}",
    )
    note = st.text_area(
        "Möchtest du Katharina noch etwas erzählen?",
        key=f"e_note_{C['day']}",
    )

    if st.button(
        "Tag abschließen",
        type="primary",
        use_container_width=True,
        disabled=not (breakfast_feedback and digestion and energy),
    ):
        C["evening"][C["day"]] = {
            "breakfast_feedback": breakfast_feedback,
            "digestion": digestion,
            "energy": energy,
            "note": note,
        }
        morning = C["morning"].get(C["day"], {})
        C["history"].append(
            {
                "day": C["day"],
                "morning_summary": f"{morning.get('sleep', '–')}, {', '.join(morning.get('body', []))}",
                "breakfast_feedback": breakfast_feedback,
                "evening_summary": f"Verdauung: {digestion}; Energie: {energy}",
            }
        )
        st.success("Danke 🌿 Morgen schauen wir gemeinsam weiter.")
        if C["day"] < 14:
            C["day"] += 1
        st.rerun()


def render_client_day():
    if not C.get("started"):
        render_welcome()
        return

    if not C.get("onboarding_complete"):
        render_anamnesis()
        return

    if not C.get("approved"):
        st.title(f"Danke, {client_name()} 🌿")
        st.write("Katharina prüft deine vorläufige Begleitrichtung.")
        st.info("Die 14-Tage-Begleitung startet nach der fachlichen Freigabe.")
        return

    st.caption(f"Tag {C['day']} von 14 · {C.get('approved_direction', '')}")

    tab_morning, tab_kitchen, tab_evening = st.tabs(
        ["🌞 Morgenbesuch", "🍲 Meine Mitte Küche", "🌙 Abendblick"]
    )

    with tab_morning:
        answers = morning_visit()
        if answers:
            recipe = select_breakfast()
            intro = (
                "Heute darf dein Frühstück ruhig, warm gekocht und gut überschaubar sein. "
                "Die Auswahl berücksichtigt deine Grundrichtung und deine Vorliebe."
            )
            render_recipe(recipe, intro)

    with tab_kitchen:
        kitchen_idea()

    with tab_evening:
        evening_check()

    st.divider()
    if st.button("Demo vollständig zurücksetzen"):
        reset_demo()


render_navigation()

if st.session_state.view == "katharina":
    render_katharina_dashboard()
else:
    render_client_day()
