# ----------------------------------------------------------------------
# sa integration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField, TagsField


class Migration(BaseMigration):
    def migrate(self):
        # Administrative Domain
        self.db.add_column(
            "sa_administrativedomain",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True),
        )
        self.db.add_column(
            "sa_administrativedomain",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True),
        )
        self.db.add_column(
            "sa_administrativedomain", "bi_id", models.IntegerField(null=True, blank=True)
        )
        # AuthProfile
        self.db.add_column(
            "sa_authprofile", "remote_system", DocumentReferenceField("self", null=True, blank=True)
        )
        self.db.add_column(
            "sa_authprofile", "remote_id", models.CharField(max_length=64, null=True, blank=True)
        )
        self.db.add_column("sa_authprofile", "bi_id", models.IntegerField(null=True, blank=True))
        self.db.add_column("sa_authprofile", "tags", TagsField("Tags", null=True, blank=True))
        # ManagedObject
        self.db.add_column(
            "sa_managedobject",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject", "remote_id", models.CharField(max_length=64, null=True, blank=True)
        )
        self.db.add_column("sa_managedobject", "bi_id", models.IntegerField(null=True, blank=True))
        self.db.add_column(
            "sa_managedobject",
            "escalation_policy",
            models.CharField(
                "Escalation Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable"), ("P", "From Profile")],
                default="P",
            ),
        )
        self.db.add_column(
            "sa_managedobject", "tt_system", DocumentReferenceField("self", null=True, blank=True)
        )
        self.db.add_column(
            "sa_managedobject",
            "tt_system_id",
            models.CharField(max_length=64, null=True, blank=True),
        )
        # ManagedObjectProfile
        self.db.add_column(
            "sa_managedobjectprofile",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobjectprofile", "bi_id", models.IntegerField(null=True, blank=True)
        )
        self.db.add_column(
            "sa_managedobjectprofile",
            "escalation_policy",
            models.CharField(
                "Escalation Policy",
                max_length=1,
                choices=[("E", "Enable"), ("D", "Disable")],
                default="E",
            ),
        )
        # TerminationGroup
        self.db.add_column(
            "sa_terminationgroup",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True),
        )
        self.db.add_column(
            "sa_terminationgroup",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True),
        )
        self.db.add_column(
            "sa_terminationgroup", "bi_id", models.IntegerField(null=True, blank=True)
        )
