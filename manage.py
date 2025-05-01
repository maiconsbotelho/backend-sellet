#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

import socket

def force_ipv4():
    original_getaddrinfo = socket.getaddrinfo
    def getaddrinfo_ipv4(*args, **kwargs):
        return [info for info in original_getaddrinfo(*args, **kwargs) if info[0] == socket.AF_INET]
    socket.getaddrinfo = getaddrinfo_ipv4

force_ipv4()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Adiciona o diretório base ao PYTHONPATH
    BASE_DIR = Path(__file__).resolve().parent
    sys.path.append(str(BASE_DIR))

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()