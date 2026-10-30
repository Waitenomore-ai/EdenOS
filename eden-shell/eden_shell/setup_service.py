"""Create a child account through AccountsService and PolicyKit."""

from __future__ import annotations

from pathlib import Path
import pwd

from .setup_crypto import hash_password
from .setup_model import UsernameInUseError, validate_child_profile

try:
    import gi

    gi.require_version("Gio", "2.0")
    from gi.repository import Gio, GLib
except (ImportError, ValueError) as exc:  # pragma: no cover - Debian runtime only
    raise RuntimeError("Eden setup needs the Debian GObject bindings.") from exc


_ACCOUNTS = "org.freedesktop.Accounts"
_ACCOUNTS_PATH = "/org/freedesktop/Accounts"
_USER_INTERFACE = "org.freedesktop.Accounts.User"
_TIMEOUT_MS = 60_000


def _call(connection, path: str, interface: str, method: str, parameters, reply_type):
    return connection.call_sync(
        _ACCOUNTS,
        path,
        interface,
        method,
        parameters,
        reply_type,
        Gio.DBusCallFlags.NONE,
        _TIMEOUT_MS,
        None,
    )


def _remove_new_account(connection, user_path: str) -> None:
    uid_reply = _call(
        connection,
        user_path,
        "org.freedesktop.DBus.Properties",
        "Get",
        GLib.Variant("(ss)", (_USER_INTERFACE, "Uid")),
        GLib.VariantType.new("(v)"),
    )
    uid = uid_reply.get_child_value(0).get_variant().get_uint64()
    _call(
        connection,
        _ACCOUNTS_PATH,
        _ACCOUNTS,
        "DeleteUser",
        GLib.Variant("(xb)", (uid, True)),
        None,
    )


def create_child_account(nickname: str, username: str, password: str) -> None:
    """Create one standard, password-protected user and set Eden as its session.

    The passphrase is hashed with SHA-512-crypt via OpenSSL stdin and the hash is
    sent to AccountsService. Neither the passphrase nor hash is placed in a
    process argument or written to a file. The caller should run this function
    outside the GTK main loop because PolicyKit may show an administrator
    authentication prompt.
    """
    profile = validate_child_profile(nickname, username, password, password)
    try:
        pwd.getpwnam(profile.username)
    except KeyError:
        pass
    else:
        raise UsernameInUseError("That sign-in username is already in use. Choose another name.")
    if not Path("/usr/share/xsessions/eden-child.desktop").is_file():
        raise RuntimeError("The Eden Child Session is not installed.")

    # Finish fallible local preparation before creating any system account.
    encrypted_password = hash_password(password)
    connection = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
    created = _call(
        connection,
        _ACCOUNTS_PATH,
        _ACCOUNTS,
        "CreateUser",
        GLib.Variant("(ssi)", (profile.username, profile.nickname, 0)),
        GLib.VariantType.new("(o)"),
    )
    user_path = created.unpack()[0]
    try:
        _call(
            connection,
            user_path,
            _USER_INTERFACE,
            "SetXSession",
            GLib.Variant("(s)", ("eden-child",)),
            None,
        )
        _call(
            connection,
            user_path,
            _USER_INTERFACE,
            "SetPassword",
            GLib.Variant("(ss)", (encrypted_password, "")),
            None,
        )
    except Exception as exc:
        try:
            _remove_new_account(connection, user_path)
        except Exception as cleanup_error:
            raise RuntimeError(
                "Setup stopped partway through. An adult must check the new account before use."
            ) from cleanup_error
        raise RuntimeError("Account setup did not finish; the new account was removed.") from exc

