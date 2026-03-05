from __future__ import annotations

import subprocess
import time
import uuid
from typing import Callable

from fluttercraft.adapters.base import AdapterMessage, AdapterSession, CLIAdapter
from fluttercraft.adapters.detect import binary_on_path


class ClaudeAdapter(CLIAdapter):
    """Adapter for Claude Code CLI (``claude`` binary)."""

    @property
    def id(self) -> str:
        return "claude"

    @property
    def name(self) -> str:
        return "Claude Code"

    @property
    def icon(self) -> str:
        return "◆"

    def detect(self) -> bool:
        return binary_on_path("claude")

    def start_session(self, context: dict | None = None) -> AdapterSession:
        session = AdapterSession(
            adapter_id=self.id,
            session_id=str(uuid.uuid4()),
            active=True,
            context=context or {},
        )
        # If we have project context, prepend a system message
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
        """Run ``claude --print <message>`` and stream output line by line."""
        session.messages.append(
            AdapterMessage(role="user", content=message, timestamp=time.time())
        )

        full_output: list[str] = []
        try:
            proc = subprocess.Popen(
                ["claude", "--print", message],
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
            on_chunk("[error] claude binary not found")
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
