"""Traduce los estados del dominio al lenguaje visual de NYX."""

from core.state import AssistantState


STATE_COLORS = {
    AssistantState.SLEEPING: "black",
    AssistantState.LISTENING: "orange",
    AssistantState.THINKING: "yellow",
    AssistantState.SPEAKING: "lime",
    AssistantState.IDLE: "#00BFFF",
}

