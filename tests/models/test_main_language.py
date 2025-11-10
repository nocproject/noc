# ----------------------------------------------------------------------
# main.Language tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.main.models.language import Language


@pytest.mark.parametrize(
    ("name", "rec_name", "native_name"),
    [("English", "English", "English"), ("Russian", "Russian", "Русский")],
)
def test_default_language(name, rec_name, native_name):
    lang = Language.objects.get(name=name)
    assert lang.name == rec_name
    assert lang.native_name == native_name


@pytest.mark.parametrize(
    "data",
    [
        {"name": "Tengwar", "native_name": "Quenya", "is_active": False},
        {"name": "Klingon", "native_name": "Klingon", "is_active": True},
    ],
)
def test_insert(data):
    lang = Language(**data)
    lang.save()
    for k in data:
        assert getattr(lang, k) == data[k]
    # Fetch record
    lang = Language.objects.get(name=data["name"])
    assert lang.pk
    for k in data:
        assert getattr(lang, k) == data[k]
    # Delete record
    lang.delete()
