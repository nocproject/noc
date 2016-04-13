# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserSession model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField
from mongoengine.django.sessions import MongoSession


class UserSession(Document):
    meta = {
        "collection": "noc.user_sessions",
        "allow_inheritance": False
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

    @classmethod
    def active_sessions(cls, user=None, group=None):
        """
        Calculate current active sessions for user and group
        """
        ids = []
        if user:
            ids += [user.id]
        if group:
            ids += group.user_set.values_list("id", flat=True)
        n = 0
        now = datetime.datetime.now()
        for us in UserSession.objects.filter(user_id__in=ids):
            s = MongoSession.objects.filter(session_key=us.session_key).first()
            if s:
                # Session exists
                if s.expire_date < now:
                    # Expired session
                    s.delete()
                else:
                    n += 1  # Count as active
            else:
                # Hanging session, schedule to kill
                us.delete()
        return n
