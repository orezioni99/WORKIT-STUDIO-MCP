"""Archicad through its built-in JSON API, plus Tapir add-on commands.

Archicad has no in-app script engine to send code to, so the script is Python
that runs here and calls Archicad through the `ac` helper.
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

from ._common import NotAvailable, main

FIRST_PORT = 19723
LAST_PORT = 19743


class ArchicadError(RuntimeError):
    pass


class Archicad:
    """ac.cmd('API.GetAllElements')  /  ac.tapir('GetProjectInfo')"""

    def __init__(self, port: int):
        self.port = port
        self.url = f"http://127.0.0.1:{port}"

    def post(self, payload: dict, timeout: float = 600.0) -> dict:
        request = urllib.request.Request(
            self.url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as reply:
                return json.loads(reply.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as error:
            raise ArchicadError(f"Archicad did not answer on port {self.port}: {error}") from None

    def cmd(self, name: str, parameters: dict | None = None, timeout: float = 600.0):
        """Run a built-in JSON API command, e.g. 'API.GetAllElements'. Returns its result."""
        payload = {"command": name}
        if parameters is not None:
            payload["parameters"] = parameters
        reply = self.post(payload, timeout)
        if not reply.get("succeeded"):
            error = reply.get("error") or {}
            raise ArchicadError(f"{name} failed: {error.get('message', reply)} "
                                f"(code {error.get('code')})")
        return reply.get("result", {})

    def tapir(self, name: str, parameters: dict | None = None, timeout: float = 600.0):
        """Run a Tapir add-on command, e.g. 'GetProjectInfo', 'CreateColumns'."""
        result = self.cmd("API.ExecuteAddOnCommand", {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": name},
            "addOnCommandParameters": parameters or {},
        }, timeout)
        response = result.get("addOnCommandResponse", result)
        if isinstance(response, dict) and response.get("success") is False:
            error = response.get("error") or {}
            raise ArchicadError(f"Tapir {name} failed: {error.get('message', response)}")
        return response

    def has_tapir(self) -> bool:
        try:
            reply = self.cmd("API.IsAddOnCommandAvailable", {
                "addOnCommandId": {"commandNamespace": "TapirCommand",
                                   "commandName": "GetAddOnVersion"}})
            return bool(reply.get("available"))
        except ArchicadError:
            return False

    def guids(self, elements) -> list[str]:
        """Flatten [{'elementId': {'guid': ...}}, ...] into a list of guid strings."""
        return [item["elementId"]["guid"] for item in elements]


def _open_ports() -> list[int]:
    found = []
    for port in range(FIRST_PORT, LAST_PORT + 1):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                found.append(port)
        except OSError:
            continue
    return found


def _connect(app_id, request):
    wanted = request.get("instance")
    ports = [int(wanted)] if wanted else _open_ports()
    last = None
    for port in ports:
        ac = Archicad(port)
        try:
            product = ac.cmd("API.GetProductInfo", timeout=5)
        except ArchicadError as error:
            last = error
            continue
        info = {"app": "archicad", "port": port, "version": product.get("version"),
                "build": product.get("buildNumber"), "language": product.get("languageCode"),
                "tapir": ac.has_tapir()}
        return {"ac": ac, "ArchicadError": ArchicadError, "json": json}, info, None
    raise NotAvailable(
        "Archicad is not answering on ports 19723-19743. Start Archicad and open a project"
        + (f" ({last})" if last else ".")
    )


if __name__ == "__main__":
    main(_connect)
