# ----------------------------------------------------------------------
# ImageStore model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BinaryField, IntField, BooleanField
from mongoengine.errors import ValidationError

# NOC modules
from noc.config import config
from noc.core.mime import ContentType


def validate_content_type(value: int) -> None:
    # Check is valid content type
    try:
        ct = ContentType(value)
    except ValueError as e:
        raise ValidationError(str(e))
    # Check content type is image
    if not ct.is_image:
        raise ValidationError("Image is required")


class ImageStore(Document):
    meta = {"collection": "avatars", "strict": False, "auto_create_index": False}

    name = StringField(primary_key=True)
    type = StringField(choices=["background"])
    is_hidden = BooleanField("Is Hidden", default=False)
    content_type = IntField(validation=validate_content_type)
    file = BinaryField(max_bytes=1048576)

    def __str__(self) -> str:
        return f"{self.type}: {self.name}"

    def get_content_type(self) -> str:
        """
        Return content-type string
        :return:
        """
        return ContentType(self.content_type).content_type
