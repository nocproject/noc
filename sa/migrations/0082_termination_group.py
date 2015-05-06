# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    
    def forwards(self):
        
        # Model "TerminationGroup"
        db.create_table("sa_terminationgroup", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField("Name", max_length=64, unique=True)),
            ("description", models.TextField("Description", null=True, blank=True))
        ))        
        db.send_create_signal("sa", ["TerminationGroup"])
        TerminationGroup = db.mock_model(
            model_name="TerminationGroup",
            db_table="sa_terminationgroup", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        # Alter sa_managedobject
        db.add_column(
            "sa_managedobject", "termination_group",
            models.ForeignKey(
                TerminationGroup, verbose_name="Termination Group",
                blank=True, null=True,
                related_name="termination_set"
            )
        )
        db.add_column(
            "sa_managedobject", "service_terminator",
            models.ForeignKey(
                TerminationGroup, verbose_name="Service Terminator",
                blank=True, null=True,
                related_name="access_set"
            )
        )
        # Selector
        db.add_column(
            "sa_managedobjectselector", "filter_termination_group",
            models.ForeignKey(
                TerminationGroup,
                verbose_name=_("Filter by termination group"), null=True, blank=True,
                related_name="selector_termination_group_set"
            )
        )
        db.add_column(
            "sa_managedobjectselector", "filter_service_terminator",
            models.ForeignKey(
                TerminationGroup,
                verbose_name=_("Filter by service terminator"), null=True, blank=True,
                related_name="selector_service_terminator_set"
            )
        )
    
    def backwards(self):
        db.delete_column("sa_managedobjectselector", "filter_termination_group_id")
        db.delete_column("sa_managedobjectselector", "filter_service_terminator_id")
        db.delete_column("sa_managedobject", "termination_group_id")
        db.delete_column("sa_managedobject", "service_terminator_id")
        db.delete_table("sa_terminationgroup")
