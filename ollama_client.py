"""
ollama_client.py — All communication with the local Ollama service lives here.

Pipeline for every user message:
  1. classify()   — quick, low-token call: is this USEFUL or USELESS?
  2. _run()        — picks the matching persona prompt + generation options,
                     then streams the actual in-character reply.

Everything network-related runs on a background thread (see OllamaClient
below) so the Tkinter main loop never blocks. Callbacks fire from that
background thread — the caller must hop back to the main thread with
`.after(0, ...)` before touching any widget.
"""

import json
import threading
import requests

from config import (
    OLLAMA_CHAT_ENDPOINT,
    OLLAMA_TAGS_ENDPOINT,
    ACTIVE_MODEL,
    CLASSIFIER_OPTIONS,
    CLASSIFIER_SYSTEM_PROMPT,
    DISMISSIVE_OPTIONS,
    DISMISSIVE_SYSTEM_PROMPT_TEMPLATE,
    ESCALATION_LEVEL_1,
    ESCALATION_LEVEL_2,
    ESCALATION_LEVEL_3,
    SERIOUS_OPTIONS,
    SERIOUS_SYSTEM_PROMPT,
)


def check_connection() -> tuple[bool, str]:
    """Synchronous startup check — safe to call on the main thread once, before any chat happens."""
    try:
        response = requests.get(OLLAMA_TAGS_ENDPOINT, timeout=3)
        response.raise_for_status()
        return True, "Connected to Ollama."
    except requests.exceptions.ConnectionError:
        return False, (
            "Can't reach Ollama at localhost:11434.\n"
            "Is the Ollama service running? Try opening PowerShell and running 'ollama serve'."
        )
    except requests.exceptions.Timeout:
        return False, "Ollama didn't respond in time. It may be overloaded or hung."
    except requests.exceptions.RequestException as e:
        return False, f"Unexpected error reaching Ollama: {e}"


def classify(user_text: str) -> str:
    """
    Fast, near-deterministic call that decides USEFUL vs USELESS.
    Must be called from a background thread — it blocks on the network.
    Defaults to "USEFUL" on any failure, since a short dismissive reply
    is a safer fallback than accidentally trying to run the serious,
    longer generation path on a request we couldn't classify.
    """
    payload = {
        "model": ACTIVE_MODEL,
        "messages": [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "stream": False,
        "options": CLASSIFIER_OPTIONS,
    }
    try:
        response = requests.post(OLLAMA_CHAT_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "").strip().upper()
        return "USELESS" if "USELESS" in content else "USEFUL"
    except requests.exceptions.RequestException:
        return "USEFUL"


class OllamaClient:
    """Runs the classify-then-respond pipeline on a background thread."""

    def __init__(self):
        self._current_thread = None
        self._stop_requested = False

    def stream_chat(self, user_text, history, consecutive_useful_count, on_classified, on_token, on_done, on_error):
        """
        user_text:                the raw text the user just typed.
        history:                  full user/assistant turn history (no system message).
        consecutive_useful_count: how many USEFUL questions in a row BEFORE this one,
                                   tracked by the caller (main.py) — used to pick the
                                   escalation level for the dismissive persona.
        on_classified(category):  fired once classification finishes, with "USEFUL" or "USELESS",
                                   so the caller can update its own counter.
        on_token / on_done / on_error: streaming callbacks, same as before.
        """
        self._stop_requested = False
        self._current_thread = threading.Thread(
            target=self._run,
            args=(user_text, history, consecutive_useful_count, on_classified, on_token, on_done, on_error),
            daemon=True,
        )
        self._current_thread.start()

    def stop(self):
        self._stop_requested = True

    def _run(self, user_text, history, consecutive_useful_count, on_classified, on_token, on_done, on_error):
        try:
            category = classify(user_text)
        except Exception as e:
            on_error(f"Classification step failed: {e}")
            return

        on_classified(category)

        if category == "USEFUL":
            new_count = consecutive_useful_count + 1
            if new_count == 1:
                escalation = ESCALATION_LEVEL_1
            elif new_count == 2:
                escalation = ESCALATION_LEVEL_2
            else:
                escalation = ESCALATION_LEVEL_3
            system_prompt = DISMISSIVE_SYSTEM_PROMPT_TEMPLATE.format(escalation_instruction=escalation)
            options = DISMISSIVE_OPTIONS
        else:
            system_prompt = SERIOUS_SYSTEM_PROMPT
            options = SERIOUS_OPTIONS

        payload = {
            "model": ACTIVE_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + history,
            "stream": True,
            "options": options,
        }

        try:
            with requests.post(OLLAMA_CHAT_ENDPOINT, json=payload, stream=True, timeout=60) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if self._stop_requested:
                        break
                    if not line:
                        continue

                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        on_token(token)

                    if chunk.get("done"):
                        break

            on_done()

        except requests.exceptions.ConnectionError:
            on_error("Lost connection to Ollama. Is the service still running?")
        except requests.exceptions.Timeout:
            on_error("Ollama took too long to respond.")
        except json.JSONDecodeError:
            on_error("Received a malformed response from Ollama.")
        except requests.exceptions.RequestException as e:
            on_error(f"Request to Ollama failed: {e}")
