# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmClass model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import hashlib
## NOC modules
import noc.lib.nosql as nosql
from alarmseverity import AlarmSeverity
from alarmclassvar import AlarmClassVar
from datasource import DataSource
from alarmrootcausecondition import AlarmRootCauseCondition
from alarmclasscategory import AlarmClassCategory
from alarmclassjob import AlarmClassJob


class AlarmClass(nosql.Document):
    """
    Alarm class
    """
    meta = {
        "collection": "noc.alarmclasses",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)
    # Create or not create separate Alarm
    # if is_unique is True and there is active alarm
    # Do not create separate alarm if is_unique set
    is_unique = nosql.BooleanField(default=False)
    # List of var names to be used as discriminator key
    discriminator = nosql.ListField(nosql.StringField())
    # Can alarm status be cleared by user
    user_clearable = nosql.BooleanField(default=True)
    # Default alarm severity
    default_severity = nosql.PlainReferenceField(AlarmSeverity)
    #
    datasources = nosql.ListField(nosql.EmbeddedDocumentField(DataSource))
    vars = nosql.ListField(nosql.EmbeddedDocumentField(AlarmClassVar))
    # Text messages
    # alarm_class.text -> locale -> {
    #     "subject_template" -> <template>
    #     "body_template" -> <template>
    #     "symptoms" -> <text>
    #     "probable_causes" -> <text>
    #     "recommended_actions" -> <text>
    # }
    text = nosql.DictField(required=True)
    # Flap detection
    flap_condition = nosql.StringField(
        required=False,
        choices=[("none", "none"), ("count", "count")],
        default=None)
    flap_window = nosql.IntField(required=False, default=0)
    flap_threshold = nosql.FloatField(required=False, default=0)
    # RCA
    root_cause = nosql.ListField(
        nosql.EmbeddedDocumentField(AlarmRootCauseCondition))
    # Job descriptioons
    jobs = nosql.ListField(nosql.EmbeddedDocumentField(AlarmClassJob))
    #
    category = nosql.ObjectIdField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = AlarmClassCategory.objects.filter(name=c_name).first()
        if not c:
            c = AlarmClassCategory(name=c_name)
            c.save()
        self.category = c.id
        super(AlarmClass, self).save(*args, **kwargs)

    def get_discriminator(self, vars):
        """
        Calculate discriminator hash

        :param vars: Dict of vars
        :returns: Discriminator hash
        """
        if vars:
            ds = sorted(str(vars[n]) for n in self.discriminator)
            return hashlib.sha1("\x00".join(ds)).hexdigest()
        else:
            return hashlib.sha1("").hexdigest()
