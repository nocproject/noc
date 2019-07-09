# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test .get_json_path() method
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


@pytest.mark.parametrize("model", [x for x in get_documents() if hasattr(x, "get_json_path")])
def test_document_get_json_path(model):
    for o in model.objects.all():
        path = o.get_json_path()
        assert path
        assert isinstance(path, six.string_types)
