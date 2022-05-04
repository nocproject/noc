# ----------------------------------------------------------------------
# SLAProbe Attributes dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField, UInt64Field
from noc.sla.models.slaprobe import SLAProbe as SLAProbeModel
from noc.core.text import ch_escape


class SLAProbe(DictionaryModel):
    class Meta(object):
        name = "slaprobe"
        layout = "hashed"
        source_model = "sla.SLAProbe"
        incremental_update = True

    name = StringField()
    group = StringField()
    description = StringField()
    profile = StringField()
    type = StringField()
    target = StringField()
    service = UInt64Field()

    @classmethod
    def extract(cls, item: "SLAProbeModel"):
        return {
            "bi_id": item.bi_id,
            "name": item.name,
            "group": item.group or "",
            "description": ch_escape(item.description or ""),
            "profile": item.profile.name,
            "type": item.type,
            "target": item.target,
            "service": item.service.bi_id if item.service else 0,
        }
