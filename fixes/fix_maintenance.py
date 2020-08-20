# ---------------------------------------------------------------------
# Update Maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import progressbar

# NOC module
from noc.maintenance.models.maintenance import Maintenance


def fix():
    max_value = Maintenance._get_collection().estimated_document_count()
    for m in progressbar.progressbar(Maintenance.objects.filter(), max_value=max_value):
        try:
            m.save()
        except Exception as e:
            print("[%s] %s" % (m.id, e))
