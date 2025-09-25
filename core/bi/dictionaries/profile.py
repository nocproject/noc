# ----------------------------------------------------------------------
# Profile dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.sa.models.profile import Profile as ProfileModel


class Profile(DictionaryModel):
    class Meta(object):
        name = "profile"
        layout = "hashed"
        source_model = "sa.Profile"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "ProfileModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
