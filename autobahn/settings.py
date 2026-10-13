"""Spielkonstanten."""

from pathlib import Path

# Bildschirm (passt auch auf Laptops mit 1366×768)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Autobahnspiel"

# Strasse
LANE_COUNT = 6
LANE_WIDTH = SCREEN_WIDTH // LANE_COUNT

# Grössen der Sprites (Seitenverhältnis der Bilder beibehalten)
PLAYER_SIZE = (70, 127)
ENEMY_SIZE = (70, 130)
COIN_SIZE = (40, 40)
PLAYER_SPEED = 8

# Levels: Geschwindigkeit der Gegner und Frames zwischen zwei neuen Gegnern
LEVELS = [
    {"car_speed": 5, "car_frequency": 50},   # Level 1
    {"car_speed": 7, "car_frequency": 40},   # Level 2
    {"car_speed": 9, "car_frequency": 30},   # Level 3
    {"car_speed": 11, "car_frequency": 20},  # Level 4
]
LEVEL_DURATION = 60  # Sekunden pro Level

# Punkte und Leben
COIN_INTERVAL = 5 * FPS  # alle 5 Sekunden eine Münze
COIN_POINTS = 10
START_LIVES = 3
INVULNERABLE_FRAMES = FPS  # nach einer Kollision 1 Sekunde unverwundbar

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 47)
YELLOW = (250, 204, 21)
GRASS_COLOR = (34, 102, 51)
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (230, 230, 230)

IMAGE_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
