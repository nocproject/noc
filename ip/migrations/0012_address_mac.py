# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db
# NOC modules
from noc.core.model.fields import MACField
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db
## NOC modules
from noc.lib.fields import MACField
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Migration:
    depends_on=(
        ("sa","0007_managed_object"),
    )
    def forwards(self):
        ManagedObject=db.mock_model(model_name="ManagedObject",db_table="sa_managedobject",db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("ip_ipv4address","mac",MACField("MAC",null=True,blank=True))
        db.add_column("ip_ipv4address","managed_object",models.ForeignKey(ManagedObject,null=True,blank=True))
        db.add_column("ip_ipv4address","auto_update_mac",models.BooleanField("Auto Update MAC",default=False))
<<<<<<< HEAD

    def backwards(self):
        db.drop_column("ip_ipv4address","managed_object_id")
        db.drop_column("ip_ipv4address","mac")
        db.drop_column("ip_ipv4address","auto_update_mac")
=======
    
    def backwards(self):
        db.drop_column("ip_ipv4address","managed_object_id")
        db.drop_column("ip_ipv4address","mac")
        db.drop_column("ip_ipv4address","auto_update_mac")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
