"""Controlador de escritorio: adapta eventos al estado central de NYX."""

from __future__ import annotations

import threading

from app.composition import create_desktop_brain
from core.state import AssistantState, MicrophoneState
from core.store import AssistantSnapshot, StateStore
from gui.orb import NyxOrb
from gui.window import NyxWindow
from voice.service import VoiceService
from voice.speaker import SpeechService


class NYX:
    """Compone UI y servicios sin introducir lógica de negocio en las vistas."""

    _ACTIVITIES = {
        AssistantState.SLEEPING: "Esperando la palabra de activación",
        AssistantState.LISTENING: "Escuchando al usuario",
        AssistantState.THINKING: "Procesando la solicitud",
        AssistantState.SPEAKING: "Comunicando una respuesta",
        AssistantState.IDLE: "Disponible",
    }

    def __init__(self) -> None:
        self.window = NyxWindow()
        self.window.root.withdraw()
        self.orb = NyxOrb()
        self.state_store = StateStore()
        self.brain = create_desktop_brain(self.state_store)
        self.speech = SpeechService()
        self._unsubscribe_state = self.state_store.subscribe(self._render_snapshot, emit_current=True)

        self.voice = VoiceService(
            on_activated=lambda: self._on_ui(self._wake),
            on_command=lambda text: self._on_ui(lambda: self._receive_voice_command(text)),
            on_command_timeout=lambda: self._on_ui(self.sleep),
            on_session_started=lambda: self._on_ui(self._acknowledge_session),
            on_interruption=lambda: self._on_ui(self._interrupt_speech),
            on_listening_enabled=self._on_listening_changed,
        )

        self.window.set_on_submit(self.process_text)
        self.window.set_voice_callback(self._request_voice_listening)
        self.orb.set_callback(self.open_window)
        self.window.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self._set_state(AssistantState.SLEEPING)
        self.voice.start()

    @property
    def state(self) -> AssistantState:
        return self.state_store.snapshot().state

    def _on_ui(self, callback) -> None:
        self.window.root.after(0, callback)

    def _render_snapshot(self, snapshot: AssistantSnapshot) -> None:
        self._on_ui(lambda: self._render_snapshot_on_ui(snapshot))

    def _render_snapshot_on_ui(self, snapshot: AssistantSnapshot) -> None:
        self.window.render_state(snapshot.state)
        self.window.render_system_state(snapshot)
        self.orb.render_state(snapshot.state)

    def _set_state(self, state: AssistantState) -> None:
        self.state_store.update(state=state, activity=self._ACTIVITIES[state])

    def _on_listening_changed(self, enabled: bool) -> None:
        self.state_store.update(
            microphone=MicrophoneState.ACTIVE if enabled else MicrophoneState.INACTIVE,
            activity="Esperando la palabra de activación" if enabled else "Escucha desactivada",
        )

    def open_window(self) -> None:
        self.window.root.deiconify()
        self.orb.hide()

    def open_control_center(self, section: str = "Sistema") -> None:
        self.open_window()
        self.window.show_section(section)

    def close_window(self) -> None:
        self.window.root.withdraw()
        self.orb.show()
        self.sleep()

    def _wake(self) -> None:
        self._set_state(AssistantState.LISTENING)

    def _receive_voice_command(self, text: str) -> None:
        self.window.add_user_message(text)
        self.process_text(text)

    def _acknowledge_session(self) -> None:
        self.window.add_assistant_message("Sí, señorito Pablo.")
        self._begin_speaking("Sí, señorito Pablo.")

    def _request_voice_listening(self) -> None:
        self.voice.set_listening_enabled(True)
        self._set_state(AssistantState.LISTENING)

    def toggle_listening(self) -> bool:
        enabled = not self.voice.listening_enabled
        self.voice.set_listening_enabled(enabled)
        if enabled:
            self._set_state(AssistantState.SLEEPING)
        return enabled

    def process_text(self, text: str) -> None:
        if not text.strip():
            return
        self._set_state(AssistantState.THINKING)
        threading.Thread(target=self._process_in_background, args=(text,), daemon=True, name="nyx-brain").start()

    def _process_in_background(self, text: str) -> None:
        try:
            response = self.brain.procesar(text)
        except Exception as error:
            print("Error procesando la solicitud:", error)
            response = "Lo siento, he tenido un problema al procesar esa solicitud."
        self._on_ui(lambda: self._show_response(response))

    def _show_response(self, response: str) -> None:
        self.window.add_assistant_message(response)
        self._begin_speaking(response)

    def _begin_speaking(self, text: str) -> None:
        self._set_state(AssistantState.SPEAKING)
        self.voice.begin_speaking()
        self.speech.speak(text, on_complete=lambda succeeded: self._on_ui(lambda: self._speech_finished(succeeded)))

    def _interrupt_speech(self) -> None:
        self.speech.stop()
        self.voice.end_speaking()
        self._set_state(AssistantState.LISTENING)
        self.window.add_assistant_message("De acuerdo, Pablo.")

    def _speech_finished(self, succeeded: bool = True) -> None:
        self.voice.end_speaking()
        if not succeeded:
            self.state_store.update(activity="Síntesis de voz no disponible; respuesta mostrada en el centro de control")
        if self.voice.session_active:
            self._set_state(AssistantState.LISTENING)
        else:
            self.sleep()

    def sleep(self) -> None:
        self._set_state(AssistantState.SLEEPING)

    def status_text(self) -> str:
        snapshot = self.state_store.snapshot()
        return f"Estado: {snapshot.state.value} | Actividad: {snapshot.activity} | Modelo: {snapshot.active_model}"

    def request_open_control_center(self, section: str = "Sistema") -> None:
        self._on_ui(lambda: self.open_control_center(section))

    def request_toggle_listening(self) -> None:
        self._on_ui(self.toggle_listening)

    def request_shutdown(self) -> None:
        self._on_ui(self.shutdown)

    def shutdown(self) -> None:
        self.voice.stop()
        self._unsubscribe_state()
        self.window.root.destroy()

    # API anterior para no romper lanzadores y extensiones existentes.
    def abrir(self) -> None:
        self.open_window()

    def cerrar(self) -> None:
        self.close_window()

    def despertar(self, text: str = "") -> None:
        self._wake()
        if text.strip():
            self._receive_voice_command(text)

    def procesar(self, text: str) -> None:
        self.process_text(text)

    def dormir(self) -> None:
        self.sleep()

    def run(self) -> None:
        self.window.run()
