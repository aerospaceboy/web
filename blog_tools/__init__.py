"""Tools for maintaining the AerospaceBoy Halo blog."""

import sys


def configure_console():
    """Keep Chinese JSON output readable through Windows pipes and terminals."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
