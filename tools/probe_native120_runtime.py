# Inspect a running process with query/read access and compare Native120 signature digests.
# No code is injected or changed. Optional logs use LOCALAPPDATA, capped at 1 MiB total.
import argparse
import contextlib
import ctypes
from ctypes import wintypes
import datetime
import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import tempfile

VERSION = "0.1.0"


def load_profiles(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    profiles = data["profiles"]
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= 8:
        raise ValueError("Expected between one and eight signature profiles")
    for profile in profiles:
        signatures = profile["signatures"]
        if profile["core_probe_count"] != 11 or len(signatures) != 11:
            raise ValueError("Each Native120 profile must contain all 11 core probes")
        if [s["index"] for s in signatures] != list(range(11)):
            raise ValueError("Signature indices must be unique and ordered 0 through 10")
        for signature in signatures:
            rva = int(signature["game_rva"], 0)
            length = signature["length"]
            expected = signature["expected_sha256"]
            if (not 0 <= rva < 2**32 or type(length) is not int or not 1 <= length <= 4096
                    or not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None):
                raise ValueError("Invalid signature RVA, length, or SHA256 digest")
    return profiles


def require_image(actual, expected):
    if os.path.normcase(str(Path(actual).resolve(strict=True))) != os.path.normcase(
        str(Path(expected).resolve(strict=True))
    ):
        raise ValueError("Process image path differs from the explicitly requested image")


@contextlib.contextmanager
def open_process(pid, expected_image):
    if not 0 < pid < 2**32:
        raise ValueError("PID must be a positive Windows DWORD")
    if os.name != "nt":
        raise OSError("Live process probing requires Windows")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.QueryFullProcessImageNameW.argtypes = (
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)
    )
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE

    class ModuleEntry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD), ("th32ModuleID", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD), ("GlblcntUsage", wintypes.DWORD),
            ("ProccntUsage", wintypes.DWORD), ("modBaseAddr", ctypes.c_void_p),
            ("modBaseSize", wintypes.DWORD), ("hModule", wintypes.HANDLE),
            ("szModule", wintypes.WCHAR * 256), ("szExePath", wintypes.WCHAR * 260),
        ]

    kernel.Module32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(ModuleEntry))
    kernel.Module32FirstW.restype = wintypes.BOOL
    kernel.ReadProcessMemory.argtypes = (
        wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
    )
    kernel.ReadProcessMemory.restype = wintypes.BOOL
    # Request neither VM_WRITE nor VM_OPERATION, preventing this handle from patching code.
    handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        image = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(image))
        if not kernel.QueryFullProcessImageNameW(handle, 0, image, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        require_image(image.value, expected_image)
        snapshot = kernel.CreateToolhelp32Snapshot(0x0008 | 0x0010, pid)
        if snapshot == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            module = ModuleEntry()
            module.dwSize = ctypes.sizeof(module)
            if not kernel.Module32FirstW(snapshot, ctypes.byref(module)):
                raise ctypes.WinError(ctypes.get_last_error())
            require_image(module.szExePath, expected_image)
            if module.th32ProcessID != pid or not module.modBaseAddr or not module.modBaseSize:
                raise ValueError("Invalid main module identity or bounds")
        finally:
            kernel.CloseHandle(snapshot)

        def read_rva(rva, length):
            if rva < 0 or length <= 0 or rva + length > module.modBaseSize:
                raise ValueError("Read lies outside the verified main module")
            buffer = ctypes.create_string_buffer(length)
            transferred = ctypes.c_size_t()
            if not kernel.ReadProcessMemory(
                handle, module.modBaseAddr + rva, buffer, length, ctypes.byref(transferred)
            ):
                raise ctypes.WinError(ctypes.get_last_error())
            if transferred.value != length:
                raise OSError("ReadProcessMemory returned an incomplete signature")
            return buffer.raw

        yield {"path": image.value, "base": module.modBaseAddr,
               "image_size": module.modBaseSize, "read_rva": read_rva}
    finally:
        kernel.CloseHandle(handle)


def compare_profiles(profiles, image_size, read_rva):
    results = []
    for profile in profiles:
        probes = []
        for signature in profile["signatures"]:
            rva = int(signature["game_rva"], 0)
            length = signature["length"]
            probe = {"index": signature["index"], "rva": hex(rva), "length": length}
            if rva + length > image_size:
                probe.update(match=False, cause="Outside main module bounds")
            else:
                actual = read_rva(rva, length)
                if len(actual) != length:
                    raise OSError("Signature reader returned incomplete bytes")
                actual_digest = hashlib.sha256(actual).hexdigest()
                probe.update(match=actual_digest == signature["expected_sha256"],
                             actual_sha256=actual_digest)
            probes.append(probe)
        matches = sum(probe["match"] for probe in probes)
        results.append({"profile_rva": profile["profile_rva"], "matches": matches,
                        "required_matches": 11, "probes": probes})
    compatible = any(profile["matches"] == 11 for profile in results)
    return {"classification": "signature-compatible" if compatible else "incompatible",
            "compatible": compatible, "profiles": results,
            "scope": "11 core entry probes only; later guards, patch activation and gameplay remain unverified"}


def write_report(path, report):
    target = Path(path).resolve()
    if any(target == Path(report["config"][key]).resolve() for key in ("image", "profiles")):
        raise ValueError("Output must differ from the image and signature input files")
    if not target.parent.is_dir():
        raise ValueError("Output directory must already exist")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent,
                                         prefix=target.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__ or "Read-only Native120 runtime signature probe")
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--image", required=True)
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    report = {"version": VERSION, "captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "config": vars(args), "status": "error", "access": "PROCESS_QUERY_INFORMATION | PROCESS_VM_READ"}
    logger = logging.getLogger("native120-runtime-probe")
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    handler = None
    exit_code = 1
    try:
        if args.debug:
            log_dir = Path(os.environ["LOCALAPPDATA"]) / "NarutoStorm4UltimateOverhaul" / "Logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(log_dir / "runtime-probe.log", maxBytes=512 * 1024,
                                          backupCount=1, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
            report["debug_log"] = str(log_dir / "runtime-probe.log")
        logger.debug("Startup version=%s config=%s", VERSION, vars(args))
        profiles = load_profiles(args.profiles)
        with open_process(args.pid, args.image) as process:
            logger.debug("Verified main module path=%s base=%#x size=%d",
                         process["path"], process["base"], process["image_size"])
            report["process"] = {key: value for key, value in process.items() if key != "read_rva"}
            report.update(compare_profiles(profiles, process["image_size"], process["read_rva"]))
        report["status"] = "ok"
        exit_code = 0 if report["compatible"] else 3
    except Exception as error:
        report["cause"] = str(error)
        report["error_type"] = type(error).__name__
        logger.debug("Probe failed", exc_info=True)
    report["exit_code"] = exit_code
    try:
        write_report(args.output, report)
    except Exception as error:
        print(json.dumps({"status": "error", "cause": "Cannot write report: " + str(error),
                          "probe_result": report}))
        exit_code = 1
    else:
        print(json.dumps({"status": report["status"], "classification": report.get("classification"),
                          "cause": report.get("cause"), "output": str(Path(args.output).resolve()),
                          "debug_log": report.get("debug_log"), "exit_code": exit_code}))
    logger.debug("Shutdown exit_code=%d", exit_code)
    if handler is not None:
        logger.removeHandler(handler)
        handler.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
