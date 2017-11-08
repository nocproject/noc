# -*- coding: utf-8 -*-

from django.db import models
from south.db import db


class Migration:
    depends_on = [
        ("main", "0013_notifications")
    ]

    def forwards(self):
        # Get data
        pc = {}
        for vc_domain_id, selector_id, key, value in db.execute(
                "SELECT vc_domain_id,selector_id,key,value FROM vc_vcdomainprovisioningconfig"):
            if vc_domain_id not in pc:
                pc[vc_domain_id] = {}
            if selector_id not in pc[vc_domain_id]:
                pc[vc_domain_id][selector_id] = {"enable": True,
                                                 "tagged_ports": None}
            pc[vc_domain_id][selector_id][key] = value
            # Alter
        db.add_column("vc_vcdomainprovisioningconfig", "is_enabled",
                      models.BooleanField("Is Enabled", default=True))
        db.add_column("vc_vcdomainprovisioningconfig", "tagged_ports",
                      models.CharField("Tagged Ports", max_length=256, null=True,
                                       blank=True))
        NotificationGroup = db.mock_model(model_name='NotificationGroup', db_table='main_notificationgroup',
                                          db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("vc_vcdomainprovisioningconfig",
                      "notification_group", models.ForeignKey(NotificationGroup,
                                                              verbose_name="Notification Group", null=True,
                                                              blank=True))
        db.delete_column("vc_vcdomainprovisioningconfig", "key")
        db.delete_column("vc_vcdomainprovisioningconfig", "value")
        # Save data
        db.execute("DELETE FROM vc_vcdomainprovisioningconfig")
        for vc_domain_id, c in pc.items():
            for selector_id, v in c.items():
                db.execute(
                    "INSERT INTO vc_vcdomainprovisioningconfig(vc_domain_id,selector_id,is_enabled,tagged_ports,notification_group_id) VALUES(%s,%s,%s,%s,%s)"
                    ,
                    [vc_domain_id, selector_id,
                     v["enable"].lower() in ["true", "t"],
                     v["tagged_ports"], None])
        db.execute("COMMIT")

    def backwards(self):
        "Write your backwards migration here"
