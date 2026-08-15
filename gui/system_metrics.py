"""Lectura opcional de métricas locales para la vista; no pertenece al núcleo."""

from __future__ import annotations

import ctypes
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SystemMetrics:
    memory_percent: int | None
    disk_percent: int | None


def read_system_metrics() -> SystemMetrics:
    memory_percent = None
    if hasattr(ctypes, "windll"):
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            memory_percent = int(status.dwMemoryLoad)
    usage = shutil.disk_usage(Path.cwd().anchor or "/")
    return SystemMetrics(memory_percent, int(usage.used / usage.total * 100))
