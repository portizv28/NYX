"""Centro de control de NYX con navegación lateral y esfera protagonista."""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable
from tkinter import scrolledtext

from core.state import AssistantState
from core.store import AssistantSnapshot
from gui.state_style import STATE_COLORS


class NyxWindow:
    """Vista de escritorio: representa estado y emite acciones del usuario."""

    SECTIONS = (
        "Conversaciones", "Memoria", "Capacidades", "Automatizaciones",
        "Archivos", "Configuración", "Sistema",
    )
    SIDEBAR_WIDTH = 280

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("NYX")
        self.root.geometry("1040x680")
        self.root.minsize(760, 560)
        self.root.configure(bg="#06080D")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self._on_submit: Callable[[str], None] | None = None
        self._on_voice_request: Callable[[], None] | None = None
        self._selected_section = "Conversaciones"
        self._visual_state = AssistantState.SLEEPING
        self._phase = 0.0
        self._sidebar_visible = False
        self._build_header()
        self._build_sidebar()
        self._build_main()
        self._hide_sidebar()
        self._animate_orb()

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg="#0B0E16", height=54)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        tk.Button(
            header, text="☰", command=self.toggle_sidebar, font=("Segoe UI Symbol", 18),
            fg="#BDEBFF", bg="#0B0E16", activebackground="#172333", relief="flat", width=3,
        ).pack(side="left", padx=(10, 4))
        tk.Label(
            header, text="NYX", fg="#E7F8FF", bg="#0B0E16", font=("Segoe UI", 16, "bold")
        ).pack(side="left")
        self.status_label = tk.Label(
            header, text="SLEEP · Esperando", fg="#6E9FB4", bg="#0B0E16", font=("Segoe UI", 9)
        )
        self.status_label.pack(side="right", padx=18)

    def _build_sidebar(self) -> None:
        self.sidebar = tk.Frame(self.root, bg="#0B0E16", width=self.SIDEBAR_WIDTH)
        self.sidebar.grid_propagate(False)
        tk.Label(
            self.sidebar, text="CONTROL CENTER", fg="#5FAFD1", bg="#0B0E16", font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=22, pady=(24, 12))
        self._section_buttons: dict[str, tk.Button] = {}
        for section in self.SECTIONS:
            button = tk.Button(
                self.sidebar, text=section, anchor="w", command=lambda item=section: self.show_section(item),
                fg="#CFD9E1", bg="#0B0E16", activeforeground="white", activebackground="#172333",
                relief="flat", font=("Segoe UI", 11), padx=22, pady=10,
            )
            button.pack(fill="x")
            self._section_buttons[section] = button
        tk.Frame(self.sidebar, bg="#1A2634", height=1).pack(fill="x", padx=20, pady=18)
        self.sidebar_summary = tk.Label(
            self.sidebar, text="NYX · Nix\nSistema disponible", justify="left", anchor="w",
            fg="#6E9FB4", bg="#0B0E16", font=("Segoe UI", 9), padx=22,
        )
        self.sidebar_summary.pack(fill="x")

    def _build_main(self) -> None:
        self.main = tk.Frame(self.root, bg="#06080D")
        self.main.grid(row=1, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=3)
        self.main.grid_rowconfigure(1, weight=0)
        self.main.grid_rowconfigure(2, weight=0)

        self.orb_canvas = tk.Canvas(self.main, bg="#06080D", highlightthickness=0, height=330)
        self.orb_canvas.grid(row=0, column=0, sticky="nsew")
        self.orb_canvas.bind("<Configure>", lambda _event: self._draw_orb())
        self.orb_glow = self.orb_canvas.create_oval(0, 0, 0, 0, fill="", outline="#333333", width=8)
        self.orb = self.orb_canvas.create_oval(0, 0, 0, 0, fill="black", outline="")
        self.orb_caption = self.orb_canvas.create_text(0, 0, text="Esperando la palabra de activación", fill="#6E9FB4", font=("Segoe UI", 10))

        self.section_frame = tk.Frame(self.main, bg="#06080D")
        self.section_frame.grid(row=1, column=0, sticky="ew", padx=42)
        self.section_frame.grid_columnconfigure(0, weight=1)
        self.section_title = tk.Label(
            self.section_frame, text="Conversaciones", fg="#E7F8FF", bg="#06080D", font=("Segoe UI", 14, "bold")
        )
        self.section_title.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.section_info = tk.Label(
            self.section_frame, text="", justify="left", anchor="w", fg="#91A6B5", bg="#06080D", font=("Segoe UI", 10)
        )
        self.section_info.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.chat_card = tk.Frame(self.main, bg="#0B0E16", highlightbackground="#172333", highlightthickness=1)
        self.chat_card.grid(row=2, column=0, sticky="ew", padx=42, pady=(4, 28))
        self.chat = scrolledtext.ScrolledText(
            self.chat_card, wrap=tk.WORD, height=6, bg="#0B0E16", fg="#DDE8EE", insertbackground="white",
            relief="flat", font=("Segoe UI", 10), padx=14, pady=10,
        )
        self.chat.pack(fill="x", padx=1, pady=(1, 0))
        self.chat.config(state="disabled")
        controls = tk.Frame(self.chat_card, bg="#0B0E16")
        controls.pack(fill="x", padx=10, pady=(2, 10))
        self.entry = tk.Entry(
            controls, font=("Segoe UI", 11), bg="#172333", fg="white", insertbackground="white", relief="flat"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.entry.bind("<Return>", lambda _event: self.enviar())
        tk.Button(controls, text="Enviar", command=self.enviar, bg="#1C7FA7", fg="white", relief="flat", padx=12).pack(side="left", padx=(8, 0))
        tk.Button(controls, text="Voz", command=self.escuchar, bg="#172333", fg="#BDEBFF", relief="flat", padx=12).pack(side="left", padx=(6, 0))
        self.entry.focus()

    def toggle_sidebar(self) -> None:
        if self._sidebar_visible:
            self._hide_sidebar()
        else:
            self._show_sidebar()

    def _show_sidebar(self) -> None:
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.root.grid_columnconfigure(0, minsize=self.SIDEBAR_WIDTH)
        self._sidebar_visible = True

    def _hide_sidebar(self) -> None:
        self.sidebar.grid_remove()
        self.root.grid_columnconfigure(0, minsize=0)
        self._sidebar_visible = False

    def _draw_orb(self) -> None:
        width = max(self.orb_canvas.winfo_width(), 1)
        height = max(self.orb_canvas.winfo_height(), 1)
        center_x, center_y = width / 2, height * 0.45
        amplitude = {
            AssistantState.SLEEPING: 0.045,
            AssistantState.LISTENING: 0.11,
            AssistantState.THINKING: 0.075,
            AssistantState.SPEAKING: 0.12,
            AssistantState.IDLE: 0.06,
        }[self._visual_state]
        base_radius = 66
        radius = base_radius * (1 + math.sin(self._phase) * amplitude)
        glow_radius = radius + 24 + math.sin(self._phase * 0.7) * 5
        self.orb_canvas.coords(self.orb, center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        self.orb_canvas.coords(self.orb_glow, center_x - glow_radius, center_y - glow_radius, center_x + glow_radius, center_y + glow_radius)
        self.orb_canvas.coords(self.orb_caption, center_x, center_y + 112)

    def _animate_orb(self) -> None:
        speed = {
            AssistantState.SLEEPING: 0.035,
            AssistantState.LISTENING: 0.14,
            AssistantState.THINKING: 0.1,
            AssistantState.SPEAKING: 0.16,
            AssistantState.IDLE: 0.06,
        }[self._visual_state]
        self._phase += speed
        self._draw_orb()
        self.root.after(33, self._animate_orb)

    def add_message(self, author: str, text: str) -> None:
        self.chat.config(state="normal")
        self.chat.insert("end", f"{author}:\n{text}\n\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def add_user_message(self, text: str) -> None:
        self.add_message("Tú", text)

    def add_assistant_message(self, text: str) -> None:
        self.add_message("NYX", text)

    def render_state(self, state: AssistantState) -> None:
        self._visual_state = state
        color = STATE_COLORS[state]
        self.orb_canvas.itemconfig(self.orb, fill=color)
        self.orb_canvas.itemconfig(self.orb_glow, outline="#263341" if state is AssistantState.SLEEPING else color)
        self.status_label.config(text=f"{state.value.upper()} · {self._state_caption(state)}")

    def render_system_state(self, snapshot: AssistantSnapshot) -> None:
        capabilities = ", ".join(snapshot.capabilities) or "sin capacidades"
        self.orb_canvas.itemconfig(self.orb_caption, text=snapshot.activity)
        self.sidebar_summary.config(text=f"NYX · Nix\nMicrófono: {snapshot.microphone.value}\nModelo: {snapshot.active_model}")
        if self._selected_section == "Sistema":
            self.section_info.config(
                text=(f"Estado: {snapshot.state.value}   ·   Micrófono: {snapshot.microphone.value}\n"
                      f"Modelo: {snapshot.active_model}   ·   Memoria: {'conectada' if snapshot.memory_available else 'no disponible'}\n"
                      f"Capacidades: {capabilities}\nÚltima acción: {snapshot.last_action}")
            )

    def show_section(self, section: str) -> None:
        if section not in self.SECTIONS:
            return
        self._selected_section = section
        self.section_title.config(text=section)
        for name, button in self._section_buttons.items():
            button.config(bg="#172333" if name == section else "#0B0E16")
        if section == "Conversaciones":
            self.section_info.config(text="Habla con NYX o escribe una solicitud. La esfera refleja su estado en todo momento.")
            self.chat_card.grid()
        else:
            self.chat_card.grid_remove()
            if section != "Sistema":
                self.section_info.config(text="Este espacio está preparado para conectar la capacidad de NYX correspondiente.")
        if self._sidebar_visible:
            self._hide_sidebar()

    @staticmethod
    def _state_caption(state: AssistantState) -> str:
        return {
            AssistantState.SLEEPING: "Esperando",
            AssistantState.LISTENING: "Escuchando",
            AssistantState.THINKING: "Pensando",
            AssistantState.SPEAKING: "Hablando",
            AssistantState.IDLE: "Disponible",
        }[state]

    def set_on_submit(self, callback: Callable[[str], None]) -> None:
        self._on_submit = callback

    def set_callback(self, callback: Callable[[str], None]) -> None:
        self.set_on_submit(callback)

    def set_voice_callback(self, callback: Callable[[], None]) -> None:
        self._on_voice_request = callback

    def enviar(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.add_user_message(text)
        if self._on_submit:
            self._on_submit(text)

    def escuchar(self) -> None:
        if self._on_voice_request:
            self._on_voice_request()

    # Compatibilidad con la API inicial.
    def escribir_chat(self, text: str) -> None:
        self.add_assistant_message(text)

    def cambiar_color(self, color: str) -> None:
        self.orb_canvas.itemconfig(self.orb, fill=color)

    def cambiar_estado(self, text: str) -> None:
        self.add_assistant_message(text)

    def run(self) -> None:
        self.root.mainloop()
