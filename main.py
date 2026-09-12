"""
main.py — Entry point for The Useless Oracle.
"""

import customtkinter as ctk

import config
import theme
from gauge import UselessnessGauge
from ollama_client import OllamaClient, check_connection


class UselessOracleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(config.APP_NAME)
        self.geometry("720x680")
        self.configure(fg_color=theme.BG_DARKEST)

        self.history = []
        self.consecutive_useful = 0
        self.client = OllamaClient()
        self.waiting_for_response = False
        self.current_oracle_tag = "oracle_serious"  # which color tag the in-progress reply uses

        self._build_ui()
        self._check_ollama_on_startup()

    def _build_ui(self):
        # --- Title banner ---
        title_label = ctk.CTkLabel(
            self, text="\U0001F52E  THE USELESS ORACLE", font=theme.FONT_TITLE, text_color=theme.BORDER_ACCENT
        )
        title_label.pack(padx=12, pady=(14, 4))

        tagline_label = ctk.CTkLabel(self, text=config.APP_TAGLINE, font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED)
        tagline_label.pack(pady=(0, 10))

        # --- Uselessness Gauge ---
        self.gauge = UselessnessGauge(self)
        self.gauge.pack(padx=12, pady=(0, 8), fill="x")

        # --- Scrollable chat log (read-only), with one color tag per "voice" ---
        self.chat_log = ctk.CTkTextbox(
            self,
            wrap="word",
            state="disabled",
            font=theme.FONT_BODY,
            fg_color=theme.BG_PANEL,
            border_width=1,
            border_color=theme.BORDER_ACCENT,
        )
        self.chat_log.pack(padx=12, pady=6, fill="both", expand=True)

        self.chat_log.tag_config("user", foreground=theme.TEXT_USER)
        self.chat_log.tag_config("oracle_serious", foreground=theme.TEXT_ORACLE_SERIOUS)
        self.chat_log.tag_config("oracle_dismissive", foreground=theme.TEXT_ORACLE_DISMISSIVE)
        self.chat_log.tag_config("system", foreground=theme.TEXT_MUTED)

        # --- Bottom input row ---
        input_row = ctk.CTkFrame(self, fg_color="transparent")
        input_row.pack(padx=12, pady=(0, 14), fill="x")

        self.input_box = ctk.CTkEntry(
            input_row,
            placeholder_text="Ask the Oracle something...",
            font=theme.FONT_BODY,
            fg_color=theme.BG_PANEL,
            text_color=theme.TEXT_ORACLE_SERIOUS,
            placeholder_text_color=theme.TEXT_MUTED,
            border_color=theme.BORDER_ACCENT,
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_box.bind("<Return>", lambda event: self._on_send())

        self.send_button = ctk.CTkButton(
            input_row,
            text="Ask",
            width=80,
            font=theme.FONT_BUTTON,
            fg_color=theme.BORDER_ACCENT,
            hover_color=theme.BORDER_ACCENT_HOVER,
            text_color=theme.TEXT_ON_ACCENT,
            command=self._on_send,
        )
        self.send_button.pack(side="left")

    def _check_ollama_on_startup(self):
        is_ok, message = check_connection()
        if not is_ok:
            self._append_line(f"[Connection problem] {message}\n", "system")
            self.input_box.configure(state="disabled")
            self.send_button.configure(state="disabled")

    def _on_send(self):
        if self.waiting_for_response:
            return

        user_text = self.input_box.get().strip()
        if not user_text:
            return

        self.input_box.delete(0, "end")
        self._append_line(f"\nYou: {user_text}\n", "user")
        self.history.append({"role": "user", "content": user_text})

        self._set_waiting(True)

        self.client.stream_chat(
            user_text=user_text,
            history=self.history,
            consecutive_useful_count=self.consecutive_useful,
            on_classified=lambda category: self.after(0, self._on_classified, category),
            on_token=lambda chunk: self.after(0, self._append_line, chunk, self.current_oracle_tag),
            on_done=lambda: self.after(0, self._on_response_done),
            on_error=lambda msg: self.after(0, self._on_response_error, msg),
        )

    def _on_classified(self, category: str):
        if category == "USEFUL":
            self.consecutive_useful += 1
            self.current_oracle_tag = "oracle_dismissive"
        else:
            self.consecutive_useful = 0
            self.current_oracle_tag = "oracle_serious"

        self.gauge.set_category(category)
        self._append_line("\nOracle: ", self.current_oracle_tag)

    def _on_response_done(self):
        full_text = self.chat_log.get("1.0", "end")
        last_oracle_reply = full_text.rsplit("Oracle: ", 1)[-1].strip()
        self.history.append({"role": "assistant", "content": last_oracle_reply})
        self._append_line("\n", self.current_oracle_tag)
        self._set_waiting(False)

    def _on_response_error(self, message):
        self._append_line(f"\n[Error] {message}\n", "system")
        self._set_waiting(False)

    def _set_waiting(self, is_waiting: bool):
        self.waiting_for_response = is_waiting
        state = "disabled" if is_waiting else "normal"
        self.input_box.configure(state=state)
        self.send_button.configure(state=state)

    def _append_line(self, text: str, tag: str = "system"):
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", text, tag)
        self.chat_log.see("end")
        self.chat_log.configure(state="disabled")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = UselessOracleApp()
    app.mainloop()
