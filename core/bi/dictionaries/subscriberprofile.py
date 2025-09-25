# ----------------------------------------------------------------------
# Interface Profile dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.crm.models.subscriberprofile import SubscriberProfile as SubscriberProfileModel


class SubscriberProfile(DictionaryModel):
    class Meta(object):
        name = "subscriberprofile"
        layout = "hashed"
        source_model = "crm.SubscriberProfile"
        incremental_update = True

    id = StringField()
    name = StringField()
    description = StringField()
    glyph = StringField()

    @classmethod
    def extract(cls, item: "SubscriberProfileModel"):
        return {
            "id": str(item.id),
            "name": item.name,
            "description": item.description or "",
            "glyph": item.glyph or "",
        }
