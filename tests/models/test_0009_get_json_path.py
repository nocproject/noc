# ----------------------------------------------------------------------
# Test .get_json_path() method
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import get_documents


@pytest.mark.parametrize("model", [x for x in get_documents() if hasattr(x, "get_json_path")])
def test_document_get_json_path(model):
    for o in model.objects.all():
        path = o.get_json_path()
        assert path
        assert isinstance(path, str)
