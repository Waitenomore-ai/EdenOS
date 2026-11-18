"""Local Eden parent PIN convenience lock.

The Linux administrator account remains the authoritative recovery path.
This PIN only gates the in-app Parent Corner.
"""
from __future__ import annotations
import hashlib, json, os, secrets, tempfile
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

def verify_pin(pin: str) -> bool:
    try:
        pin = _validate(pin)
        data = json.loads(_path().read_text(encoding="utf-8"))
        salt = bytes.fromhex(data["salt"])
        expected = data["digest"]
        return secrets.compare_digest(_digest(pin, salt), expected)
    except (OSError, ValueError, TypeError, KeyError):
        return False
