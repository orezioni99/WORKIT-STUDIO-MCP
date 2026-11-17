"""Drive Windows apps through COM automation: no add-in to install.

One runner covers AutoCAD and its clones, Navisworks, SOLIDWORKS, Inventor,
CATIA, Solid Edge, MicroStation, ETABS / SAP2000 and Robot. Each "flavour"
only decides which names the script gets and how a change is grouped for undo.
"""
from __future__ import annotations

import sys
import time

from ..registry import find
from ._common import NotAvailable, main

if sys.platform != "win32":  # pragma: no cover
    def _connect(app_id, request):
        raise NotAvailable("COM automation only exists on Windows.")
else:
    import pythoncom
    import pywintypes
    import win32com.client
    import win32com.client.dynamic
    from win32com.client import VARIANT

    _FILTER_KEEPALIVE = []

    def _install_filter():
        """Register a COM message filter: when the app answers "busy, call later"
        (a command is running, a dialog is open) COM waits and retries instead of
        failing with "call was rejected by callee". pywin32 cannot implement
        IMessageFilter, so the tiny COM object is built by hand with ctypes."""
        try:
            import ctypes
            from ctypes import wintypes

            HRESULT = ctypes.c_long
            this = ctypes.c_void_p

            def query_interface(_self, _iid, out):
                out[0] = _self
                return 0

            def add_ref(_self):
                return 2

            def release(_self):
                return 1

            def handle_incoming(_self, _call_type, _task, _tick, _info):
                return 0  # SERVERCALL_ISHANDLED

            def retry_rejected(_self, _task, tick, reject_type):
                if reject_type == 2 and tick < 120000:  # SERVERCALL_RETRYLATER
                    return 250  # try again in 250 ms
                return 0xFFFFFFFF  # give up

            def message_pending(_self, _task, _tick, _pending_type):
                return 2  # PENDINGMSG_WAITDEFPROCESS

            prototypes = (
                (ctypes.WINFUNCTYPE(HRESULT, this, ctypes.c_void_p,
                                    ctypes.POINTER(ctypes.c_void_p)), query_interface),
                (ctypes.WINFUNCTYPE(wintypes.ULONG, this), add_ref),
                (ctypes.WINFUNCTYPE(wintypes.ULONG, this), release),
                (ctypes.WINFUNCTYPE(wintypes.DWORD, this, wintypes.DWORD, ctypes.c_void_p,
                                    wintypes.DWORD, ctypes.c_void_p), handle_incoming),
                (ctypes.WINFUNCTYPE(wintypes.DWORD, this, ctypes.c_void_p, wintypes.DWORD,
                                    wintypes.DWORD), retry_rejected),
                (ctypes.WINFUNCTYPE(wintypes.DWORD, this, ctypes.c_void_p, wintypes.DWORD,
                                    wintypes.DWORD), message_pending),
            )
            callbacks = [prototype(function) for prototype, function in prototypes]
            table = (ctypes.c_void_p * len(callbacks))(
                *[ctypes.cast(callback, ctypes.c_void_p) for callback in callbacks])
            instance = ctypes.pointer(ctypes.cast(table, ctypes.c_void_p))
            previous = ctypes.c_void_p()
            register = ctypes.windll.ole32.CoRegisterMessageFilter
            register.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
            register.restype = HRESULT
            outcome = register(ctypes.cast(instance, ctypes.c_void_p), ctypes.byref(previous))
            _FILTER_KEEPALIVE.extend([callbacks, table, instance])
            return outcome == 0
        except Exception:
            return False

    def _attach(app, progids):
        installed = False
        for progid in progids:
            try:
                clsid = pywintypes.IID(progid)
            except pythoncom.com_error:
                continue
            installed = True
            try:
                unknown = pythoncom.GetActiveObject(clsid)
            except pythoncom.com_error:
                continue
            return win32com.client.dynamic.Dispatch(
                unknown.QueryInterface(pythoncom.IID_IDispatch)
            )
        if not installed:
            raise NotAvailable(f"{app.name} does not seem to be installed on this PC "
                               f"(no COM class {', '.join(progids)}).")
        raise NotAvailable(f"{app.name} is not running. {app.setup}")

    # ------------------------------------------------------------- helpers
    def doubles(*values):
        """COM array of doubles. doubles(0, 0, 0) or doubles([x1, y1, x2, y2])."""
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = values[0]
        return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in values])

    def point(x=0.0, y=0.0, z=0.0):
        """A 3D point as the COM array AutoCAD-style APIs expect."""
        return doubles(x, y, z)

    def ints(values):
        """COM array of 16-bit integers (DXF group codes for selection filters)."""
        return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_I2, [int(v) for v in values])

    def variants(values):
        """COM array of variants (values for selection filters, attribute data)."""
        return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, list(values))

    def objects(values):
        """COM array of objects (for AddRegion, CopyObjects and similar)."""
        return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(values))

    nothing = VARIANT(pythoncom.VT_DISPATCH, None)

    def _try(getter, default=None):
        try:
            return getter()
        except Exception:
            return default

    def _base(app_obj):
        return {
            "app": app_obj, "VARIANT": VARIANT, "pythoncom": pythoncom, "win32com": win32com,
            "doubles": doubles, "point": point, "ints": ints, "variants": variants,
            "objects": objects, "nothing": nothing, "time": time,
        }

    # ------------------------------------------------------------ flavours
    def _autocad(app_obj):
        doc = _try(lambda: app_obj.ActiveDocument)
        scope = _base(app_obj)

        def wait_idle(timeout=120.0):
            """Block until AutoCAD has finished the commands sent to it."""
            end = time.time() + timeout
            while time.time() < end:
                state = _try(lambda: app_obj.GetAcadState())
                if state is None or _try(lambda: state.IsQuiescent, True):
                    return True
                time.sleep(0.2)
            return False

        def command(text, timeout=120.0):
            """Type a command line into AutoCAD, e.g. command('_.ZOOM _E')."""
            target = app_obj.ActiveDocument
            if not text.endswith(("\n", " ")):
                text += "\n"
            target.SendCommand(text)
            return wait_idle(timeout)

        def entities(space=None):
            """List every entity in model space (or the space you pass)."""
            space = space if space is not None else app_obj.ActiveDocument.ModelSpace
            return [space.Item(index) for index in range(space.Count)]

        scope.update(acad=app_obj, doc=doc, ms=_try(lambda: doc.ModelSpace) if doc else None,
                     command=command, wait_idle=wait_idle, entities=entities)

        def wrap(fn, label):
            target = _try(lambda: app_obj.ActiveDocument)
            if target is None:
                return fn()
            _try(target.StartUndoMark)
            try:
                return fn()
            finally:
                _try(target.EndUndoMark)

        info = {"name": _try(lambda: app_obj.Name), "version": _try(lambda: app_obj.Version),
                "document": _try(lambda: doc.Name) if doc else None,
                "documents": _try(lambda: app_obj.Documents.Count)}
        return scope, info, wrap

    def _navisworks(app_obj):
        scope = _base(app_obj)
        state = _try(lambda: app_obj.State())
        scope.update(nw=app_obj, state=state)
        info = {"file": _try(lambda: state.CurrentFileName) if state is not None else None}
        return scope, info, None

    def _solidworks(app_obj):
        model = _try(lambda: app_obj.ActiveDoc)
        scope = _base(app_obj)
        scope.update(sw=app_obj, model=model)

        def wrap(fn, label):
            extension = _try(lambda: app_obj.ActiveDoc.Extension)
            started = extension is not None and _try(extension.StartRecordingUndoObject) is not None
            try:
                return fn()
            finally:
                if started:
                    _try(lambda: extension.FinishRecordingUndoObject2(label, False))

        info = {"version": _try(lambda: app_obj.RevisionNumber),
                "document": _try(lambda: model.GetTitle) if model is not None else None}
        return scope, info, wrap

    def _inventor(app_obj):
        doc = _try(lambda: app_obj.ActiveDocument)
        scope = _base(app_obj)
        scope.update(inv=app_obj, doc=doc, tg=_try(lambda: app_obj.TransientGeometry))

        def wrap(fn, label):
            target = _try(lambda: app_obj.ActiveDocument)
            if target is None:
                return fn()
            transaction = _try(lambda: app_obj.TransactionManager.StartTransaction(target, label))
            try:
                value = fn()
            except BaseException:
                if transaction is not None:
                    _try(transaction.Abort)
                raise
            if transaction is not None:
                _try(transaction.End)
            return value

        info = {"version": _try(lambda: app_obj.SoftwareVersion.DisplayVersion),
                "document": _try(lambda: doc.DisplayName) if doc is not None else None}
        return scope, info, wrap

    def _catia(app_obj):
        doc = _try(lambda: app_obj.ActiveDocument)
        scope = _base(app_obj)
        scope.update(catia=app_obj, doc=doc)
        return scope, {"document": _try(lambda: doc.Name) if doc is not None else None}, None

    def _solidedge(app_obj):
        doc = _try(lambda: app_obj.ActiveDocument)
        scope = _base(app_obj)
        scope.update(se=app_obj, doc=doc)
        return scope, {"document": _try(lambda: doc.Name) if doc is not None else None}, None

    def _microstation(app_obj):
        scope = _base(app_obj)
        scope.update(ustn=app_obj, dgn=_try(lambda: app_obj.ActiveDesignFile),
                     model=_try(lambda: app_obj.ActiveModelReference))
        return scope, {"file": _try(lambda: app_obj.ActiveDesignFile.Name)}, None

    def _csi(app_obj):
        scope = _base(app_obj)
        sap = _try(lambda: app_obj.SapModel)
        scope.update(etabs=app_obj, sap=sap, SapModel=sap)
        return scope, {"file": _try(lambda: sap.GetModelFilename)}, None

    def _robot(app_obj):
        scope = _base(app_obj)
        project = _try(lambda: app_obj.Project)
        scope.update(robot=app_obj, project=project,
                     structure=_try(lambda: project.Structure) if project is not None else None)
        return scope, {"file": _try(lambda: project.FileName) if project is not None else None}, None

    _FLAVOURS = {
        "autocad": _autocad, "navisworks": _navisworks, "solidworks": _solidworks,
        "inventor": _inventor, "catia": _catia, "solidedge": _solidedge,
        "microstation": _microstation, "csi": _csi, "robot": _robot,
    }

    def _connect(app_id, request):
        app = find(app_id)
        pythoncom.CoInitialize()
        retrying = _install_filter()
        app_obj = _attach(app, app.extra["progids"])
        flavour = _FLAVOURS[app.extra.get("flavour", app.id)]
        scope, info, wrap = flavour(app_obj)
        info = dict(info or {}, app=app.id, retries_when_busy=retrying)
        return scope, info, wrap


if __name__ == "__main__":
    main(_connect)
