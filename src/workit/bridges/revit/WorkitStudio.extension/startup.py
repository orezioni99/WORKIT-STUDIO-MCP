# -*- coding: utf-8 -*-
"""WorkitStudio for Revit, as a pyRevit extension.

pyRevit runs this file when it loads. It adds two endpoints to pyRevit Routes
(turn Routes on in pyRevit Settings):
    GET  http://127.0.0.1:48884/workit/ping
    POST http://127.0.0.1:48884/workit/exec
Routes itself has no login, so every exec request must carry the WorkitStudio
token (a secret in the user's home folder that web pages cannot read).
"""
import clr
from pyrevit import HOST_APP, routes

import workit_core as core  # from this extension's lib folder

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit import DB, UI  # noqa: E402

api = routes.API("workit")
_scope = {"__name__": "__workit__", "DB": DB, "UI": UI}


@api.route("/ping")
def ping(uiapp):
    uidoc = uiapp.ActiveUIDocument
    doc = uidoc.Document if uidoc else None
    return routes.make_response(data={"ok": True, "result": {
        "app": "revit", "protocol": core.PROTOCOL, "version": HOST_APP.version,
        "document": doc.Title if doc else None,
    }})


@api.route("/exec", methods=["POST"])
def execute(request, uiapp):
    data = request.data or {}
    if not core._same(core.text_type(data.get("token", "")), core.text_type(core.read_token())):
        return routes.make_response(data={"ok": False, "error": "bad token"})
    uidoc = uiapp.ActiveUIDocument
    doc = uidoc.Document if uidoc else None
    _scope.update(uiapp=uiapp, app=uiapp.Application, uidoc=uidoc, doc=doc)
    wrap = None
    if data.get("mode") == "modify" and doc is not None:
        def wrap(fn, label):
            transaction = DB.Transaction(doc, label)
            transaction.Start()
            try:
                value = fn()
            except BaseException:
                transaction.RollBack()
                raise
            transaction.Commit()
            return value
    reply = core.run_script(data.get("code") or "", _scope, wrap,
                            data.get("label") or "WorkitStudio")
    # Routes serialises with IronPython's json, which fails on U+0080..U+00FF:
    # hand it ASCII-only JSON text; the server decodes the extra layer.
    return routes.make_response(data=core.ascii_json(reply))
