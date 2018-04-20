# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Drop VRF.is_active
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
=======
##----------------------------------------------------------------------
## Drop VRF.is_active
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
from noc.ip.models import *


class Migration:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def forwards(self):
        db.drop_column("ip_vrf", "is_active")

    def backwards(self):
        db.create_column("ip_vrf", "is_active",
                         models.BooleanField(default=True))
