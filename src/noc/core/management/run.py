# ----------------------------------------------------------------------
# CLI Command Runner
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Is a separate module.
# Using in base.py changes BaseCommand to __main__.BaseCommand
# and affects loader.
# @todo: Move to package entrypont when packaging will be ready.
if __name__ == "__main__":
    # Python modules
    import sys
    from typing import NoReturn

    # NOC modules
    from noc.core.management.base import command_loader

    def die(msg: str) -> NoReturn:
        print(msg)
        sys.exit(1)

    if len(sys.argv) < 2:
        die("Command not set")

    # Find command
    try:
        cmd = command_loader[sys.argv[1]]
    except KeyError:
        die(f"Invalid command: {sys.argv[1]}")

    sys.exit(cmd().run_from_argv(sys.argv[2:]))
