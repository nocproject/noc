# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.debug tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
import pytest
from six.moves import StringIO

# NOC modules
from noc.core.debug import ErrorReport


def test_error_report():
    stream = StringIO()
    logger = logging.Logger(__name__ + "::test_error_report")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream))
    with pytest.raises(ValueError):
        with ErrorReport(logger=logger):
            raise ValueError("Ошибка--@!@--")
    report = stream.getvalue()
    assert "@!@" in report
    assert "ValueError" in report
    assert "stream" in report
