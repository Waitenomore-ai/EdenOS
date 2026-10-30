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
        'storage_scope': 'Root filesystem only; live media and other mounts are not installation measurements.',
    }


def main() -> None:
    print(json.dumps(collect_report(), indent=2))


if __name__ == '__main__':
    main()

