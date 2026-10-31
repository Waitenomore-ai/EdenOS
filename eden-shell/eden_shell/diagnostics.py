"""Read-only, local system evidence. No identifiers or network requests."""
import json
from pathlib import Path
import re
import shutil

from .version import build_label


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8').strip()
    except (OSError, UnicodeError):
        return ''


def assess_storage(total: int, free: int) -> dict:
    used = total - free
    return {'total_bytes': total, 'used_bytes': used, 'free_bytes': free,
            'within_budget': used <= 20 * 2**30 and free >= 6 * 2**30}


def is_live_session(root: Path = Path('/')) -> bool:
    return (root / 'run/live/medium').is_dir()


def graphics_devices(root: Path = Path('/')) -> list[dict[str, str]]:
    """Return non-identifying DRM device/driver details for support reports."""
    drm = root / 'sys/class/drm'
    devices: list[dict[str, str]] = []
    try:
        entries = sorted(drm.glob('card[0-9]'))
    except OSError:
        entries = []
    for card in entries:
        if not card.is_dir():
            continue
        device = card / 'device'
        record = {'card': card.name}
        record['driver'] = 'unknown'
        record['status'] = _read(card / 'status') or 'unknown'
        try:
            record['driver'] = (device / 'driver').resolve().name
        except OSError:
            pass
        for field, filename in (('vendor', 'vendor'), ('device', 'device')):
            value = _read(device / filename)
            if value:
                record[field] = value
        name = _read(device / 'uevent')
        if name:
            model = re.search(r'^PCI_SLOT_NAME=(.+)$', name, re.M)
            if model:
                record['pci_slot'] = model.group(1)
        devices.append(record)
    return devices


def graphics_boot_flags(root: Path = Path('/')) -> list[str]:
    """Expose only graphics-related kernel flags, never root or identity data."""
    cmdline = _read(root / 'proc/cmdline')
    allowed = ('nomodeset', 'radeon.', 'amdgpu.', 'drm.debug')
    return [token for token in cmdline.split() if token == 'nomodeset' or token.startswith(allowed[1:])]


def collect_report(root: Path = Path('/')) -> dict:
    memory = re.search(r'^MemTotal:\s+(\d+) kB$', _read(root / 'proc/meminfo'), re.M)
    cpu = re.search(r'^model name\s*:\s*(.+)$', _read(root / 'proc/cpuinfo'), re.M)
    usage = shutil.disk_usage(root)
    return {
        'build': build_label(root / 'etc/eden-os/build.json'),
        'live_session': is_live_session(root),
        'hardware_model': _read(root / 'sys/class/dmi/id/product_name') or 'unknown',
        'firmware_bits': _read(root / 'sys/firmware/efi/fw_platform_size') or 'unknown',
        'cpu': cpu.group(1) if cpu else 'unknown',
        'memory_bytes': int(memory.group(1)) * 1024 if memory else None,
        'storage': assess_storage(usage.total, usage.free),
        'graphics': graphics_devices(root),
        'graphics_boot_flags': graphics_boot_flags(root),
        'storage_scope': 'Root filesystem only; live media and other mounts are not installation measurements.',
    }


def main() -> None:
    print(json.dumps(collect_report(), indent=2))


if __name__ == '__main__':
    main()
