# ----------------------------------------------------------------------
# ImageStore model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, BooleanField, FileField
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.mime import ContentType
from noc.config import config


def validate_content_type(value: int) -> None:
    # Check is valid content type
    try:
        ct = ContentType(value)
    except ValueError as e:
        raise ValidationError(str(e))
    # Check content type image
    if not ct.is_image:
        raise ValidationError("Image is required")


@on_delete_check(check=[("inv.ConfiguredMap", "background_image")])
class ImageStore(Document):
    meta = {"collection": "imagestore", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    type = StringField(choices=["background"], default="background")
    is_hidden = BooleanField("Is Hidden", default=False)
    content_type = IntField(validation=validate_content_type)
    file = FileField(max_bytes=config.web.max_image_size, required=False)

    def __str__(self) -> str:
        return f"{self.type}: {self.name}"

    def get_content_type(self) -> str:
        """
        Return content-type string
        :return:
        """
        if not self.content_type:
            return ""
        return ContentType(self.content_type).content_type
