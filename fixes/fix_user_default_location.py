# ---------------------------------------------------------------------
# Update segment redundancy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.aaa.models.user import User


def fix():
    for up in User.objects.filter():
        up.heatmap_lat = config.web.heatmap_lat
        up.heatmap_lon = config.web.heatmap_lon
        up.heatmap_zoom = config.web.heatmap_zoom
        up.save()
