"""Hash an account passphrase without putting it in process arguments or files."""

from __future__ import annotations

import subprocess


def hash_password(password: str) -> str:
    """Return a salted SHA-512-crypt hash suitable for AccountsService."""
    # OpenSSL's stdin protocol reads a line, so reject characters that could
    # truncate or otherwise change the passphrase before creating a hash.
    if not password or not password.isprintable():
        raise ValueError("The passphrase must contain only printable characters.")
    result = subprocess.run(
        ["/usr/bin/openssl", "passwd", "-6", "-stdin"],
        input=password + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    hashed = result.stdout.strip()
    if not hashed.startswith("$6$"):
        raise RuntimeError("OpenSSL did not return a SHA-512-crypt password hash.")
    return hashed
