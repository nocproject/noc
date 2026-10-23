# ----------------------------------------------------------------------
# Avatar model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BinaryField, IntField
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


class Avatar(Document):
    meta = {"collection": "avatars", "strict": False, "auto_create_index": False}

    user_id = StringField(primary_key=True)
    content_type = IntField(validation=validate_content_type)
    data = BinaryField(max_bytes=config.ui.max_avatar_size)

    def __str__(self) -> str:
        return self.user_id

    def get_content_type(self) -> str:
        """
        Return content-type string
        :return:
        """
        return ContentType(self.content_type).content_type
