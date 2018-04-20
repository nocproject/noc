# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:

    def forwards(self):
        db.add_column(
            "sa_managedobjectselector", "filter_managed",
            models.NullBooleanField(
                "Filter by Is Managed",
                null=True, blank=True, default=True)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectselector", "filter_managed")
