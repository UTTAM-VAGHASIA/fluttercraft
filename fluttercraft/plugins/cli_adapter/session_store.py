from __future__ import annotations

import json
import os
import time

from fluttercraft.adapters.base import AdapterMessage, AdapterSession


# ── Persistence helpers ───────────────────────────────────────────────────────


def default_sessions_path() -> str:
    return os.path.join(os.path.expanduser("~"), ".fluttercraft", "cli_sessions.json")


def save_sessions(sessions: list[AdapterSession], path: str | None = None) -> bool:
    path = path or default_sessions_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = []
        for s in sessions:
            data.append(
                {
                    "adapter_id": s.adapter_id,
                    "session_id": s.session_id,
                    "active": s.active,
                    "context": s.context,
                    "messages": [
                        {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                        for m in s.messages
                    ],
                }
            )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def load_sessions(path: str | None = None) -> list[AdapterSession]:
    path = path or default_sessions_path()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        sessions = []
        for item in data:
            msgs = [
                AdapterMessage(
                    role=m["role"],
                    content=m["content"],
                    timestamp=float(m.get("timestamp", 0.0)),
                )
                for m in item.get("messages", [])
            ]
            sessions.append(
                AdapterSession(
                    adapter_id=item.get("adapter_id", ""),
                    session_id=item.get("session_id", ""),
                    active=False,  # never restore as active
                    context=item.get("context", {}),
                    messages=msgs,
                )
            )
        return sessions
    except Exception:
        return []


def get_history_for_adapter(
    sessions: list[AdapterSession], adapter_id: str, limit: int = 20
) -> list[AdapterSession]:
    """Return the most recent sessions for a given adapter."""
    matching = [s for s in sessions if s.adapter_id == adapter_id]
    # Sort by latest message timestamp (or session order)
    def _last_ts(s: AdapterSession) -> float:
        if s.messages:
            return s.messages[-1].timestamp
        return 0.0

    return sorted(matching, key=_last_ts, reverse=True)[:limit]
