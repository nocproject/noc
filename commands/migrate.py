# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Pretty command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

## Django modules
from django.core.management import call_command

if __name__ == "__main__":
    call_command("syncdb", interactive=False,
                 load_initial_data=False)
    call_command("migrate", no_initial_data=True, noinput=True,
                 ignore_ghosts=True)
