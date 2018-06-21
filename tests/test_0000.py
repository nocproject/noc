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
