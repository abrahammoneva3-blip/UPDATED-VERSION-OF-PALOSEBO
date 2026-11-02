"""Static game data: characters, cosmetics, flags, bamboo designs, stages."""
from settings import *

# --------------------------------------------------------------------------
# Characters (cosmetic only - every character plays exactly the same)
# --------------------------------------------------------------------------
CHARACTERS = [
    dict(id="kid", name="FIESTA KID", price=0, skin=(222, 160, 104), hair=(30, 22, 30), hair_style="spiky",
         shirt_style="tee", shirt=YELLOW, shirt2=RED, pants=BLUE, pants_style="shorts", hat="none", acc="none"),
    dict(id="student", name="STUDENT", price=0, skin=(238, 188, 130), hair=(28, 24, 40), hair_style="side",
         shirt_style="polo", shirt=(246, 246, 250), shirt2=RED, pants=DKBLUE, pants_style="long", hat="none", acc="none"),
    dict(id="farmer", name="FARMER", price=0, skin=(190, 126, 76), hair=(40, 26, 24), hair_style="short",
         shirt_style="tank", shirt=(200, 170, 110), shirt2=BROWN, pants=(120, 96, 60), pants_style="long", hat="salakot", acc="none"),
    dict(id="fisher", name="FISHERMAN", price=180, skin=(176, 112, 70), hair=(24, 20, 28), hair_style="short",
         shirt_style="stripes", shirt=TEAL, shirt2=WHITE, pants=(240, 232, 210), pants_style="shorts", hat="bandana", acc="none"),
    dict(id="athlete", name="BRGY ATHLETE", price=240, skin=(214, 150, 96), hair=(36, 24, 24), hair_style="short",
         shirt_style="jersey", shirt=RED, shirt2=WHITE, pants=(250, 250, 250), pants_style="shorts", hat="headband", acc="wristbands"),
    dict(id="champ", name="FIESTA CHAMP", price=400, skin=(228, 170, 112), hair=(20, 16, 24), hair_style="slick",
         shirt_style="barong", shirt=(250, 236, 196), shirt2=GOLD, pants=(50, 40, 70), pants_style="long", hat="none", acc="sash"),
]

HATS = [
    dict(id="none", name="NO HAT", price=0, kind="none"),
    dict(id="cap", name="FIESTA CAP", price=0, kind="cap", color=RED),
    dict(id="headband", name="PULA HEADBAND", price=50, kind="headband", color=RED),
    dict(id="bandana", name="BLUE BANDANA", price=70, kind="bandana", color=BLUE),
    dict(id="buri", name="BURI HAT", price=90, kind="buri", color=STRAW),
    dict(id="salakot", name="SALAKOT", price=110, kind="salakot", color=STRAW),
    dict(id="sampaguita", name="SAMPAGUITA", price=140, kind="crown", color=WHITE),
]

OUTFITS = [
    dict(id="pula", name="PULA SHIRT", price=0, shirt=RED, shirt2=YELLOW),
    dict(id="bughaw", name="BUGHAW SHIRT", price=80, shirt=BLUE, shirt2=WHITE),
    dict(id="dilaw", name="DILAW SHIRT", price=80, shirt=YELLOW, shirt2=RED),
    dict(id="berde", name="BERDE SHIRT", price=100, shirt=GREEN, shirt2=YELLOW),
    dict(id="lila", name="UBE SHIRT", price=120, shirt=PURPLE, shirt2=PINK),
    dict(id="rosas", name="ROSAS SHIRT", price=120, shirt=PINK, shirt2=WHITE),
    dict(id="barong", name="BARONG TAGALOG", price=220, shirt=(250, 236, 196), shirt2=GOLD, style="barong"),
]

ACCESSORIES = [
    dict(id="none", name="NO ACCESSORY", price=0),
    dict(id="wristbands", name="WRISTBANDS", price=70),
    dict(id="shades", name="SHADES", price=90),
    dict(id="lei", name="SAMPAGUITA LEI", price=120),
    dict(id="sash", name="FIESTA SASH", price=150),
]

FLAGS = [
    dict(id="araw", name="ARAW NG PISTA", price=0),
    dict(id="banderitas", name="BANDERITAS", price=150),
    dict(id="inabel", name="INABEL WEAVE", price=200),
    dict(id="bituin", name="BITUIN", price=200),
    dict(id="pabalat", name="PABALAT CUT-PAPER", price=250),
]

BAMBOOS = [
    dict(id="berde", name="BERDENG KAWAYAN", price=0, color=(74, 170, 64)),
    dict(id="ginto", name="GINTONG KAWAYAN", price=200, color=(226, 176, 44)),
    dict(id="guhit", name="PISTA STRIPES", price=250, color=(214, 60, 60)),
    dict(id="laso", name="LASO NG PISTA", price=300, color=(74, 170, 64)),
]

SKIES = [
    dict(id="stage", name="STAGE DEFAULT", price=0),
    dict(id="sunset", name="GINTONG DAPITHAPON", price=300),
    dict(id="night", name="GABI NG PISTA", price=350),
]

CATEGORIES = [
    ("CHARACTERS", "characters", CHARACTERS),
    ("HATS", "hats", HATS),
    ("OUTFITS", "outfits", OUTFITS),
    ("ACCESSORIES", "accessories", ACCESSORIES),
    ("FLAGS", "flags", FLAGS),
    ("BAMBOO", "bamboo", BAMBOOS),
    ("SKIES", "skies", SKIES),
]

# --------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------
STAGES = [
    dict(id=1, name="BARANGAY FIESTA", tagline="BAHAY KUBO AT BANDERITAS", sway=1.0, events=1.0, wind_bias=1.0, crowd=26),
    dict(id=2, name="PROVINCIAL FIESTA", tagline="SIMBAHAN AT PLAZA", sway=1.12, events=1.0, wind_bias=1.0, crowd=30),
    dict(id=3, name="BEACH FIESTA", tagline="DAGAT AT DAPITHAPON", sway=1.25, events=1.1, wind_bias=1.3, crowd=32),
    dict(id=4, name="MOUNTAIN FIESTA", tagline="BULKAN AT PALAYAN", sway=1.4, events=1.15, wind_bias=1.5, crowd=30),
    dict(id=5, name="GRAND FIESTA", tagline="ANG PINAKAMALAKING PISTA!", sway=1.5, events=1.25, wind_bias=1.2, crowd=44),
]

DEFAULT_LOADOUT_P1 = dict(character="kid", hat="default", outfit="default", accessory="default")
DEFAULT_LOADOUT_P2 = dict(character="student", hat="default", outfit="default", accessory="default")


def by_id(items, item_id):
    for it in items:
        if it["id"] == item_id:
            return it
    return items[0]
