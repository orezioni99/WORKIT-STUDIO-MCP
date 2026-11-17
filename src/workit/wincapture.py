"""Capture an app's main window as PNG (Windows only, standard library only).

Used when an app has no in-app viewport capture: the picture is the app's
window exactly as the user sees it.
"""
from __future__ import annotations

import ctypes
import struct
import sys
import zlib
from ctypes import wintypes


class CaptureError(RuntimeError):
    pass


def _png(width: int, height: int, rgb: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    stride = width * 3
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        rows += rgb[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(rows), 6))
            + chunk(b"IEND", b""))


def _pids(process_names: tuple[str, ...]) -> set[int]:
    import subprocess

    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, timeout=10,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                         ).stdout.decode("mbcs", "replace")
    wanted = {name.lower() for name in process_names}
    found = set()
    for line in out.splitlines():
        cells = [cell.strip('"') for cell in line.split('","')]
        if len(cells) > 1 and cells[0].lower() in wanted:
            try:
                found.add(int(cells[1]))
            except ValueError:
                pass
    return found


def capture(process_names: tuple[str, ...], max_width: int = 1280, max_height: int = 800) -> bytes:
    """PNG bytes of the largest visible top-level window of the given processes."""
    if sys.platform != "win32":
        raise CaptureError("window capture is only available on Windows")
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    for name, restype, argtypes in (
        ("GetDC", wintypes.HDC, [wintypes.HWND]),
        ("ReleaseDC", ctypes.c_int, [wintypes.HWND, wintypes.HDC]),
        ("PrintWindow", wintypes.BOOL, [wintypes.HWND, wintypes.HDC, wintypes.UINT]),
        ("GetWindowRect", wintypes.BOOL, [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]),
        ("IsWindowVisible", wintypes.BOOL, [wintypes.HWND]),
        ("IsIconic", wintypes.BOOL, [wintypes.HWND]),
        ("GetWindow", wintypes.HWND, [wintypes.HWND, wintypes.UINT]),
        ("GetWindowThreadProcessId", wintypes.DWORD,
         [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]),
    ):
        function = getattr(user32, name)
        function.restype, function.argtypes = restype, argtypes
    for name, restype, argtypes in (
        ("CreateCompatibleDC", wintypes.HDC, [wintypes.HDC]),
        ("CreateCompatibleBitmap", wintypes.HBITMAP, [wintypes.HDC, ctypes.c_int, ctypes.c_int]),
        ("SelectObject", wintypes.HGDIOBJ, [wintypes.HDC, wintypes.HGDIOBJ]),
        ("DeleteObject", wintypes.BOOL, [wintypes.HGDIOBJ]),
        ("DeleteDC", wintypes.BOOL, [wintypes.HDC]),
        ("SetStretchBltMode", ctypes.c_int, [wintypes.HDC, ctypes.c_int]),
        ("StretchBlt", wintypes.BOOL, [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, wintypes.HDC, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, wintypes.DWORD]),
        ("GetDIBits", ctypes.c_int, [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT,
                                     wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p,
                                     wintypes.UINT]),
    ):
        function = getattr(gdi32, name)
        function.restype, function.argtypes = restype, argtypes

    pids = _pids(process_names)
    if not pids:
        raise CaptureError("the app is not running")

    best = {"hwnd": None, "area": 0, "minimised": False}

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(hwnd, _lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value not in pids or not user32.IsWindowVisible(hwnd):
            return True
        if user32.GetWindow(hwnd, 4):  # GW_OWNER: skip owned dialogs and palettes
            return True
        if user32.IsIconic(hwnd):
            best["minimised"] = True
            return True
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        area = max(0, rect.right - rect.left) * max(0, rect.bottom - rect.top)
        if area > best["area"]:
            best.update(hwnd=hwnd, area=area)
        return True

    user32.EnumWindows(visit, 0)
    hwnd = best["hwnd"]
    if not hwnd:
        if best["minimised"]:
            raise CaptureError("the app's window is minimised; restore it and try again")
        raise CaptureError("the app has no visible window")

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width, height = rect.right - rect.left, rect.bottom - rect.top
    if width <= 0 or height <= 0:
        raise CaptureError("the app's window has no size")
    scale = min(1.0, max_width / width, max_height / height)
    out_w, out_h = max(1, int(width * scale)), max(1, int(height * scale))

    screen = user32.GetDC(None)
    full_dc = gdi32.CreateCompatibleDC(screen)
    full_bmp = gdi32.CreateCompatibleBitmap(screen, width, height)
    small_dc = gdi32.CreateCompatibleDC(screen)
    small_bmp = gdi32.CreateCompatibleBitmap(screen, out_w, out_h)
    try:
        old_full = gdi32.SelectObject(full_dc, full_bmp)
        if not user32.PrintWindow(hwnd, full_dc, 2):  # PW_RENDERFULLCONTENT
            raise CaptureError("Windows refused to capture the app's window")
        old_small = gdi32.SelectObject(small_dc, small_bmp)
        gdi32.SetStretchBltMode(small_dc, 4)  # HALFTONE
        gdi32.StretchBlt(small_dc, 0, 0, out_w, out_h, full_dc, 0, 0, width, height, 0x00CC0020)
        gdi32.SelectObject(small_dc, old_small)
        gdi32.SelectObject(full_dc, old_full)

        header = struct.pack("<IiiHHIIiiII", 40, out_w, -out_h, 1, 32, 0, 0, 0, 0, 0, 0)
        info = ctypes.create_string_buffer(header, 40 + 12)
        pixels = ctypes.create_string_buffer(out_w * out_h * 4)
        if not gdi32.GetDIBits(small_dc, small_bmp, 0, out_h, pixels, info, 0):
            raise CaptureError("could not read the captured pixels")
    finally:
        gdi32.DeleteObject(full_bmp)
        gdi32.DeleteObject(small_bmp)
        gdi32.DeleteDC(full_dc)
        gdi32.DeleteDC(small_dc)
        user32.ReleaseDC(None, screen)

    bgra = pixels.raw
    rgb = bytearray(out_w * out_h * 3)
    rgb[0::3] = bgra[2::4]
    rgb[1::3] = bgra[1::4]
    rgb[2::3] = bgra[0::4]
    return _png(out_w, out_h, bytes(rgb))
