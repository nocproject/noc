# ----------------------------------------------------------------------
# noc.core.debug tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from io import StringIO

# Third-party modules
import pytest

# NOC modules
from noc.core.debug import ErrorReport


def test_error_report():
    stream = StringIO()
    logger = logging.Logger(__name__ + "::test_error_report")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream))
    with pytest.raises(ValueError), ErrorReport(logger=logger):
        raise ValueError("Ошибка--@!@--")
    report = stream.getvalue()
    assert "@!@" in report
    assert "ValueError" in report
    assert "stream" in report
