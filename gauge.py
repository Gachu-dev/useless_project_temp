"""
gauge.py — The Uselessness Gauge: a purely theatrical meter that swings
between PRACTICAL and PROFOUND based on the last classification result.

The number itself means nothing real (it's randomized within a band per
category) — it's a comic prop, not a measurement. The animation is what
sells it: the marker eases toward its target instead of jumping instantly.
"""

import random
import tkinter as tk

import customtkinter as ctk

import theme


class UselessnessGauge(ctk.CTkFrame):
    TRACK_WIDTH = 260
    TRACK_HEIGHT = 14
    MARKER_RADIUS = 9

    def __init__(self, master):
        super().__init__(master, fg_color=theme.BG_PANEL, border_width=1, border_color=theme.BORDER_ACCENT)

        self._value = 0.0    # currently displayed 0-100 position
        self._target = 0.0   # value the animation is easing toward
        self._animating = False

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            header, text="USELESSNESS GAUGE", font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED
        ).pack(side="left")

        self.value_label = ctk.CTkLabel(
            header, text="0%", font=theme.FONT_BUTTON, text_color=theme.BORDER_ACCENT
        )
        self.value_label.pack(side="right")

        track_row = ctk.CTkFrame(self, fg_color="transparent")
        track_row.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(
            track_row, text="PRACTICAL", font=theme.FONT_SMALL, text_color=theme.TEXT_ORACLE_DISMISSIVE
        ).pack(side="left", padx=(0, 6))

        # A plain tkinter Canvas for the track/marker — CustomTkinter has no
        # canvas widget of its own, so this is set to match the panel
        # background exactly and otherwise behaves like any other widget.
        self.canvas = tk.Canvas(
            track_row,
            width=self.TRACK_WIDTH,
            height=self.TRACK_HEIGHT + self.MARKER_RADIUS * 2,
            bg=theme.BG_PANEL,
            highlightthickness=0,
        )
        self.canvas.pack(side="left")

        ctk.CTkLabel(
            track_row, text="PROFOUND", font=theme.FONT_SMALL, text_color=theme.TEXT_ORACLE_SERIOUS
        ).pack(side="left", padx=(6, 0))

        self._draw_track()
        self._marker = self._draw_marker()

    def _draw_track(self):
        y = self.MARKER_RADIUS + self.TRACK_HEIGHT / 2
        self.canvas.create_line(0, y, self.TRACK_WIDTH, y, fill=theme.TEXT_MUTED, width=2)

    def _draw_marker(self):
        x, y, r = 0, self.MARKER_RADIUS + self.TRACK_HEIGHT / 2, self.MARKER_RADIUS
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=theme.BORDER_ACCENT, outline="")

    def set_category(self, category: str):
        """
        Call this once per classification result ("USEFUL" or "USELESS").
        Picks a new random target in the matching band and kicks off the
        easing animation toward it.
        """
        if category == "USEFUL":
            self._target = random.uniform(3, 15)     # low = "barely useless at all"
        else:
            self._target = random.uniform(85, 99)    # high = "profoundly useless"

        if not self._animating:
            self._animating = True
            self._step()

    def _step(self):
        diff = self._target - self._value
        if abs(diff) < 0.3:
            self._value = self._target
            self._animating = False
        else:
            self._value += diff * 0.15  # ease-out: bigger gaps move faster, settles near the target
        self._redraw()

        if self._animating:
            self.after(16, self._step)  # roughly 60fps

    def _redraw(self):
        x = (self._value / 100) * self.TRACK_WIDTH
        y = self.MARKER_RADIUS + self.TRACK_HEIGHT / 2
        r = self.MARKER_RADIUS
        self.canvas.coords(self._marker, x - r, y - r, x + r, y + r)
        self.value_label.configure(text=f"{self._value:.0f}%")
