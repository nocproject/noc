# ----------------------------------------------------------------------
# sa.job application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.sa.models.job import Job
from noc.core.translation import ugettext as _


class JobApplication(ExtDocApplication):
    """
    Job application
    """

    title = "Jobs"
    menu = [_("Jobs")]
    model = Job
    glyph = "truck"
