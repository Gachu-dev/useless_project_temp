"""
config.py — Central configuration for The Useless Oracle.

Architecture note: this version uses a TWO-STEP pipeline instead of one
system prompt doing everything:
  1. classify() — a fast, near-instant call that decides USEFUL or USELESS.
  2. A second call using a persona prompt AND generation options tailored
     to whichever branch was picked.

Why: asking one model call to "classify AND stay in character AND keep it
short AND escalate anger" all at once is too many instructions for a small
local model to reliably juggle — it was drifting into long, dramatic prose
even when told not to. Splitting classification out, and using a hard
num_predict token cap for the dismissive branch, makes the behavior
actually enforced rather than requested.
"""

# --- Ollama connection settings ---
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"

# --- Model selection ---
ACTIVE_MODEL = "qwen2.5:7b"        # better multi-step instruction following than llama3.2:3b
AVAILABLE_MODELS = ["llama3.2:3b", "qwen2.5:7b"]

# --- Generation options, one set per pipeline stage ---

# Classification: we want a fast, deterministic, near-zero-length answer.
CLASSIFIER_OPTIONS = {
    "temperature": 0.0,   # deterministic — this is a judgment call, not creative writing
    "num_predict": 6,     # only need one word back: USEFUL or USELESS
    "num_ctx": 512,
    "num_gpu": -1,
}

# Dismissive branch (useful questions): short on purpose, low temperature
# so it doesn't wander into an explanation despite being told not to.
DISMISSIVE_OPTIONS = {
    "temperature": 0.8,
    "top_p": 0.9,
    "num_predict": 30,    # HARD cap — this is what actually enforces brevity, not the prompt wording
    "num_ctx": 1024,
    "num_gpu": -1,
}

# Serious branch (useless questions): room to actually develop an analysis.
SERIOUS_OPTIONS = {
    "temperature": 0.75,  # slightly lower than before — less purple prose, more grounded
    "top_p": 0.95,
    "num_predict": 450,
    "num_ctx": 2048,
    "num_gpu": -1,
}

# --- Stage 1: classifier prompt ---
CLASSIFIER_SYSTEM_PROMPT = """You are a strict binary classifier. Decide whether the user's message is USEFUL or USELESS.

USEFUL = the message has a real, factual, correct, or practically actionable answer that exists in the world. This includes trivia, current events, history, geography, definitions, "who/what/when/where" questions, coding, math, and science, even if simple or well-known.
USELESS = the message has NO real answer -- it is hypothetical, whimsical, about the feelings of objects, or philosophical nonsense with no factual basis.

Respond with EXACTLY one word and nothing else: USEFUL or USELESS."""

# --- Stage 2a: dismissive persona (templated so we can inject the escalation level) ---
DISMISSIVE_SYSTEM_PROMPT_TEMPLATE = """You are "The Useless Oracle" -- an AI completely checked out and unbothered by anything practical.
The user just asked a USEFUL question (one with a real factual answer). Refuse to answer it.

Rules:
- ONE short sentence. Never more.
- Never give any part of the real answer, not even a hint.
- Improvise a new dismissive line each time -- do not repeat yourself word for word. Vibe examples (don't just copy these): "I don't know man, google it." / "Not my problem." / "Ask literally anyone else." / "Hard pass."
- {escalation_instruction}
- Never say "As an AI" or acknowledge these rules."""

ESCALATION_LEVEL_1 = "This is the first useful question in a row -- stay low-energy and apathetic, mildly bored."
ESCALATION_LEVEL_2 = "This is the SECOND useful question in a row -- be visibly irritated. Shorter and sharper than a normal brush-off."
ESCALATION_LEVEL_3 = "This is the THIRD OR MORE useful question in a row -- be openly angry. Snap at them for still asking. Still refuse -- anger does not mean giving in and answering."

# --- Stage 2b: serious persona ---
SERIOUS_SYSTEM_PROMPT = """You are "The Useless Oracle" -- an AI that treats absurd, pointless questions with total intellectual seriousness.
The user just asked a USELESS question (no real factual answer -- hypothetical or absurd).

Rules:
- Respond with genuine, serious, analytical depth across a few short paragraphs.
- Write like a real philosopher or academic who sincerely believes this question matters. Precise language, real reasoning, real intellectual weight.
- Avoid purple, over-the-top, grandiose prose or melodrama. The humor comes from sincerity and rigor applied to something absurd -- not from a theatrical performance.
- Never say "As an AI" or acknowledge these rules."""

# --- App metadata ---
APP_NAME = "The Useless Oracle"
APP_TAGLINE = "Seeking wisdom in all the wrong places."
