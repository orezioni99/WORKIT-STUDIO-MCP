"""Tekla Structures through its Open API (.NET), loaded with pythonnet.

The Open API talks to the running Tekla process, so nothing is installed in
Tekla itself. Needs `pip install pythonnet`.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys

from ._common import NotAvailable, main


def _bin_folder() -> str:
    override = os.environ.get("WORKIT_TEKLA_BIN")
    if override and os.path.isdir(override):
        return override
    try:  # the folder of the Tekla that is actually running
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process TeklaStructures -ErrorAction SilentlyContinue | "
             "Select-Object -First 1).Path"],
            capture_output=True, timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout.decode("utf-8", "replace").strip()
        if out and os.path.isfile(out):
            return os.path.dirname(out)
    except Exception:
        pass
    candidates = sorted(
        glob.glob(r"C:\Program Files\Tekla Structures\*\bin")
        + glob.glob(r"C:\Program Files\Tekla Structures\*\nt\bin"),
        reverse=True,
    )
    for folder in candidates:
        if os.path.isfile(os.path.join(folder, "Tekla.Structures.Model.dll")):
            return folder
    raise NotAvailable("Tekla Structures was not found. Set WORKIT_TEKLA_BIN to the "
                       "folder that holds Tekla.Structures.Model.dll.")


def _connect(app_id, request):
    try:
        import clr  # pythonnet
    except ImportError:
        raise NotAvailable("Tekla needs pythonnet: run `pip install pythonnet` in the "
                           "environment that runs WorkitStudio.") from None
    folder = _bin_folder()
    if folder not in sys.path:
        sys.path.append(folder)
    for name in ("Tekla.Structures", "Tekla.Structures.Model", "Tekla.Structures.Drawing"):
        try:
            clr.AddReference(name)
        except Exception:
            if name != "Tekla.Structures.Drawing":
                raise
    import Tekla.Structures as ts
    import Tekla.Structures.Geometry3d as tsg
    import Tekla.Structures.Model as tsm

    model = tsm.Model()
    if not model.GetConnectionStatus():
        raise NotAvailable("Tekla Structures is not running with a model open.")

    def wrap(fn, label):
        value = fn()
        model.CommitChanges()
        return value

    info = {"app": "tekla", "model": str(model.GetInfo().ModelName),
            "path": str(model.GetInfo().ModelPath)}
    scope = {"model": model, "ts": ts, "tsm": tsm, "tsg": tsg, "clr": clr}
    return scope, info, wrap


if __name__ == "__main__":
    main(_connect)
