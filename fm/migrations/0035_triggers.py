# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.fm.models import *

class Migration:
    depends_on = (
        ("main", "0037_template"),
    )

    def forwards(self):
        Template = db.mock_model(model_name="Template",
            db_table="main_template", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        
        ManagedObjectSelector = db.mock_model(model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)

        NotificationGroup = db.mock_model(model_name="NotificationGroup",
            db_table="main_notificationgroup", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)

        PyRule = db.mock_model(model_name="PyRule",
            db_table="main_pyrule", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        
        db.create_table("fm_eventtrigger", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=64, unique=True)),
            ("is_enabled", models.BooleanField(_("Is Enabled"), default=True)),
            ("event_class_re", models.CharField(_("Event class RE"), max_length=256)),
            ("condition", models.CharField(_("Condition"), max_length=256, default="True")),
            ("time_pattern", models.ForeignKey(TimePattern,
                                          verbose_name=_("Time Pattern"),
                                          null=True, blank=True)),
            ("selector", models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Managed Object Selector"),
                                 null=True, blank=True)),
            ("notification_group", models.ForeignKey(NotificationGroup,
                                           verbose_name=_("Notification Group"),
                                           null=True, blank=True)),
            ("template", models.ForeignKey(NOCTemplate,
                                 verbose_name=_("Template"),
                                 null=True, blank=True)),
            ("pyrule", models.ForeignKey(PyRule,
                               verbose_name=_("pyRule"),
                               null=True, blank=True))
        ))

        db.create_table("fm_alarmtrigger", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("name", models.CharField(_("Name"), max_length=64, unique=True)),
            ("is_enabled", models.BooleanField(_("Is Enabled"), default=True)),
            ("alarm_class_re", models.CharField(_("Alarm class RE"), max_length=256)),
            ("condition", models.CharField(_("Condition"), max_length=256, default="True")),
            ("time_pattern", models.ForeignKey(TimePattern,
                                          verbose_name=_("Time Pattern"),
                                          null=True, blank=True)),
            ("selector", models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Managed Object Selector"),
                                 null=True, blank=True)),
            ("notification_group", models.ForeignKey(NotificationGroup,
                                           verbose_name=_("Notification Group"),
                                           null=True, blank=True)),
            ("template", models.ForeignKey(NOCTemplate,
                                 verbose_name=_("Template"),
                                 null=True, blank=True)),
            ("pyrule", models.ForeignKey(PyRule,
                               verbose_name=_("pyRule"),
                               null=True, blank=True))
        ))

        db.send_create_signal("main", ["EventTrigger", "AlarmTrigger"])
    
    def backwards(self):
        db.delete_table("fm_eventtrigger")
        db.delete_table("fm_alarmtrigger")
