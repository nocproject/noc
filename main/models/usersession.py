# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UserSession model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField


class UserSession(Document):
    meta = {
        "collection": "noc.user_sessions",
        "strict": False
    }
    session_key = StringField(primary_key=True)
    user_id = IntField()

    @classmethod
    def register(cls, session_key, user):
        UserSession(session_key=session_key,
                    user_id=user.id).save(force_insert=True)

    @classmethod
    def unregister(cls, session_key):
        UserSession.objects.filter(session_key=session_key).delete()
