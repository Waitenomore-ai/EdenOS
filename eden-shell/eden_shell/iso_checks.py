"""Static boot-file checks; these do not prove a machine can boot the ISO."""
from pathlib import Path
import re
import struct
import sys


def has_dual_firmware_boot(report: str) -> bool:
    platforms = set(re.findall(
        r'^\s*El Torito boot img\s*:\s*\d+\s+(BIOS|UEFI)\s+y(?:\s|$)',
        report, re.MULTILINE))
    return platforms == {'BIOS', 'UEFI'}


def is_amd64_efi_application(binary: bytes) -> bool:
    if len(binary) < 64 or binary[:2] != b'MZ':
        return False
    pe = struct.unpack_from('<I', binary, 0x3c)[0]
    optional = pe + 24
    if pe < 64 or optional + 70 > len(binary):
        return False
    optional_size = struct.unpack_from('<H', binary, pe + 20)[0]
    return (
        binary[pe:pe + 4] == b'PE\x00\x00'
        and struct.unpack_from('<H', binary, pe + 4)[0] == 0x8664
        and optional_size >= 70
        and optional + optional_size <= len(binary)
        and struct.unpack_from('<H', binary, optional)[0] == 0x20b
        and struct.unpack_from('<H', binary, optional + 68)[0] == 10
    )


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: python3 -m eden_shell.iso_checks BOOT_CATALOG BOOTX64.EFI', file=sys.stderr)
        return 1
    try:
        report = Path(sys.argv[1]).read_text(encoding='utf-8')
        binary = Path(sys.argv[2]).read_bytes()
    except (OSError, UnicodeError) as exc:
        print(f'Cannot inspect boot files: {exc}', file=sys.stderr)
        return 1
    if not has_dual_firmware_boot(report):
        print('Missing bootable BIOS or UEFI image in the ISO catalogue.', file=sys.stderr)
        return 1
    if not is_amd64_efi_application(binary):
        print('Fallback loader does not have an amd64 EFI application header.', file=sys.stderr)
        return 1
    print('BIOS/UEFI catalogue entries and amd64 EFI header checked; hardware boot remains unverified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
