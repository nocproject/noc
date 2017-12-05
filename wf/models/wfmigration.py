# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Workflow Migration model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField,
                                ReferenceField, ListField,
                                EmbeddedDocumentField)
# NOC modules
from .state import State


class MigrationItem(EmbeddedDocument):
    from_state = ReferenceField(State)
    to_state = ReferenceField(State)
    is_active = BooleanField()
    description = StringField()


class WFMigration(Document):
    meta = {
        "collection": "wfmigrations",
        "strict": False,
        "auto_create_index": False
    }
    name = StringField(unique=True)
    description = StringField()
    migrations = ListField(EmbeddedDocumentField(MigrationItem))

    def __unicode__(self):
        return self.name

    def get_translation_map(self, target_wf):
        """
        Returns from_state -> to_state translation
        :param target_wf: Target workflow
        :return:
        """
        return dict((m.from_state, m.to_state)
                    for m in self.migrations
                    if m.is_active and m.to_state.workflow == target_wf)
