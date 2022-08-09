# ----------------------------------------------------------------------
# DiagnosticConfig dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.sa.models.objectdiagnosticconfig import ObjectDiagnosticConfig as ObjectDiagnosticConfigModel


class ObjectDiagnosticConfig(DictionaryModel):
    class Meta(object):
        name = "objectdiagnosticconfig"
        layout = "hashed"
        source_model = "sa.ObjectDiagnosticConfig"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "ObjectDiagnosticConfigModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
