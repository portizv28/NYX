"""Control Center de NYX: vista Tkinter reactiva, sin lógica de negocio."""

from __future__ import annotations

import math
from datetime import datetime
import tkinter as tk
from collections.abc import Callable
from tkinter import scrolledtext

from core.state import AssistantState
from core.store import AssistantSnapshot
from gui.orb_geometry import LEFT_SEGMENT, RIGHT_SEGMENT, geometry_for
from gui.system_metrics import read_system_metrics
from news.models import NewsQueryResult


class NyxWindow:
    """Representa el estado y emite intenciones del usuario al controlador."""

    SECTIONS = ("Inicio", "Conversaciones", "Noticias", "Memoria", "Capacidades", "Automatizaciones", "Archivos", "Configuración", "Sistema", "Información de NYX")
    SIDEBAR_WIDTH = 248
    BG = "#03060C"
    PANEL = "#080E17"
    PANEL_ALT = "#0B1420"
    BORDER = "#1A4262"
    BLUE = "#25A8FF"
    WHITE = "#F4F8FF"

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("NYX")
        self.root.geometry("1500x920")
        self.root.minsize(1020, 680)
        self.root.configure(bg=self.BG)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self._on_submit: Callable[[str], None] | None = None
        self._on_voice_request: Callable[[], None] | None = None
        self._on_news_refresh: Callable[[], None] | None = None
        self._on_news_open: Callable[[str], None] | None = None
        self._on_listening_toggle: Callable[[], None] | None = None
        self._on_mute_toggle: Callable[[], None] | None = None
        self._selected_section = "Inicio"
        self._sidebar_visible = True
        self._visual_state = AssistantState.SLEEPING
        self._phase = 0.0
        self._muted = False
        self._build_header()
        self._build_layout()
        self._build_footer()
        self._show_dashboard()
        self._animate()

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg="#04070D", height=66, highlightbackground=self.BORDER, highlightthickness=1)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        header.grid_propagate(False)
        tk.Button(header, text="☰", command=self.toggle_sidebar, font=("Segoe UI Symbol", 21), fg=self.WHITE, bg="#04070D", activebackground="#10263A", relief="flat", width=3).pack(side="left", padx=(10, 4))
        tk.Label(header, text="NYX", fg="#FFFFFF", bg="#04070D", font=("Segoe UI", 22, "bold")).pack(side="left", padx=8)
        tk.Label(header, text="ASISTENTE INTELIGENTE", fg="#5EBBFF", bg="#04070D", font=("Segoe UI", 10, "bold")).pack(side="left", padx=28)
        self.status_label = tk.Label(header, text="SLEEPING · Esperando", fg=self.WHITE, bg="#04070D", font=("Segoe UI", 10))
        self.status_label.pack(side="right", padx=20)

    def _build_layout(self) -> None:
        self.body = tk.Frame(self.root, bg=self.BG)
        self.body.grid(row=1, column=0, sticky="nsew", padx=12, pady=10)
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, minsize=355)
        self._build_sidebar()
        self._build_center()
        self._build_news_panel()

    def _panel(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        return tk.Frame(parent, bg=self.PANEL, highlightbackground=self.BORDER, highlightthickness=1, **kwargs)

    def _build_sidebar(self) -> None:
        self.sidebar = self._panel(self.body, width=self.SIDEBAR_WIDTH)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self.sidebar.grid_propagate(False)
        tk.Label(self.sidebar, text="MENÚ", fg="#9AB8CA", bg=self.PANEL, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(20, 8))
        self._section_buttons: dict[str, tk.Button] = {}
        for section in self.SECTIONS:
            button = tk.Button(self.sidebar, text=section, anchor="w", command=lambda item=section: self.show_section(item), fg="#EAF4FC", bg=self.PANEL, activeforeground="white", activebackground="#10263A", relief="flat", font=("Segoe UI", 10), padx=20, pady=9)
            button.pack(fill="x")
            self._section_buttons[section] = button
        system = self._panel(self.sidebar)
        system.pack(fill="x", padx=14, pady=18)
        tk.Label(system, text="ESTADO DEL SISTEMA", fg="#B9D8E9", bg=self.PANEL, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        self.sidebar_summary = tk.Label(system, text="NYX ONLINE\nMicrófono: activo\nModelo: Ollama", justify="left", anchor="w", fg="#7AA8C3", bg=self.PANEL, font=("Segoe UI", 9))
        self.sidebar_summary.pack(fill="x", padx=12, pady=(0, 10))
        self.metrics_label = tk.Label(system, text="", justify="left", anchor="w", fg="#5EBBFF", bg=self.PANEL, font=("Segoe UI", 9))
        self.metrics_label.pack(fill="x", padx=12, pady=(0, 10))

    def _build_center(self) -> None:
        self.center = self._panel(self.body)
        self.center.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        self.center.grid_columnconfigure(0, weight=1)
        self.center.grid_rowconfigure(1, weight=1)
        meta = tk.Frame(self.center, bg=self.PANEL)
        meta.grid(row=0, column=0, sticky="ew", padx=22, pady=(16, 0))
        meta.grid_columnconfigure(1, weight=1)
        self.clock_label = tk.Label(meta, text="", fg=self.WHITE, bg=self.PANEL, justify="left", anchor="w", font=("Segoe UI", 15, "bold"))
        self.clock_label.grid(row=0, column=0, rowspan=2, sticky="w")
        self.center_title = tk.Label(meta, text="NYX", fg=self.WHITE, bg=self.PANEL, font=("Segoe UI", 20, "bold"))
        self.center_title.grid(row=0, column=1)
        tk.Label(meta, text="ASISTENTE INTELIGENTE", fg="#5EBBFF", bg=self.PANEL, font=("Segoe UI", 9, "bold")).grid(row=1, column=1)
        self.mode_label = tk.Label(meta, text="MODO\nNORMAL", fg="#9ED7FF", bg=self.PANEL, justify="right", anchor="e", font=("Segoe UI", 9, "bold"))
        self.mode_label.grid(row=0, column=2, rowspan=2, sticky="e")
        self.orb_canvas = tk.Canvas(self.center, bg=self.PANEL, highlightthickness=0, height=430)
        self.orb_canvas.grid(row=1, column=0, sticky="nsew", padx=12)
        self.orb_canvas.bind("<Configure>", lambda _event: self._draw_orb())
        self.ring_left = self.orb_canvas.create_arc(0, 0, 0, 0, start=LEFT_SEGMENT[0], extent=LEFT_SEGMENT[1], style="arc", outline=self.WHITE, width=18)
        self.ring_right = self.orb_canvas.create_arc(0, 0, 0, 0, start=RIGHT_SEGMENT[0], extent=RIGHT_SEGMENT[1], style="arc", outline=self.WHITE, width=18)
        self.orb = self.orb_canvas.create_oval(0, 0, 0, 0, fill="#F4F8FF", outline="#FFFFFF", width=2)
        self.orb_caption = self.orb_canvas.create_text(0, 0, text="NYX está esperando", fill="#B8D6E8", font=("Segoe UI", 11))
        self.wave_canvas = tk.Canvas(self.center, bg=self.PANEL, height=46, highlightthickness=0)
        self.wave_canvas.grid(row=2, column=0, sticky="ew", padx=42)
        self.greeting = tk.Label(self.center, text="Muy buenas, Pablo.\n¿Qué necesita de mí hoy?", justify="center", fg=self.WHITE, bg=self.PANEL, font=("Segoe UI", 16, "bold"))
        self.greeting.grid(row=3, column=0, pady=(6, 14))
        self._build_quick_actions()
        self.chat_card = self._panel(self.center)
        self.chat_card.grid(row=1, column=0, rowspan=4, sticky="nsew", padx=26, pady=26)
        self.chat_card.grid_remove()
        self._build_chat()

    def _build_quick_actions(self) -> None:
        quick = self._panel(self.center)
        quick.grid(row=4, column=0, sticky="ew", padx=28, pady=(0, 20))
        tk.Label(quick, text="ACCESOS RÁPIDOS", fg="#72C7FF", bg=self.PANEL, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(10, 5))
        controls = tk.Frame(quick, bg=self.PANEL)
        controls.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(controls, text="🎙  Hablar con NYX", command=self.escuchar, bg="#10263A", fg=self.WHITE, relief="flat", padx=12, pady=8).pack(side="left", padx=3)
        tk.Button(controls, text="Nueva nota", bg="#0E1C2B", fg=self.WHITE, relief="flat", padx=12, pady=8).pack(side="left", padx=3)
        tk.Button(controls, text="Abrir Spotify", bg="#0E1C2B", fg=self.WHITE, relief="flat", padx=12, pady=8).pack(side="left", padx=3)

    def _build_chat(self) -> None:
        tk.Label(self.chat_card, text="CONVERSACIONES", fg=self.WHITE, bg=self.PANEL, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=16, pady=(14, 6))
        self.chat = scrolledtext.ScrolledText(self.chat_card, wrap=tk.WORD, height=15, bg=self.PANEL, fg="#DDE8EE", insertbackground="white", relief="flat", font=("Segoe UI", 10), padx=14, pady=10)
        self.chat.pack(fill="both", expand=True, padx=1, pady=(1, 0))
        self.chat.config(state="disabled")
        controls = tk.Frame(self.chat_card, bg=self.PANEL)
        controls.pack(fill="x", padx=12, pady=12)
        self.entry = tk.Entry(controls, font=("Segoe UI", 11), bg="#10263A", fg="white", insertbackground="white", relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry.bind("<Return>", lambda _event: self.enviar())
        tk.Button(controls, text="Enviar", command=self.enviar, bg="#167EA6", fg="white", relief="flat", padx=12).pack(side="left", padx=(8, 0))

    def _build_news_panel(self) -> None:
        self.right_stack = tk.Frame(self.body, bg=self.BG)
        self.right_stack.grid(row=0, column=2, sticky="nsew")
        self.right_stack.grid_rowconfigure(0, weight=1)
        self.right_stack.grid_columnconfigure(0, weight=1)
        self.news_panel = self._panel(self.right_stack)
        self.news_panel.grid(row=0, column=0, sticky="nsew")
        top = tk.Frame(self.news_panel, bg=self.PANEL)
        top.pack(fill="x", padx=14, pady=(16, 8))
        tk.Label(top, text="NOTICIAS", fg=self.WHITE, bg=self.PANEL, font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Button(top, text="Actualizar  ↻", command=self.refresh_news, bg="#10263A", fg="#72C7FF", relief="flat", padx=8).pack(side="right")
        self.news_status = tk.Label(self.news_panel, text="Fuentes configuradas", justify="left", anchor="w", fg="#91B8CA", bg=self.PANEL, font=("Segoe UI", 8))
        self.news_status.pack(fill="x", padx=14, pady=(0, 6))
        self.news_feed = tk.Frame(self.news_panel, bg=self.PANEL)
        self.news_feed.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        lower = tk.Frame(self.right_stack, bg=self.BG)
        lower.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        lower.grid_columnconfigure((0, 1), weight=1)
        self.events_panel = self._panel(lower)
        self.events_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tk.Label(self.events_panel, text="PRÓXIMOS EVENTOS", fg="#72C7FF", bg=self.PANEL, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Label(self.events_panel, text="Calendario no conectado", fg="#91B8CA", bg=self.PANEL, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(0, 12))
        self.weather_panel = self._panel(lower)
        self.weather_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        tk.Label(self.weather_panel, text="CLIMA", fg="#72C7FF", bg=self.PANEL, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Label(self.weather_panel, text="Sin proveedor meteorológico\nconfigurado", fg="#91B8CA", bg=self.PANEL, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(0, 12))

    def _build_footer(self) -> None:
        footer = tk.Frame(self.root, bg="#04070D", height=58, highlightbackground=self.BORDER, highlightthickness=1)
        footer.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))
        footer.grid_propagate(False)
        self.listen_button = tk.Button(footer, text="🎙  Escuchar", command=self._toggle_listening, bg="#10263A", fg=self.WHITE, relief="flat", padx=16, pady=8)
        self.listen_button.pack(side="right", padx=(4, 12), pady=10)
        self.mute_button = tk.Button(footer, text="🔊  Silenciar", command=self._toggle_mute, bg="#10263A", fg=self.WHITE, relief="flat", padx=16, pady=8)
        self.mute_button.pack(side="right", padx=4, pady=10)
        tk.Label(footer, text="NYX v0.8 · Siempre a tu lado.", fg="#91B8CA", bg="#04070D", font=("Segoe UI", 9)).pack(side="left", padx=18)

    def _draw_orb(self) -> None:
        width, height = max(self.orb_canvas.winfo_width(), 1), max(self.orb_canvas.winfo_height(), 1)
        geometry = geometry_for(self._visual_state, self._phase, width / 2, height * 0.47, min(98, width * 0.15, height * 0.22))
        x, y = geometry.center_x, geometry.center_y
        self.orb_canvas.coords(self.orb, x - geometry.inner_radius, y - geometry.inner_radius, x + geometry.inner_radius, y + geometry.inner_radius)
        radius = geometry.ring_center_radius
        bounds = (x - radius, y - radius, x + radius, y + radius)
        self.orb_canvas.coords(self.ring_left, *bounds)
        self.orb_canvas.coords(self.ring_right, *bounds)
        self.orb_canvas.itemconfig(self.ring_left, width=geometry.ring_thickness)
        self.orb_canvas.itemconfig(self.ring_right, width=geometry.ring_thickness)
        self.orb_canvas.coords(self.orb_caption, x, y + radius + geometry.ring_thickness + 18)

    def _draw_wave(self) -> None:
        self.wave_canvas.delete("wave")
        if self._visual_state is AssistantState.SLEEPING:
            return
        width, height = max(self.wave_canvas.winfo_width(), 1), 46
        color = self.BLUE
        for x in range(0, width, 5):
            envelope = math.sin(math.pi * x / width) ** 1.5
            motion = abs(math.sin(self._phase * 3 + x * 0.12))
            amplitude = 4 + 15 * envelope * motion
            self.wave_canvas.create_line(x, height / 2 - amplitude, x, height / 2 + amplitude, fill=color, width=2, tags="wave")

    def _animate(self) -> None:
        speed = {AssistantState.SLEEPING: 0.028, AssistantState.LISTENING: 0.13, AssistantState.THINKING: 0.09, AssistantState.SPEAKING: 0.16, AssistantState.IDLE: 0.05}[self._visual_state]
        self._phase += speed
        self._draw_orb()
        self._draw_wave()
        now = datetime.now()
        self.clock_label.config(text=f"{now:%H:%M}\n{now:%d %b %Y}".upper())
        self.root.after(33, self._animate)

    def render_state(self, state: AssistantState) -> None:
        self._visual_state = state
        active = state is not AssistantState.SLEEPING
        color = self.BLUE if active else self.WHITE
        self.orb_canvas.itemconfig(self.orb, fill="#063464" if active else self.WHITE, outline=color)
        self.orb_canvas.itemconfig(self.ring_left, outline=color)
        self.orb_canvas.itemconfig(self.ring_right, outline=color)
        caption = {AssistantState.SLEEPING: "SLEEPING · Esperando", AssistantState.LISTENING: "LISTENING · Escuchando", AssistantState.THINKING: "PROCESSING · Pensando", AssistantState.SPEAKING: "SPEAKING · Hablando", AssistantState.IDLE: "IDLE · Disponible"}[state]
        self.status_label.config(text=caption, fg=color)
        self.orb_canvas.itemconfig(self.orb_caption, text=caption, fill=color)
        self.greeting.config(fg=color if active else self.WHITE)

    def render_system_state(self, snapshot: AssistantSnapshot) -> None:
        self.sidebar_summary.config(text=f"NYX ONLINE\nMicrófono: {snapshot.microphone.value}\nModelo: {snapshot.active_model}\nMemoria: {'conectada' if snapshot.memory_available else 'no disponible'}")
        microphone_active = snapshot.microphone.value == "active"
        self.listen_button.config(text="🎙  Escuchar" if microphone_active else "🎙  Activar escucha", fg=self.WHITE if microphone_active else "#91B8CA")
        metrics = read_system_metrics()
        ram = f"RAM {metrics.memory_percent}%" if metrics.memory_percent is not None else "RAM no disponible"
        disk = f"DISCO {metrics.disk_percent}%"
        self.metrics_label.config(text=f"{ram}\n{disk}\nCPU / RED: no disponibles")

    def add_message(self, author: str, text: str) -> None:
        self.chat.config(state="normal")
        self.chat.insert("end", f"{author}:\n{text}\n\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def add_user_message(self, text: str) -> None: self.add_message("Tú", text)
    def add_assistant_message(self, text: str) -> None: self.add_message("NYX", text)

    def render_news(self, result: NewsQueryResult) -> None:
        for widget in self.news_feed.winfo_children(): widget.destroy()
        self.news_status.config(text=" · ".join(f"{s.source_name} {'✓' if s.ok else '⚠'}" for s in result.statuses))
        if not result.items:
            tk.Label(self.news_feed, text="No hay noticias para este periodo. Revisa los avisos de fuente.", fg="#91B8CA", bg=self.PANEL, wraplength=300, justify="left").pack(pady=14)
            return
        for index, item in enumerate(result.items, 1):
            card = tk.Frame(self.news_feed, bg=self.PANEL_ALT, highlightbackground="#132C42", highlightthickness=1)
            card.pack(fill="x", pady=4)
            tk.Label(card, text=f"{index}. {item.source.upper()}  ·  {item.published_label}", fg="#5EBBFF", bg=self.PANEL_ALT, anchor="w", font=("Segoe UI", 8, "bold")).pack(fill="x", padx=10, pady=(8, 2))
            tk.Label(card, text=item.title, fg=self.WHITE, bg=self.PANEL_ALT, anchor="w", justify="left", wraplength=300, font=("Segoe UI", 9, "bold")).pack(fill="x", padx=10)
            if item.summary:
                tk.Label(card, text=item.summary[:150] + ("…" if len(item.summary) > 150 else ""), fg="#B7C6D0", bg=self.PANEL_ALT, anchor="w", justify="left", wraplength=300, font=("Segoe UI", 8)).pack(fill="x", padx=10, pady=(2, 4))
            if item.link:
                tk.Button(card, text="Abrir origen  ›", command=lambda url=item.link: self._open_news(url), bg=self.PANEL_ALT, fg="#72C7FF", relief="flat").pack(anchor="e", padx=8, pady=(0, 6))

    def show_section(self, section: str) -> None:
        if section not in self.SECTIONS: return
        self._selected_section = section
        for name, button in self._section_buttons.items(): button.config(bg="#10263A" if name == section else self.PANEL)
        if section == "Conversaciones":
            self.chat_card.grid(); self.greeting.grid_remove(); self.wave_canvas.grid_remove()
        else:
            self.chat_card.grid_remove(); self.greeting.grid(); self.wave_canvas.grid()
        if section == "Noticias" and self._on_news_refresh: self._on_news_refresh()

    def _show_dashboard(self) -> None:
        self.show_section("Inicio")

    def toggle_sidebar(self) -> None:
        if self._sidebar_visible:
            self.sidebar.grid_remove(); self._sidebar_visible = False
        else:
            self.sidebar.grid(); self._sidebar_visible = True

    def set_on_submit(self, callback: Callable[[str], None]) -> None: self._on_submit = callback
    def set_callback(self, callback: Callable[[str], None]) -> None: self.set_on_submit(callback)
    def set_voice_callback(self, callback: Callable[[], None]) -> None: self._on_voice_request = callback
    def set_news_callbacks(self, refresh: Callable[[], None], open_article: Callable[[str], None]) -> None: self._on_news_refresh, self._on_news_open = refresh, open_article
    def set_audio_callbacks(self, toggle_listening: Callable[[], None], toggle_mute: Callable[[], None]) -> None: self._on_listening_toggle, self._on_mute_toggle = toggle_listening, toggle_mute

    def enviar(self) -> None:
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, "end"); self.add_user_message(text)
            if self._on_submit: self._on_submit(text)

    def escuchar(self) -> None:
        if self._on_voice_request: self._on_voice_request()

    def refresh_news(self) -> None:
        if self._on_news_refresh: self._on_news_refresh()

    def _open_news(self, url: str) -> None:
        if self._on_news_open: self._on_news_open(url)

    def _toggle_listening(self) -> None:
        if self._on_listening_toggle: self._on_listening_toggle()

    def _toggle_mute(self) -> None:
        self._muted = not self._muted
        self.mute_button.config(text="🔇  Audio silenciado" if self._muted else "🔊  Silenciar", fg="#FFB3B3" if self._muted else self.WHITE)
        if self._on_mute_toggle: self._on_mute_toggle()

    def escribir_chat(self, text: str) -> None: self.add_assistant_message(text)
    def cambiar_color(self, color: str) -> None: self.orb_canvas.itemconfig(self.orb, fill=color)
    def cambiar_estado(self, text: str) -> None: self.add_assistant_message(text)
    def run(self) -> None: self.root.mainloop()
