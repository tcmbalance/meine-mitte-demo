
import streamlit as st
from datetime import date

st.set_page_config(page_title="Meine Mitte V11", page_icon="🌿", layout="centered")

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
C.setdefault("kitchen_dislikes", [])
C.setdefault("kitchen_missing", [])
C.setdefault("kitchen_variant", 0)
C.setdefault("liked_vegetables", [])
C.setdefault("onboarding_complete", False)
C.setdefault("anamnesis", {})
C.setdefault("provisional_assessment", {})
C.setdefault("approved_direction", None)
C.setdefault("approval_note", "")


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
FOOD_MATRIX = {
    # temperature = TCM-Grunddaten/Arbeitsdaten.
    # practice_rules = Katharinas Begleitlogik, bewusst getrennt von der TCM-Temperatur.
    "Buchweizen": {
        "group": "Getreide", "temperature": "neutral",
        "practice_rules": [],
        "source_note": "Lebensmittelliste / fachlicher Abgleich",
    },
    "Hafer": {
        "group": "Getreide", "temperature": "neutral",
        "practice_rules": ["bei aktuellem Hitze-/Schwitzhinweis nicht priorisieren"],
        "source_note": "TCM-Grundtemperatur neutral; Katharina-Praxisregel separat",
    },
    "Haferdrink": {
        "group": "Getränk/Pflanzendrink", "temperature": "nicht automatisch vom Hafer ableiten",
        "practice_rules": ["bei aktuellem Hitze-/Schwitzhinweis nicht priorisieren"],
        "source_note": "Katharina-Praxisregel",
    },
    "Reis": {
        "group": "Getreide", "temperature": "Arbeitsmatrix",
        "practice_rules": [],
        "source_note": "Unterlagen",
    },
    "Hirse": {
        "group": "Getreide", "temperature": "Arbeitsmatrix",
        "practice_rules": [],
        "source_note": "Unterlagen",
    },
    "Polenta": {
        "group": "Getreide", "temperature": "Arbeitsmatrix",
        "practice_rules": [],
        "source_note": "Unterlagen",
    },
    "Ingwer": {
        "group": "Gewürz", "temperature": "thermisch relevant",
        "practice_rules": ["bei aktuellem Hitze-/Schwitzhinweis nicht automatisch empfehlen"],
        "source_note": "Katharina-Praxisregel / Unterlagen",
    },
    "Zimt": {
        "group": "Gewürz", "temperature": "thermisch relevant",
        "practice_rules": ["bei aktuellem Hitze-/Schwitzhinweis nicht automatisch empfehlen"],
        "source_note": "Katharina-Praxisregel / Unterlagen",
    },
}

def katharina_heat_blocked(ingredient):
    data = FOOD_MATRIX.get(ingredient, {})
    return "bei aktuellem Hitze-/Schwitzhinweis nicht priorisieren" in data.get("practice_rules", []) or            "bei aktuellem Hitze-/Schwitzhinweis nicht automatisch empfehlen" in data.get("practice_rules", [])


def recipe_is_allowed(recipe, filters):
    if "HITZEFILTER" in filters:
        for ingredient in recipe["ingredients"]:
            if katharina_heat_blocked(ingredient):
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


KITCHEN_COMPONENTS = {
    "bases": [
        {"name": "Reis", "ingredients": {"Reis"}, "tags": {"neutral", "mild"}},
        {"name": "Hirse", "ingredients": {"Hirse"}, "tags": {"warm", "mild"}},
        {"name": "Polenta", "ingredients": {"Polenta"}, "tags": {"mild"}},
        {"name": "Buchweizen", "ingredients": {"Buchweizen"}, "tags": {"neutral"}},
    ],
    "vegetables": [
        {"name": "Zucchini", "ingredients": {"Zucchini"}, "tags": {"mild"}},
        {"name": "Karotte", "ingredients": {"Karotte"}, "tags": {"mild"}},
        {"name": "Fenchel", "ingredients": {"Fenchel"}, "tags": {"aromatisch"}},
        {"name": "Kürbis", "ingredients": {"Kürbis"}, "tags": {"mild"}},
        {"name": "Kohlrabi", "ingredients": {"Kohlrabi"}, "tags": {"mild"}},
    ],
    "extras": [
        {"name": "Ei", "ingredients": {"Ei"}, "tags": {"protein"}},
        {"name": "ein paar Butterflocken", "ingredients": {"Butter"}, "tags": {"fett"}},
        {"name": "ohne zusätzliche Ergänzung", "ingredients": set(), "tags": {"leicht"}},
    ],
}

def component_allowed(component, filters):
    ingredients = component["ingredients"]
    if "HITZEFILTER" in filters:
        if ingredients & {"Hafer", "Haferdrink", "Ingwer", "Zimt", "stark wärmende Gewürze", "erhitzende Getränke"}:
            return False
    return True

def choose_component(group, filters, blocked, offset=0):
    allowed = [
        item for item in KITCHEN_COMPONENTS[group]
        if component_allowed(item, filters) and item["name"] not in blocked
    ]
    if not allowed:
        return None
    return allowed[offset % len(allowed)]

def build_kitchen_idea(filters, variant=0, dislikes=None, missing=None, evening=False):
    blocked = set(dislikes or []) | set(missing or [])
    base = choose_component("bases", filters, blocked, variant)
    # Katharina-Regel: sanft gegartes Gemüse wird primär nach Geschmack
    # und individueller Verträglichkeit gewählt. Ein allgemeiner Hitzehinweis
    # filtert hier nicht automatisch einzelne Gemüsesorten heraus.
    vegetable_pool = KITCHEN_COMPONENTS["vegetables"]
    liked = set(C.get("liked_vegetables", []))
    if liked:
        vegetable_pool = [v for v in vegetable_pool if v["name"] in liked]

    allowed_veg = [v for v in vegetable_pool if v["name"] not in blocked]
    veg1 = allowed_veg[variant % len(allowed_veg)] if allowed_veg else None
    remaining_veg = [v for v in allowed_veg if not veg1 or v["name"] != veg1["name"]]
    veg2 = remaining_veg[(variant + 1) % len(remaining_veg)] if remaining_veg else None
    extra = choose_component("extras", filters, blocked, variant)

    if evening:
        # Katharina-Grundrichtung: abends leichter; Ei nicht automatisch priorisieren.
        light = [x for x in KITCHEN_COMPONENTS["extras"] if x["name"] == "ohne zusätzliche Ergänzung"]
        extra = light[0]

    if not base or not veg1:
        return None

    veg_names = [veg1["name"]]
    if veg2:
        veg_names.append(veg2["name"])

    return {
        "base": base["name"],
        "vegetables": veg_names,
        "extra": extra["name"] if extra else "ohne zusätzliche Ergänzung",
        "evening": evening,
    }

def kitchen_card(idea, title="Katharinas Küchenbaukasten"):
    if not idea:
        st.warning("Für die aktuellen Filter ist in dieser Demo noch keine passende Kombination hinterlegt.")
        return

    veg_text = " und ".join(idea["vegetables"])
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(title)
    st.write(f"**Heute kombinieren wir:** {idea['base']} · {veg_text} · {idea['extra']}")

    st.markdown("**So bereitest du das Gemüse zu:**")
    st.write("1. Gemüse klein schneiden und direkt in einen Topf mit gut schließendem Deckel geben.")
    st.write("2. Eine kleine Prise Himalayasalz dazugeben.")
    if idea["extra"] == "ein paar Butterflocken":
        st.write("3. Ein paar Butterflocken dazugeben.")
    else:
        st.write("3. Heute keine Butterflocken ergänzen.")
    st.write("4. Deckel schließen und bei mittlerer bis eher sanfter Hitze etwa 5–10 Minuten unter Beobachtung im eigenen Saft garen.")
    st.write("5. Den Deckel möglichst geschlossen lassen, damit Dampf und Feuchtigkeit im Topf bleiben.")
    st.write("6. Das Gemüse soll angenehm gegart, aber nicht zerkocht sein.")

    st.markdown("**Dann kombinieren:**")
    if idea["evening"]:
        st.write(f"Das Gemüse mit einer kleinen Portion {idea['base']} kombinieren oder bei spätem Abendessen noch leichter halten.")
    else:
        st.write(f"Das Gemüse mit {idea['base']} kombinieren.")
    if idea["extra"] == "Ei":
        st.write("Das Ei zum Schluss untermengen oder separat weich garen und dazugeben.")
    elif idea["extra"] == "ein paar Butterflocken":
        st.write("Die Butterflocken beim Garen mit dem Gemüse verwenden.")
    else:
        st.write("Heute bleibt die Kombination bewusst schlicht und leicht.")

    st.caption("Die konkrete Kombination wird erst nach den aktuell aktiven Filtern ausgewählt.")
    st.markdown('</div>', unsafe_allow_html=True)



def score_anamnesis(a):
    scores = {
        "Feuchtigkeit": 0,
        "Hitzehinweise": 0,
        "Kältehinweise": 0,
        "Mitte stärken": 0,
        "Stagnationshinweise": 0,
    }
    reasons = {k: [] for k in scores}

    def add(key, points, reason):
        scores[key] += points
        reasons[key].append(reason)

    for item in a.get("digestion", []):
        if item in {"Völlegefühl / Druck", "Blähungen", "Schwere nach dem Essen"}:
            add("Feuchtigkeit", 2, item)
            add("Mitte stärken", 2, item)
        if item in {"weicher Stuhl / Durchfall", "unverdautes im Stuhl"}:
            add("Mitte stärken", 2, item)
            add("Feuchtigkeit", 1, item)
        if item == "trockener / schwieriger Stuhl":
            add("Hitzehinweise", 1, item)

    for item in a.get("body", []):
        if item in {"Schwere / Trägheit", "geschwollene Hände / Beine", "viel Schleim"}:
            add("Feuchtigkeit", 2, item)
        if item in {"Hitzegefühl", "starkes Schwitzen", "innere Unruhe mit Wärme"}:
            add("Hitzehinweise", 2, item)
        if item in {"kalte Hände / Füße", "Frieren", "Wärme tut gut"}:
            add("Kältehinweise", 2, item)
            add("Mitte stärken", 1, item)

    for item in a.get("food_habits", []):
        if item in {"viel Brot / Gebäck", "viel Käse", "häufig Joghurt / kalte Milchprodukte", "häufig Süßigkeiten"}:
            add("Feuchtigkeit", 2, item)
            add("Mitte stärken", 1, item)
        if item in {"viel Rohkost", "häufig kalte Speisen / Getränke"}:
            add("Kältehinweise", 1, item)
            add("Mitte stärken", 1, item)

    for item in a.get("stagnation", []):
        if item in {"häufig angespannt", "Gefühl von innerem Stau", "seufze oft", "Bewegung tut mir gut", "gereizt / schnell genervt"}:
            add("Stagnationshinweise", 2, item)

    if a.get("sleep") in {"unruhig", "häufiges Erwachen"}:
        add("Stagnationshinweise", 1, f"Schlaf: {a.get('sleep')}")
    if a.get("energy") in {"müde / schwer", "Einbruch nach dem Essen"}:
        add("Mitte stärken", 2, f"Energie: {a.get('energy')}")
        add("Feuchtigkeit", 1, f"Energie: {a.get('energy')}")
    if a.get("thermal") == "eher heiß / viel Schwitzen":
        add("Hitzehinweise", 3, "thermisches Empfinden")
    elif a.get("thermal") == "eher kalt / friere leicht":
        add("Kältehinweise", 3, "thermisches Empfinden")

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    contradictions = []
    if scores["Hitzehinweise"] >= 2 and scores["Kältehinweise"] >= 2:
        contradictions.append("Es zeigen sich gleichzeitig Hitze- und Kältehinweise. Thermik nicht vereinfachen; Verlauf und Kontext prüfen.")
    if scores["Feuchtigkeit"] >= 4 and scores["Stagnationshinweise"] >= 3:
        contradictions.append("Feuchtigkeits- und Stagnationshinweise treten gemeinsam auf. Ernährung nicht als einzigen Begleitbaustein behandeln.")

    return {
        "scores": scores,
        "reasons": reasons,
        "ranked": ranked,
        "contradictions": contradictions,
    }

def client_anamnesis():
    st.title("Willkommen bei Meine Mitte 🌿")
    st.write(
        "Bevor deine Begleitung startet, möchte ich ein erstes Bild von deinem Alltag und deinem Körpergefühl bekommen. "
        "Es geht nicht darum, etwas perfekt zu beantworten."
    )
    st.caption("V11 ist eine Demo. Bitte hier noch keine echten Gesundheitsdaten von Klientinnen eingeben.")

    with st.form("anamnesis_form"):
        name = st.text_input("Wie darf ich dich ansprechen?", value=C.get("name", "Maria"))

        breakfast_pref = st.radio(
            "Wie magst du dein Frühstück grundsätzlich lieber?",
            ["süß und weich/breiig", "pikant und mit Kauanteil", "beides", "ich möchte ausprobieren"],
            index=None,
        )

        digestion = st.multiselect("Was kennst du von deiner Verdauung?", [
            "Völlegefühl / Druck", "Blähungen", "Schwere nach dem Essen",
            "weicher Stuhl / Durchfall", "unverdautes im Stuhl",
            "trockener / schwieriger Stuhl", "nichts davon"
        ])

        body = st.multiselect("Was fällt dir körperlich häufiger auf?", [
            "Schwere / Trägheit", "geschwollene Hände / Beine", "viel Schleim",
            "Hitzegefühl", "starkes Schwitzen", "innere Unruhe mit Wärme",
            "kalte Hände / Füße", "Frieren", "Wärme tut gut", "nichts davon"
        ])

        food_habits = st.multiselect("Was gehört derzeit häufig zu deinem Alltag?", [
            "viel Brot / Gebäck", "viel Käse", "häufig Joghurt / kalte Milchprodukte",
            "häufig Süßigkeiten", "viel Rohkost", "häufig kalte Speisen / Getränke",
            "überwiegend warm und gekocht"
        ])

        thermal = st.radio("Wie erlebst du dich thermisch meistens?", [
            "eher kalt / friere leicht", "ausgeglichen", "eher heiß / viel Schwitzen", "wechselt stark"
        ], index=None)

        sleep = st.radio("Wie ist dein Schlaf meistens?", [
            "ruhig", "unruhig", "häufiges Erwachen", "sehr unterschiedlich"
        ], index=None)

        energy = st.radio("Wie ist deine Energie im Alltag?", [
            "stabil", "müde / schwer", "Einbruch nach dem Essen", "unruhig / schwer abzuschalten", "wechselhaft"
        ], index=None)

        stagnation = st.multiselect("Was beschreibt dich im Moment?", [
            "häufig angespannt", "Gefühl von innerem Stau", "seufze oft",
            "Bewegung tut mir gut", "gereizt / schnell genervt", "nichts davon"
        ])

        liked_veg = st.multiselect(
            "Welches Gemüse magst du gerne?",
            [v["name"] for v in KITCHEN_COMPONENTS["vegetables"]]
        )

        free_note = st.text_area("Gibt es noch etwas, das Katharina wissen sollte?")

        submitted = st.form_submit_button("Anamnese abschließen", type="primary")

    if submitted:
        required = all([name, breakfast_pref, thermal, sleep, energy])
        if not required:
            st.error("Bitte beantworte noch die Grundfragen zu Frühstück, Thermik, Schlaf und Energie.")
            return

        pref_map = {
            "süß und weich/breiig": "suess",
            "pikant und mit Kauanteil": "pikant",
            "beides": "beides",
            "ich möchte ausprobieren": "ausprobieren",
        }
        C["name"] = name
        C["breakfast_preference"] = pref_map[breakfast_pref]
        C["liked_vegetables"] = liked_veg
        C["anamnesis"] = {
            "digestion": digestion, "body": body, "food_habits": food_habits,
            "thermal": thermal, "sleep": sleep, "energy": energy,
            "stagnation": stagnation, "free_note": free_note,
        }
        C["provisional_assessment"] = score_anamnesis(C["anamnesis"])
        C["onboarding_complete"] = True
        C["approved"] = False
        C["approved_direction"] = None
        st.success("Danke 🌿 Deine Angaben sind gespeichert. Katharina prüft jetzt die vorläufige Begleitrichtung.")
        st.rerun()


def katharina():
    st.title("Katharina-Dashboard 🪴")

    if not C.get("onboarding_complete"):
        st.info("Die Demo-Anamnese wurde noch nicht abgeschlossen.")
        st.write("Wechsle zu **🌿 Klientin**, fülle die Anamnese aus und komm danach zurück.")
        return

    a = C.get("anamnesis", {})
    assessment = C.get("provisional_assessment", {})
    scores = assessment.get("scores", {})
    ranked = assessment.get("ranked", [])

    st.subheader(f"{C['name']} – vorläufiges Gesamtbild")
    st.caption("Systemgewichtung zur fachlichen Prüfung – keine endgültige Diagnose.")

    if ranked:
        top_text = " · ".join([f"{name}: {score}" for name, score in ranked if score > 0])
        st.write("**Gewichtung:** " + (top_text or "noch keine deutliche Gewichtung"))

    for key, score in ranked:
        if score <= 0:
            continue
        with st.expander(f"{key} – Gewicht {score}"):
            for reason in assessment.get("reasons", {}).get(key, []):
                st.write("• " + reason)

    if assessment.get("contradictions"):
        st.subheader("Widersprüche / gemeinsam auftretende Hinweise")
        for item in assessment["contradictions"]:
            st.warning(item)

    st.subheader("Systemvorschlag für Katharina")
    top_names = [name for name, score in ranked if score > 0][:3]
    if top_names:
        st.info(
            "Vorrangig prüfen: " + " → ".join(top_names) + ". "
            "Die Reihenfolge ist eine vorläufige Gewichtung aus der Demo-Anamnese und muss von Katharina fachlich freigegeben oder korrigiert werden."
        )
    else:
        st.info("Aus der Demo-Anamnese ergibt sich noch keine klare Gewichtung.")

    st.write("**Freie Angabe der Klientin:** " + (a.get("free_note") or "keine"))

    st.subheader("Katharinas Entscheidung")
    direction_options = [
        "Feuchtigkeit angehen + Mitte stärken",
        "Hitzehinweise zuerst berücksichtigen",
        "Kälte berücksichtigen + Mitte stärken",
        "Mitte stärken und Verdauung beobachten",
        "Stagnationshinweise mit Bewegung/Entspannung begleiten",
        "Gesamtbild noch nicht freigeben",
    ]
    selected_direction = st.selectbox(
        "Begleitrichtung",
        direction_options,
        index=direction_options.index(C["approved_direction"]) if C.get("approved_direction") in direction_options else 0,
    )
    note = st.text_area(
        "Katharinas Notiz / Korrektur",
        value=C.get("approval_note", ""),
        placeholder="Zum Beispiel: Feuchtigkeit für 2 Wochen vorrangig angehen, Kälte berücksichtigen, Hitze nicht weiter fördern ..."
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Begleitrichtung freigeben", type="primary", use_container_width=True):
            C["approved_direction"] = selected_direction
            C["approval_note"] = note
            C["approved"] = True
            C["day"] = 1
            st.success("Freigegeben 🌿 Die Klientinnen-Begleitung kann starten.")
            st.rerun()
    with c2:
        if st.button("Noch nicht freigeben", use_container_width=True):
            C["approved_direction"] = "Gesamtbild noch nicht freigeben"
            C["approval_note"] = note
            C["approved"] = False
            st.info("Die tägliche Begleitung bleibt angehalten.")
            st.rerun()

    if C.get("approved"):
        st.success(f"**Freigegebene Richtung:** {C.get('approved_direction')}")
        if C.get("approval_note"):
            st.write("**Katharinas Notiz:** " + C["approval_note"])

    if C.get("history"):
        last = C["history"][-1]
        st.subheader("Was ist seit dem letzten Check-in passiert?")
        reaction_text = ", ".join(last.get("reaction", [])) if last.get("reaction") else "keine besondere Reaktion gemeldet"
        st.write(f"**Tag {last['day']}** · Schlaf: {last['sleep']} · Körper: {last['body']} · Frühstück: {last['food']}")
        st.write("**Reaktion:** " + reaction_text)

    if C.get("open_review"):
        st.subheader("🌿 Offener Katharina-Blick")
        review = C["open_review"]
        st.warning(
            f"Seit Tag {review['since']}: wiederholt körperlich ungünstige Rückmeldungen. "
            f"Aktuell genannt: {', '.join(review['reactions']) or 'keine Details'}."
        )
        d1, d2, d3 = st.columns(3)
        with d1:
            if st.button("Richtung beibehalten", use_container_width=True):
                C["decision"] = "Richtung beibehalten"
                C["open_review"] = None
                C["breakfast_status"] = "pause"
                st.rerun()
        with d2:
            if st.button("Rezept anpassen", use_container_width=True):
                C["decision"] = "Rezept anpassen"
                C["open_review"] = None
                C["breakfast_status"] = "question_first"
                st.rerun()
        with d3:
            if st.button("Schwerpunkt neu prüfen", use_container_width=True):
                C["decision"] = "Schwerpunkt neu prüfen"
                C["open_review"] = None
                C["breakfast_status"] = "hold"
                C["approved"] = False
                st.rerun()

    st.subheader("Küchenbaukasten – persönliche Faktoren")
    if C.get("liked_vegetables"):
        st.write("**Mag gerne:** " + " · ".join(C["liked_vegetables"]))
    if C.get("kitchen_dislikes"):
        st.write("**Mag derzeit nicht:** " + " · ".join(C["kitchen_dislikes"]))
    if C.get("kitchen_missing"):
        st.write("**Als nicht vorhanden markiert:** " + " · ".join(C["kitchen_missing"]))

    st.subheader("Verlauf")
    if not C.get("history"):
        st.caption("Noch keine Tagesrückmeldungen.")
    else:
        for h in reversed(C["history"]):
            st.markdown(f"**Tag {h['day']}** – Schlaf: {h['sleep']} · Körper: {h['body']} · Frühstück: {h['food']}")
            if h.get("reaction"):
                st.write("Reaktion:", ", ".join(h["reaction"]))
            st.divider()

def maria():
    if not C.get("onboarding_complete"):
        client_anamnesis()
        return

    if not C.get("approved"):
        st.title(f"Danke, {C['name']} 🌿")
        st.write("Deine Anamnese ist abgeschlossen. Katharina prüft jetzt deine vorläufige Begleitrichtung.")
        st.info("In dieser Demo wechselst du jetzt in das Katharina-Dashboard und gibst die Richtung dort fachlich frei.")
        return

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

    st.divider()
    st.subheader("Deine warme Gemüseidee heute")
    st.write("Du kannst Gemüse im Dampfgarer zubereiten oder sanft im eigenen Saft garen.")
    st.write("Beim sanft gegarten Gemüse steht hier zuerst im Vordergrund, was dir schmeckt und was du gut verträgst.")

    all_veg_names = [v["name"] for v in KITCHEN_COMPONENTS["vegetables"]]
    liked_veg = st.multiselect(
        "Welches Gemüse magst du gerne?",
        all_veg_names,
        default=C.get("liked_vegetables", []),
        key="liked_vegetables_selector"
    )
    C["liked_vegetables"] = liked_veg

    idea = build_kitchen_idea(
        filters=filters,
        variant=C.get("kitchen_variant", 0),
        dislikes=C.get("kitchen_dislikes", []),
        missing=C.get("kitchen_missing", []),
        evening=False,
    )
    kitchen_card(idea, "Gemüse im eigenen Saft – deine heutige Kombination")

    kitchen_feedback = st.radio(
        "Passt diese Kombination heute für dich?",
        ["Ja, passt", "Das mag ich nicht", "Das habe ich nicht zu Hause", "Heute lieber eine andere Kombination"],
        index=None,
        key=f"kitchen_feedback_{C['day']}_{C.get('kitchen_variant', 0)}"
    )

    if kitchen_feedback == "Das mag ich nicht" and idea:
        disliked = st.multiselect(
            "Was davon magst du nicht?",
            [idea["base"]] + idea["vegetables"] + [idea["extra"]],
            key=f"dislike_{C['day']}_{C.get('kitchen_variant', 0)}"
        )
        if disliked and st.button("Andere passende Kombination suchen", key=f"dislike_btn_{C['day']}_{C.get('kitchen_variant', 0)}"):
            C["kitchen_dislikes"] = sorted(set(C["kitchen_dislikes"]) | set(disliked))
            C["kitchen_variant"] += 1
            st.rerun()

    elif kitchen_feedback == "Das habe ich nicht zu Hause" and idea:
        missing = st.multiselect(
            "Was fehlt dir?",
            [idea["base"]] + idea["vegetables"] + [idea["extra"]],
            key=f"missing_{C['day']}_{C.get('kitchen_variant', 0)}"
        )
        if missing and st.button("Mit vorhandenen Alternativen neu zusammenstellen", key=f"missing_btn_{C['day']}_{C.get('kitchen_variant', 0)}"):
            C["kitchen_missing"] = sorted(set(C["kitchen_missing"]) | set(missing))
            C["kitchen_variant"] += 1
            st.rerun()

    elif kitchen_feedback == "Heute lieber eine andere Kombination":
        if st.button("Neue Kombination anzeigen", key=f"variant_btn_{C['day']}_{C.get('kitchen_variant', 0)}"):
            C["kitchen_variant"] += 1
            st.rerun()

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
