"""
theme.py — Visual identity for The Useless Oracle.

Concept: a dark "arcane terminal" look — like a fortune-telling machine
built out of old computer parts. Deep near-black background, phosphor-green
accents for anything interactive, and role-colored chat text so you can
tell at a glance whether the Oracle is being dismissive or philosophical
before you even read the words.

All colors and fonts live here as constants — nothing in main.py should
ever have a raw hex code or font name; it should import from this file.
"""

# --- Core palette ---
BG_DARKEST = "#0a0f0c"           # window background
BG_PANEL = "#141c17"             # frames, textbox, input box background
BORDER_ACCENT = "#3ddc84"        # phosphor green — borders, primary button, progress bar fill
BORDER_ACCENT_HOVER = "#2bb768"  # darker green for button hover state

# --- Chat text colors, one per "voice" ---
TEXT_USER = "#5ec8c0"            # your own messages — muted teal
TEXT_ORACLE_SERIOUS = "#e4ddf5"  # useless-question analytical replies — pale lavender
TEXT_ORACLE_DISMISSIVE = "#c97b5c"  # useful-question brush-offs — dusty rust/amber
TEXT_MUTED = "#7c8880"           # system lines, taglines, telemetry labels, errors
TEXT_ON_ACCENT = "#0a0f0c"       # text drawn on top of the green accent (button labels)

# --- Fonts ---
# Consolas ships with every Windows install and reads as "terminal-ish"
# without needing a font install step during the hackathon.
FONT_FAMILY = "Consolas"
FONT_BODY = (FONT_FAMILY, 13)
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_SMALL = (FONT_FAMILY, 11)
FONT_BUTTON = (FONT_FAMILY, 13, "bold")
