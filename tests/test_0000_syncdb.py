# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Database syncdb
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest


@pytest.mark.usefixtures("database")
def test_syncdb(database):
    """
    Force database migrations
    :param database:
    :return:
    """
    from django.core.management import call_command

    call_command("syncdb", interactive=False, load_initial_data=False)
