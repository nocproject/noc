# ----------------------------------------------------------------------
# TTSystem loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.project import ProjectModel
from noc.project.models.project import Project


class ProjectLoader(BaseLoader):
    name = "project"
    model = Project
    data_model = ProjectModel
    fields = ["id", "name", "code", "description"]
