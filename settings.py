"""Global constants for PALOSEBO: FIESTA CLIMB."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAVE_PATH = os.path.join(DATA_DIR, "save.json")

GAME_TITLE = "PALOSEBO: FIESTA CLIMB"

# Internal pixel-art resolution (scaled up with nearest-neighbour).
W, H = 384, 216
FPS = 60

# --- World layout -----------------------------------------------------------
GROUND_Y = 176          # screen y of the ground line when the camera is at 0
POLE_H = 640            # height of a bamboo pole (world units == pixels)
TOP_H = 620             # feet height at which a climber grabs the flag
POLE_X_LEFT = 122       # PLAYER 2 pole
POLE_X_RIGHT = 262      # PLAYER 1 pole
POLE_X_CENTER = 192     # single pole (time attack / practice)
MAX_CAM = POLE_H - 106     # highest camera position (flag stays visible below the HUD)

# --- Climbing tuning --------------------------------------------------------
CLIMB_SPEED = 50.0      # px / s at full stamina
DOWN_SPEED = 62.0
GREASE_SLIDE = 4.0      # the pole is greased ("sebo"): resting slides you down a bit
STAMINA_MAX = 100.0
STAMINA_LOW = 40.0      # below this the climber slows down
STAMINA_MIN_FACTOR = 0.20
STAMINA_DRAIN = 11.0    # per second at full effort
STAMINA_REST = 24.0     # per second when idle
STAMINA_REST_DOWN = 16.0
STAMINA_SLOW_RECOVER = 6.0  # recovery while creeping along when tired

BAL_CONTROL = 4.2       # acceleration from player's balance keys
BAL_SPRING = 0.6        # passive pull to centre
BAL_DAMP = 2.4
BAL_DANGER = 0.70
BAL_EDGE_GRACE = 0.30   # seconds at the very edge before slipping (forgiving)
SLIP_TIME = 0.75
SLIP_DIST = 38.0

FAST_TIME = 24.0        # "FAST CLIMB" bonus threshold (seconds)
COIN_WIN = 100
COIN_FAST = 25
COIN_PERFECT = 25
COIN_TIME_ATTACK = 50

# --- Palette (16/32-bit inspired) -------------------------------------------
OUTLINE = (34, 20, 40)
BLACK = (16, 12, 28)
NIGHT = (26, 28, 56)
WHITE = (255, 255, 255)
CREAM = (255, 244, 214)
RED = (214, 40, 57)
DKRED = (140, 24, 48)
ORANGE = (248, 138, 42)
YELLOW = (255, 208, 52)
GOLD = (232, 164, 28)
LIME = (132, 206, 64)
GREEN = (46, 150, 70)
DKGREEN = (24, 94, 60)
TEAL = (30, 170, 170)
SKY = (96, 184, 240)
LTBLUE = (170, 220, 250)
BLUE = (48, 96, 200)
DKBLUE = (28, 44, 110)
PURPLE = (130, 60, 170)
PINK = (255, 120, 170)
BROWN = (130, 80, 44)
DKBROWN = (78, 46, 36)
TAN = (212, 150, 90)
SAND = (238, 208, 140)
STRAW = (232, 196, 110)
GRAY = (140, 140, 160)
DKGRAY = (70, 70, 90)
LTGRAY = (200, 200, 216)

FIESTA_COLORS = [RED, YELLOW, BLUE, GREEN, ORANGE, PINK, TEAL, PURPLE, WHITE]
