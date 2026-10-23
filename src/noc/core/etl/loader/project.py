# ----------------------------------------------------------------------
# TTSystem loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.project import Project
from noc.project.models.project import Project as ProjectModel


class ProjectLoader(BaseLoader):
    name = "project"
    model = ProjectModel
    data_model = Project
