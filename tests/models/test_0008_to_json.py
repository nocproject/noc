# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test .to_json() method
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import pytest
import six

# NOC modules
from .util import get_documents


@pytest.mark.parametrize(
    "model", [x for x in get_documents() if hasattr(x, "to_json") and hasattr(x, "get_json_path")]
)
def test_document_to_json(model):
    for o in model.objects.all():
        j = o.to_json()
        assert j
        assert isinstance(j, six.string_types)
