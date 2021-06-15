# ----------------------------------------------------------------------
# MIME Content Types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from enum import IntEnum
from typing import Optional


class ContentType(IntEnum):
    # Application
    OCTET_STREAM = 0
    # Image
    JPEG = 100
    GIF = 101
    PNG = 102
    # Text
    CSV = 201
    # Vendor
    MS_EXCEL = 1001

    @property
    def content_type(self) -> Optional[str]:
        return _CONTENT_TYPE.get(self.value)

    @property
    def is_image(self):
        return self.value in _IMAGE_TYPE

    @classmethod
    def from_content_type(cls, ct: str) -> Optional["ContentType"]:
        return _R_CONTENT_TYPE.get(ct)


_IMAGE_TYPE = {ContentType.JPEG.value, ContentType.GIF.value, ContentType.PNG.value}

_CONTENT_TYPE = {
    # Application types
    ContentType.OCTET_STREAM.value: "application/octet-stream",
    ContentType.CSV.value: "text/csv",
    ContentType.MS_EXCEL.value: "application/vnd.ms-excel",
    # Images
    ContentType.JPEG.value: "image/jpeg",
    ContentType.GIF.value: "image/gif",
    ContentType.PNG.value: "image/png",
}

_R_CONTENT_TYPE = {_CONTENT_TYPE[ct]: ContentType(ct) for ct in _CONTENT_TYPE}
