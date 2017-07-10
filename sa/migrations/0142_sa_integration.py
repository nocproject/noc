from south.db import db
from django.db import models
from noc.core.model.fields import DocumentReferenceField, TagsField

class Migration:
    def forwards(self):
        # Administrative Domain
        db.add_column(
            "sa_administrativedomain",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True)
        )
        db.add_column(
            "sa_administrativedomain",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True)
        )
        db.add_column(
            "sa_administrativedomain",
            "bi_id",
            models.IntegerField(null=True, blank=True)
        )
        # AuthProfile
        db.add_column(
            "sa_authprofile",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True)
        )
        db.add_column(
            "sa_authprofile",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True)
        )
        db.add_column(
            "sa_authprofile",
            "bi_id",
            models.IntegerField(null=True, blank=True)
        )
        db.add_column(
            "sa_authprofile",
            "tags",
            TagsField("Tags", null=True, blank=True)
        )
        # ManagedObject
        db.add_column(
            "sa_managedobject",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True)
        )
        db.add_column(
            "sa_managedobject",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True)
        )
        db.add_column(
            "sa_managedobject",
            "bi_id",
            models.IntegerField(null=True, blank=True)
        )
        db.add_column(
            "sa_managedobject",
            "escalation_policy",
            models.CharField(
                "Escalation Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable"),
                    ("P", "From Profile")
                ],
                default="P"
            )
        )
        db.add_column(
            "sa_managedobject",
            "tt_system",
            DocumentReferenceField("self", null=True, blank=True)
        )
        db.add_column(
            "sa_managedobject",
            "tt_system_id",
            models.CharField(max_length=64, null=True, blank=True)
        )
        # ManagedObjectProfile
        db.add_column(
            "sa_managedobjectprofile",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "bi_id",
            models.IntegerField(null=True, blank=True)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "escalation_policy",
            models.CharField(
                "Escalation Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="E"
            )
        )
        # TerminationGroup
        db.add_column(
            "sa_terminationgroup",
            "remote_system",
            DocumentReferenceField("self", null=True, blank=True)
        )
        db.add_column(
            "sa_terminationgroup",
            "remote_id",
            models.CharField(max_length=64, null=True, blank=True)
        )
        db.add_column(
            "sa_terminationgroup",
            "bi_id",
            models.IntegerField(null=True, blank=True)
        )

    def backwards(self):
        # Administrative Domain
        db.delete_column("sa_administrativedomain", "remote_system")
        db.delete_column("sa_administrativedomain", "remote_id")
        db.delete_column("sa_administrativedomain", "bi_id")
        # AuthProfile
        db.delete_column("sa_authprofile", "remote_system")
        db.delete_column("sa_authprofile", "remote_id")
        db.delete_column("sa_authprofile", "bi_id")
        db.delete_column("sa_authprofile", "tags")
        # ManagedObject
        db.delete_column("sa_managedobject", "remote_system")
        db.delete_column("sa_managedobject", "remote_id")
        db.delete_column("sa_managedobject", "bi_id")
        db.delete_column("sa_managedobject", "escalation_policy")
        db.delete_column("sa_managedobject", "tt_system")
        db.delete_column("sa_managedobject", "tt_system_id")
        # ManagedObjectProfile
        db.delete_column("sa_managedobjectprofile", "remote_system")
        db.delete_column("sa_managedobjectprofile", "remote_id")
        db.delete_column("sa_managedobjectprofile", "bi_id")
        db.delete_column("sa_managedobjectprofile", "escalation_policy")
        # TerminationGroup
        db.delete_column("sa_terminationgroup", "remote_system")
        db.delete_column("sa_terminationgroup", "remote_id")
        db.delete_column("sa_terminationgroup", "bi_id")
