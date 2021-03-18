# ----------------------------------------------------------------------
# noc.core.mime tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.mime import ContentType


IMAGE_TYPES = {ContentType.JPEG.value, ContentType.GIF.value, ContentType.PNG.value}


@pytest.mark.parametrize("ct", list(ContentType))
def test_content_type(ct: ContentType):
    assert ct.content_type is not None


@pytest.mark.parametrize("ct", list(ContentType))
def test_is_image(ct: ContentType):
    assert ct.is_image is (ct.value in IMAGE_TYPES)
