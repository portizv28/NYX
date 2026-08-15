"""Máquina de estados de voz: reposo, conversación e interrupciones."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from voice.contracts import RecognitionResult, SpeechRecognizer
from voice.diagnostics import VoiceDiagnostics
from voice.factory import create_default_recognizer
from voice.wake_detector import WakeWordDetector
from voice.wake_engines import WakeEngine, create_default_wake_engine


@dataclass(frozen=True)
class VoiceSessionConfig:
    sleep_listen_timeout_seconds: float = 3.0
    conversation_listen_timeout_seconds: float = 4.0
    conversation_idle_seconds: float = 6.0
    interruption_listen_timeout_seconds: float = 1.0
    idle_delay_seconds: float = 0.1
    wake_cooldown_seconds: float = 2.0


class VoiceService:
    """Coordina una sola captura de micrófono en todo momento."""

    def __init__(
        self,
        on_activated: Callable[[], None],
        on_command: Callable[[str], None],
        on_command_timeout: Callable[[], None],
        on_session_started: Callable[[], None] | None = None,
        on_interruption: Callable[[], None] | None = None,
        on_listening_enabled: Callable[[bool], None] | None = None,
        listener: SpeechRecognizer | None = None,
        wake_detector: WakeWordDetector | None = None,
        wake_engine: WakeEngine | None = None,
        config: VoiceSessionConfig | None = None,
        diagnostics: VoiceDiagnostics | None = None,
    ) -> None:
        self.on_activated = on_activated
        self.on_command = on_command
        self.on_command_timeout = on_command_timeout
        self.on_session_started = on_session_started or (lambda: None)
        self.on_interruption = on_interruption or (lambda: None)
        self.on_listening_enabled = on_listening_enabled
        if listener is None:
            listener = create_default_recognizer()
        self.listener = listener
        self.wake_detector = wake_detector or WakeWordDetector()
        self.wake_engine = wake_engine or create_default_wake_engine(self.listener, self.wake_detector)
        self.config = config or VoiceSessionConfig()
        self.diagnostics = diagnostics or VoiceDiagnostics()
        self._running = threading.Event()
        self._enabled = threading.Event()
        self._enabled.set()
        self._speaking = threading.Event()
        self._session_active = threading.Event()
        self._cancel_listen = threading.Event()
        self._interrupt_notified = threading.Event()
        self._thread: threading.Thread | None = None
        self._session_deadline = 0.0
        self._last_wake_at = 0.0

    def start(self) -> None:
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="nyx-voice")
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        self._cancel_listen.set()

    @property
    def listening_enabled(self) -> bool:
        return self._enabled.is_set()

    @property
    def session_active(self) -> bool:
        return self._session_active.is_set()

    def set_listening_enabled(self, enabled: bool) -> None:
        if enabled:
            self._enabled.set()
        else:
            self._enabled.clear()
            self._session_active.clear()
            self._cancel_listen.set()
        if self.on_listening_enabled:
            self.on_listening_enabled(enabled)

    def begin_speaking(self) -> None:
        """Mantiene una escucha de interrupciones, no una escucha de órdenes."""
        self._speaking.set()
        self._cancel_listen.set()

    def end_speaking(self) -> None:
        self._speaking.clear()
        self._interrupt_notified.clear()
        self._cancel_listen.clear()

    # Alias de compatibilidad con el controlador anterior.
    def pause(self) -> None:
        self.begin_speaking()

    def resume(self) -> None:
        self.end_speaking()

    def _listen(self, timeout: float) -> str:
        started = time.monotonic()
        self._cancel_listen.clear()
        listen_result = getattr(self.listener, "listen_result", None)
        if listen_result:
            result = listen_result(cancel_event=self._cancel_listen, initial_timeout_seconds=timeout)
            text = result.text if result.is_reliable else ""
            self.diagnostics.record("transcription", duration_seconds=round(time.monotonic() - started, 3), reliable=result.is_reliable, text_length=len(text))
            return text
        result = self.listener.listen(cancel_event=self._cancel_listen, initial_timeout_seconds=timeout)
        text = result.text if isinstance(result, RecognitionResult) and result.is_reliable else str(result).strip()
        self.diagnostics.record("transcription", duration_seconds=round(time.monotonic() - started, 3), reliable=bool(text), text_length=len(text))
        return text

    def _loop(self) -> None:
        while self._running.is_set():
            if not self._enabled.is_set():
                time.sleep(self.config.idle_delay_seconds)
                continue
            try:
                if self._speaking.is_set():
                    self._monitor_interruption()
                elif self._session_active.is_set():
                    self._continue_session()
                else:
                    self._wait_for_wake_word()
            except Exception as error:
                print("Error de reconocimiento de voz:", error)
                time.sleep(1)

    def _wait_for_wake_word(self) -> None:
        event = self.wake_engine.wait(self._cancel_listen)
        if self._running.is_set() and event is not None:
            elapsed = time.monotonic() - self._last_wake_at
            if elapsed < self.config.wake_cooldown_seconds:
                self.diagnostics.record("wake_rejected", reason="cooldown", elapsed_seconds=round(elapsed, 3), engine=event.engine)
                return
            self._last_wake_at = time.monotonic()
            self.diagnostics.record("wake_accepted", engine=event.engine, confidence=event.confidence, command_included=bool(event.command))
            self._start_session(event.command)

    def _start_session(self, command: str) -> None:
        self._session_active.set()
        self._session_deadline = time.monotonic() + self.config.conversation_idle_seconds
        self.diagnostics.record("session_started", command_included=bool(command))
        self.on_activated()
        if command:
            self.on_command(command)
        else:
            self.on_session_started()

    def _continue_session(self) -> None:
        if time.monotonic() >= self._session_deadline:
            self._end_session()
            return
        text = self._listen(self.config.conversation_listen_timeout_seconds)
        if not text:
            return
        detection = self.wake_detector.detect(text)
        command = detection.command if detection else text.strip()
        if not command:
            return
        self._session_deadline = time.monotonic() + self.config.conversation_idle_seconds
        self.diagnostics.record("command_accepted", text_length=len(command))
        self.on_command(command)

    def _monitor_interruption(self) -> None:
        text = self._listen(self.config.interruption_listen_timeout_seconds)
        if text and self.wake_detector.is_interruption(text) and not self._interrupt_notified.is_set():
            self._interrupt_notified.set()
            self.on_interruption()

    def _end_session(self) -> None:
        self._session_active.clear()
        self.diagnostics.record("session_ended", reason="idle_timeout")
        self.on_command_timeout()
