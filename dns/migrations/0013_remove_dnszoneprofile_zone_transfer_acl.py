# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.delete_column("dns_dnszoneprofile", "zone_transfer_acl")

    def backwards(self):
        db.add_column("dns_dnszoneprofile", "zone_transfer_acl",
            models.CharField("named zone transfer ACL", max_length=64,
                default="acl-transfer"))
