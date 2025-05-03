# ----------------------------------------------------------------------
# Test __str__ method
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import get_models, get_documents


@pytest.mark.parametrize("model", get_models())
def test_model_str(model):
    for o in model.objects.all():
        assert str(o)


@pytest.mark.parametrize("model", get_documents())
def test_document_str(model):
    for o in model.objects.all():
        assert isinstance(str(o), str)
