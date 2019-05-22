# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Database migrations
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_database_migrations(database):
    """
    Force database migrations
    :param database:
    :return:
    """
    from south.management.commands.migrate import Command

    cmd = Command()
    cmd.execute(no_initial_data=True, noinput=True, ignore_ghosts=True)
