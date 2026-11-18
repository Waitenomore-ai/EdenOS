"""Local Eden parent PIN convenience lock.

The Linux administrator account remains the authoritative recovery path.
This PIN only gates the in-app Parent Corner.
"""
from __future__ import annotations
import hashlib, json, os, secrets, tempfile, time
from pathlib import Path

def _path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "eden-os" / "parent-pin.json"

def _validate(pin: str) -> str:
    if not isinstance(pin, str) or not pin.isdigit() or not 4 <= len(pin) <= 8:
        raise ValueError("Use a parent PIN with 4 to 8 numbers.")
    return pin

def has_pin() -> bool:
    try:
        data = json.loads(_path().read_text(encoding="utf-8"))
        return data.get("version") == 1 and isinstance(data.get("salt"), str) and isinstance(data.get("digest"), str)
    except (OSError, ValueError, TypeError):
        return False

def _digest(pin: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 200_000).hex()

def set_pin(pin: str) -> None:
    pin = _validate(pin)
    destination = _path()
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    salt = secrets.token_bytes(16)
    payload = {"version": 1, "salt": salt.hex(), "digest": _digest(pin, salt)}
    fd, temp = tempfile.mkstemp(prefix=".eden-parent-pin-", dir=destination.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(payload, out, sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, destination)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def _attempt_path() -> Path:
    return _path().with_name("parent-pin-attempts.json")

def _attempt_state() -> dict:
    try:
        state = json.loads(_attempt_path().read_text(encoding="utf-8"))
        if isinstance(state, dict):
            return state
    except (OSError, ValueError, TypeError):
        pass
    return {}

def _save_attempts(state: dict) -> None:
    destination = _attempt_path()
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".eden-parent-attempt-", dir=destination.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(state, out, sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def verify_pin(pin: str) -> bool:
    try:
        pin = _validate(pin)
        data = json.loads(_path().read_text(encoding="utf-8"))
        attempts = _attempt_state()
        now = time.time()
        locked_until = float(attempts.get("locked_until", 0))
        if locked_until > now:
            return False
        salt = bytes.fromhex(data["salt"])
        expected = data["digest"]
        valid = secrets.compare_digest(_digest(pin, salt), expected)
        if valid:
            _save_attempts({"failures": 0, "locked_until": 0})
            return True
        failures = int(attempts.get("failures", 0)) + 1 if not locked_until or locked_until > now else 1
        if failures >= 5:
            _save_attempts({"failures": 0, "locked_until": now + 60})
        else:
            _save_attempts({"failures": failures, "locked_until": 0})
        return False
    except (OSError, ValueError, TypeError, KeyError):
        return False
