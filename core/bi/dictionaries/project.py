# ----------------------------------------------------------------------
# Project dictionary
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import DictionaryModel
from noc.core.clickhouse.fields import StringField
from noc.project.models.project import Project as ProjectModel


class Project(DictionaryModel):
    class Meta(object):
        name = "project"
        layout = "hashed"
        source_model = "project.Project"
        incremental_update = True

    id = StringField()
    name = StringField()

    @classmethod
    def extract(cls, item: "ProjectModel"):
        return {
            "id": str(item.id),
            "name": item.name,
        }
