# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:
    def forwards(self):
        return  # Conflicts with 0087_managedobjectselector_managed, skip
        from noc.sa.models.managedobjectselector import ManagedObjectSelector

        for vc_domain_id, selector_id in db.execute(
                "SELECT id, selector_id FROM vc_vcdomain WHERE selector_id IS NOT NULL"):
            mos = ManagedObjectSelector.objects.get(id=selector_id)
            mo_ids = list(mos.managed_objects.values_list("id", flat=True))
            if mo_ids:
                mo_ids = ", ".join(str(x) for x in mo_ids)
                db.execute(
                    "UPDATE sa_managedobject SET vc_domain_id=%d WHERE id IN (%s)" % (
                        vc_domain_id, mo_ids))

    def backwards(self):
        pass
