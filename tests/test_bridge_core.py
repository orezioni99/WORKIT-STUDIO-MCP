"""The wire protocol and the in-app core, exercised with a fake host app.

The fake host is a plain thread that plays the role of an app's main thread:
it owns a Bridge and calls pump() in a loop, exactly as a host timer would.
"""
import json
import socket
import threading
import time

import pytest

from workit import adapters
from workit.bridges._core import workit_core as core
from workit.registry import App

FAKE = App("fakecad", "Fake CAD", "socket", "Python", port=47990)


@pytest.fixture()
def host(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKIT_HOME", str(tmp_path))
    undo_labels = []

    def wrap(fn, label):
        undo_labels.append(label)
        return fn()

    def shoot(path, width, height):
        from workit.wincapture import _png

        with open(path, "wb") as handle:
            handle.write(_png(2, 1, b"\xff\x00\x00\x00\xff\x00"))

    bridge = core.Bridge("fakecad", FAKE.port, namespace={"model": {"walls": 3}}, wrap=wrap,
                         screenshot=shoot, info={"version": "1.2.3"})
    assert bridge.start()
    stop = threading.Event()
    main_thread = {}

    def loop():
        main_thread["id"] = threading.get_ident()
        while not stop.is_set():
            bridge.pump()
            time.sleep(0.01)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    bridge.undo_labels = undo_labels
    bridge.main_thread = main_thread
    yield bridge
    stop.set()
    thread.join(2)
    bridge.stop()


def test_ping_lists_the_instance(host):
    live = adapters.socket_instances(FAKE)
    assert len(live) == 1
    assert live[0]["app"] == "fakecad"
    assert live[0]["version"] == "1.2.3"
    assert live[0]["port"] == host.port


def test_result_variable_and_stdout(host):
    reply = adapters.execute(FAKE, "print('hello')\nresult = model['walls'] * 2", "read", 10)
    assert reply["ok"] is True
    assert reply["result"] == 6
    assert reply["stdout"].strip() == "hello"


def test_last_expression_is_the_result(host):
    reply = adapters.execute(FAKE, "x = 20\nx + 1", "read", 10)
    assert reply["result"] == 21


def test_scripts_run_on_the_host_main_thread(host):
    reply = adapters.execute(FAKE, "import threading\nthreading.get_ident()", "read", 10)
    assert reply["result"] == host.main_thread["id"]


def test_namespace_persists_between_calls(host):
    adapters.execute(FAKE, "def area(w, h):\n    return w * h", "read", 10)
    assert adapters.execute(FAKE, "area(3, 4)", "read", 10)["result"] == 12


def test_errors_come_back_with_traceback(host):
    reply = adapters.execute(FAKE, "print('before')\n1 / 0", "read", 10)
    assert reply["ok"] is False
    assert "ZeroDivisionError" in reply["error"]
    assert "<workit>" in reply["traceback"]
    assert "before" in reply["stdout"]


def test_only_modify_is_wrapped_in_undo(host):
    adapters.execute(FAKE, "1", "read", 10)
    assert host.undo_labels == []
    adapters.execute(FAKE, "1", "modify", 10, label="AI: add walls")
    assert host.undo_labels == ["AI: add walls"]


def test_non_json_results_fall_back_to_repr(host):
    reply = adapters.execute(FAKE, "result = {'obj': object(), 'n': (1, 2), 'inf': float('inf')}",
                             "read", 10)
    assert reply["result"]["n"] == [1, 2]
    assert reply["result"]["obj"].startswith("<object object")
    assert reply["result"]["inf"] == "inf"


def test_wrong_token_is_refused(host):
    with socket.create_connection(("127.0.0.1", host.port), timeout=2) as sock:
        sock.sendall(json.dumps({"op": "exec", "code": "1", "token": "nope"}).encode() + b"\n")
        reply = json.loads(sock.recv(65536).decode())
    assert reply == {"ok": False, "error": "bad token"}


def test_http_request_is_dropped_without_running_anything(host):
    """A browser posting to the port must not be able to smuggle a request in."""
    body = json.dumps({"op": "exec", "code": "model['walls'] = 99", "token": adapters.token()})
    with socket.create_connection(("127.0.0.1", host.port), timeout=2) as sock:
        sock.sendall(("POST / HTTP/1.1\r\nHost: x\r\n\r\n" + body + "\n").encode())
        assert sock.recv(65536) == b""
    assert adapters.execute(FAKE, "model['walls']", "read", 10)["result"] == 3


def test_busy_host_times_out_cleanly(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKIT_HOME", str(tmp_path))
    bridge = core.Bridge("fakecad", FAKE.port)  # nobody pumps: the "app" is frozen
    assert bridge.start()
    try:
        reply = adapters.socket_request(bridge.port, {"op": "exec", "code": "1", "timeout": 0.5}, 5)
        assert reply["ok"] is False and "timed out" in reply["error"]
    finally:
        bridge.stop()


def test_second_instance_takes_the_next_port(host):
    # In real life the second instance is another process; here we fake that by
    # hiding the first one from the per-process registry.
    core.sys.__dict__[core._REGISTRY_ATTR].pop("fakecad")
    second = core.Bridge("fakecad", FAKE.port)
    try:
        assert second.start()
        assert second.port == host.port + 1
    finally:
        second.stop()
        core.sys.__dict__[core._REGISTRY_ATTR]["fakecad"] = host


def test_wake_is_called_instead_of_polling(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKIT_HOME", str(tmp_path))
    holder = {}
    bridge = core.Bridge("fakecad", FAKE.port, wake=lambda: holder["bridge"].pump())
    holder["bridge"] = bridge
    assert bridge.start()
    try:
        assert adapters.execute(FAKE, "6 * 7", "read", 5)["result"] == 42
    finally:
        bridge.stop()


def test_screenshot_round_trip(host):
    data = adapters.screenshot(FAKE, 640, 480)
    assert data.startswith(b"\x89PNG")
