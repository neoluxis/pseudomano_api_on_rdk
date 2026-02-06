from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
import os

import psutil


class SystemMonitor:
    def get_status(self) -> Dict[str, Any]:
        return {
            "memory_usage": self._memory_usage(),
            "cpu_load": self._cpu_load(),
            "temperature": self._temperature(),
            "uptime": self._uptime_seconds(),
        }

    def _memory_usage(self) -> Dict[str, float]:
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "used": vm.used,
            "percent": vm.percent,
        }

    def _cpu_load(self) -> Dict[str, float]:
        try:
            load1, load5, load15 = os.getloadavg()
        except OSError:
            load1, load5, load15 = 0.0, 0.0, 0.0
        return {
            "load1": float(load1),
            "load5": float(load5),
            "load15": float(load15),
            "cpu_percent": psutil.cpu_percent(interval=None),
        }

    def _temperature(self) -> Dict[str, float]:
        temps = psutil.sensors_temperatures(fahrenheit=False) or {}
        if not temps:
            return {"current": 0.0}
        readings = [t.current for group in temps.values() for t in group if t.current is not None]
        if not readings:
            return {"current": 0.0}
        return {"current": float(max(readings))}

    def _uptime_seconds(self) -> float:
        return float(datetime.now(timezone.utc).timestamp() - psutil.boot_time())
