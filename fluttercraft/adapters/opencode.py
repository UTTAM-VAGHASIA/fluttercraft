from __future__ import annotations

import subprocess
import time
import uuid
from typing import Callable

from fluttercraft.adapters.base import AdapterMessage, AdapterSession, CLIAdapter
from fluttercraft.adapters.detect import binary_on_path


class OpenCodeAdapter(CLIAdapter):
    """Adapter for OpenCode CLI (``opencode`` binary)."""

    @property
    def id(self) -> str:
        return "opencode"

    @property
    def name(self) -> str:
        return "OpenCode"

    @property
    def icon(self) -> str:
        return "◉"

    def detect(self) -> bool:
        return binary_on_path("opencode")

    def start_session(self, context: dict | None = None) -> AdapterSession:
        session = AdapterSession(
            adapter_id=self.id,
            session_id=str(uuid.uuid4()),
            active=True,
            context=context or {},
        )
        if context:
            preamble = self.build_context_prompt(context)
            if preamble:
                session.messages.append(
                    AdapterMessage(role="system", content=preamble, timestamp=time.time())
                )
        return session

    def send(
        self,
        session: AdapterSession,
        message: str,
        on_chunk: Callable[[str], None],
        on_done: Callable[[], None] | None = None,
    ) -> None:
        """Run ``opencode run <message>`` and stream output line by line."""
        session.messages.append(
            AdapterMessage(role="user", content=message, timestamp=time.time())
        )

        full_output: list[str] = []
        try:
            proc = subprocess.Popen(
                ["opencode", "run", message],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                chunk = line.rstrip("\n")
                full_output.append(chunk)
                on_chunk(chunk)
            proc.wait()
        except FileNotFoundError:
            on_chunk("[error] opencode binary not found")
        except Exception as exc:
            on_chunk(f"[error] {exc}")

        reply = "\n".join(full_output)
        session.messages.append(
            AdapterMessage(role="assistant", content=reply, timestamp=time.time())
        )
        if on_done:
            on_done()

    def stop_session(self, session: AdapterSession) -> None:
        session.active = False
