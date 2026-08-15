"""Esfera flotante de NYX."""

import tkinter as tk
from collections.abc import Callable

from core.state import AssistantState
from gui.orb_geometry import LEFT_SEGMENT, RIGHT_SEGMENT, geometry_for


class NyxOrb:
    def __init__(self) -> None:
        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="magenta")
        self.root.wm_attributes("-transparentcolor", "magenta")
        self.root.geometry("180x180+100+100")

        self.canvas = tk.Canvas(
            self.root, width=180, height=180, bg="magenta", highlightthickness=0
        )
        self.canvas.pack()
        self.glow_left = self.canvas.create_arc(0, 0, 0, 0, start=LEFT_SEGMENT[0], extent=LEFT_SEGMENT[1], style="arc", outline="#F4F8FF", width=14)
        self.glow_right = self.canvas.create_arc(0, 0, 0, 0, start=RIGHT_SEGMENT[0], extent=RIGHT_SEGMENT[1], style="arc", outline="#F4F8FF", width=14)
        self.circle = self.canvas.create_oval(0, 0, 0, 0, fill="#F4F8FF", outline="#FFFFFF", width=2)
        self._time = 0.0
        self._state = AssistantState.SLEEPING
        self._drag_x = 0
        self._drag_y = 0
        self._callback: Callable[[], None] | None = None

        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<Double-Button-1>", self._open)
        self.canvas.bind("<B1-Motion>", self._drag)
        self._animate()

    def _animate(self) -> None:
        self._time += 0.08
        geometry = geometry_for(self._state, self._time, 90, 90, 32)
        self.canvas.coords(self.circle, 90 - geometry.inner_radius, 90 - geometry.inner_radius, 90 + geometry.inner_radius, 90 + geometry.inner_radius)
        radius = geometry.ring_center_radius
        self.canvas.coords(self.glow_left, 90 - radius, 90 - radius, 90 + radius, 90 + radius)
        self.canvas.coords(self.glow_right, 90 - radius, 90 - radius, 90 + radius, 90 + radius)
        self.canvas.itemconfig(self.glow_left, width=geometry.ring_thickness)
        self.canvas.itemconfig(self.glow_right, width=geometry.ring_thickness)
        self.root.after(20, self._animate)

    def _start_drag(self, event) -> None:
        self._drag_x, self._drag_y = event.x, event.y

    def _open(self, _event) -> None:
        if self._callback:
            self._callback()

    def _drag(self, event) -> None:
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def set_callback(self, callback: Callable[[], None]) -> None:
        self._callback = callback

    def render_state(self, state: AssistantState) -> None:
        self._state = state
        active = state is not AssistantState.SLEEPING
        color = "#25A8FF"
        self.canvas.itemconfig(self.circle, fill="#063464" if active else "#F4F8FF", outline=color if active else "#FFFFFF")
        self.canvas.itemconfig(self.glow_left, outline="#F4F8FF" if state is AssistantState.SLEEPING else color)
        self.canvas.itemconfig(self.glow_right, outline="#F4F8FF" if state is AssistantState.SLEEPING else color)

    def set_position(self, x: int, y: int) -> None:
        """Posiciona la esfera; futuro movimiento inteligente usará esta API."""
        self.root.geometry(f"+{x}+{y}")

    def position(self) -> tuple[int, int]:
        return self.root.winfo_x(), self.root.winfo_y()

    def move_to(self, x: int, y: int) -> None:
        """Alias semántico para controladores de movimiento futuros."""
        self.set_position(x, y)

    # Compatibilidad con las llamadas de la versión inicial.
    def dormir(self) -> None:
        self.render_state(AssistantState.SLEEPING)

    def escuchar(self) -> None:
        self.render_state(AssistantState.LISTENING)

    def pensar(self) -> None:
        self.render_state(AssistantState.THINKING)

    def hablar(self) -> None:
        self.render_state(AssistantState.SPEAKING)

    def normal(self) -> None:
        self.render_state(AssistantState.IDLE)

    def ocultar(self) -> None:
        self.root.withdraw()

    def hide(self) -> None:
        self.ocultar()

    def mostrar(self) -> None:
        self.root.deiconify()

    def show(self) -> None:
        self.mostrar()
