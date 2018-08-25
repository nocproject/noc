# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# pyRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField
from mongoengine.errors import ValidationError


class PyRule(Document):
    meta = {
        "collection": "pyrules",
        "strict": False,
        "auto_create_index": False
    }
    # Relative modules name
    # i.e. test.mod1 for noc.pyrules.test.mod1
    name = StringField(unique=True, regex="^([a-zA-Z_][a-zA-Z0-9_]*)(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")
    #
    description = StringField()
    # Source code
    source = StringField()
    #
    last_changed = DateTimeField()

    def __unicode__(self):
        return self.name

    @property
    def full_name(self):
        return "noc.pyrules.%s" % self.name

    def clean(self):
        # Check source code
        try:
            compile(str(self.source), "<string>", "exec")
        except SyntaxError as e:
            raise ValidationError("Cannot compile pyRule: %s" % e)
        # Update last_changed
        self.last_changed = datetime.datetime.now()
