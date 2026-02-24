from __future__ import annotations

import asyncio

import pytest

from fluttercraft.core.events import (
    ErrorEvent,
    EventBus,
    FileChangedEvent,
    FocusChangedEvent,
    GitChangedEvent,
    RefreshNeededEvent,
    SessionUpdateEvent,
)


# ── subscribe / publish ───────────────────────────────────────────────────────


def test_subscribe_and_publish():
    bus = EventBus()
    received = []

    bus.subscribe(FileChangedEvent, lambda e: received.append(e))
    bus.publish(FileChangedEvent(path="/lib/main.dart"))

    assert len(received) == 1
    assert received[0].path == "/lib/main.dart"
    assert received[0].change_type == "modified"


def test_unsubscribe_stops_delivery():
    bus = EventBus()
    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(FileChangedEvent, handler)
    bus.unsubscribe(FileChangedEvent, handler)
    bus.publish(FileChangedEvent(path="/lib/main.dart"))

    assert received == []


def test_unsubscribe_not_registered_is_noop():
    bus = EventBus()

    def handler(event):
        pass

    bus.unsubscribe(FileChangedEvent, handler)  # should not raise


def test_multiple_handlers_all_called():
    bus = EventBus()
    log = []

    bus.subscribe(GitChangedEvent, lambda e: log.append("a"))
    bus.subscribe(GitChangedEvent, lambda e: log.append("b"))
    bus.publish(GitChangedEvent(branch="main", has_changes=True))

    assert log == ["a", "b"]


def test_wrong_event_type_not_delivered():
    bus = EventBus()
    received = []

    bus.subscribe(FileChangedEvent, lambda e: received.append(e))
    bus.publish(GitChangedEvent(branch="main"))

    assert received == []


# ── silent degradation ────────────────────────────────────────────────────────


def test_bad_handler_does_not_crash_bus():
    bus = EventBus()
    good = []

    def bad_handler(event):
        raise RuntimeError("boom")

    bus.subscribe(FileChangedEvent, bad_handler)
    bus.subscribe(FileChangedEvent, lambda e: good.append(e))
    bus.publish(FileChangedEvent(path="/x.dart"))

    assert len(good) == 1


def test_duplicate_subscribe_fires_once():
    bus = EventBus()
    count = []

    def handler(event):
        count.append(1)

    bus.subscribe(FileChangedEvent, handler)
    bus.subscribe(FileChangedEvent, handler)  # duplicate — ignored
    bus.publish(FileChangedEvent(path="/x.dart"))

    assert len(count) == 1


# ── all event types ───────────────────────────────────────────────────────────


def test_all_event_types_publish_without_error():
    bus = EventBus()

    bus.publish(FileChangedEvent(path="/a.dart"))
    bus.publish(GitChangedEvent(branch="dev", has_changes=False))
    bus.publish(FocusChangedEvent(plugin_id="fvm"))
    bus.publish(RefreshNeededEvent(scope="header"))
    bus.publish(ErrorEvent(source="test", message="oops"))
    bus.publish(SessionUpdateEvent(session_id="s1", status="started"))


def test_event_dataclass_defaults():
    e = GitChangedEvent()
    assert e.branch == ""
    assert e.has_changes is False

    r = RefreshNeededEvent()
    assert r.scope == "all"

    err = ErrorEvent(source="x", message="y")
    assert err.exc is None


# ── async handlers ────────────────────────────────────────────────────────────


def test_async_publish_awaits_handlers():
    bus = EventBus()
    results = []

    async def async_handler(event):
        results.append(event.path)

    bus.subscribe(FileChangedEvent, async_handler)

    asyncio.run(bus.publish_async(FileChangedEvent(path="/async.dart")))

    assert results == ["/async.dart"]


def test_async_publish_mixed_handlers():
    bus = EventBus()
    log = []

    def sync_handler(event):
        log.append("sync")

    async def async_handler(event):
        log.append("async")

    bus.subscribe(FileChangedEvent, sync_handler)
    bus.subscribe(FileChangedEvent, async_handler)

    asyncio.run(bus.publish_async(FileChangedEvent(path="/x.dart")))

    assert log == ["sync", "async"]


def test_async_bad_handler_does_not_crash():
    bus = EventBus()
    good = []

    async def bad_async(event):
        raise ValueError("async boom")

    bus.subscribe(FileChangedEvent, bad_async)
    bus.subscribe(FileChangedEvent, lambda e: good.append(e))

    asyncio.run(bus.publish_async(FileChangedEvent(path="/x.dart")))

    assert len(good) == 1
