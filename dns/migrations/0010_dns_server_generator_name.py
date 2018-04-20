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
        db.add_column("dns_dnsserver", "generator_name",
            models.CharField("Generator", max_length=32,
                default="BINDv9"))
        db.execute("UPDATE dns_dnsserver SET generator_name=%s",
            ["BINDv9"])

    def backwards(self):
        raise NotImplementedError()
