# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Slow operations registry
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
import threading
import datetime
import logging
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, StringField, UUIDField
## NOC modules
from noc.lib.threadpool import Pool
from noc.lib.debug import error_report

logger = logging.getLogger(__name__)


class SlowOp(Document):
    meta = {
        "collection": "noc.slowops",
        "indexes": [
            {
                "fields": ["expire"],
                "expireAfterSeconds": 0
            }
        ]
    }

    ts = DateTimeField()
    expire = DateTimeField()
    app = StringField()
    user = StringField()
    op = UUIDField(binary=False)
    # Op status: Running/Success/Failed
    status = StringField(choices=["R", "S", "F"])
    # Complete reason
    reason = StringField()

    _pool = Pool(name="slowops", metrics_prefix="noc.slowops.pool", min_spare=1, max_spare=5)
    SLOW_TIMEOUT = 5.0
    SLOW_TTL = datetime.timedelta(days=1)

    def __unicode__(self):
        return self.op

    @classmethod
    def submit(cls, f, app=None, user=None):
        """
        Submit slow operation. Returns None when operation completed,
        or op UUID otherwise
        """
        now = datetime.datetime.now()
        done_event = threading.Event()
        slow_event = threading.Event(())
        op = str(uuid.uuid4())
        cls._pool.run(op, cls._runner, args=(f, done_event, slow_event, op))
        s = done_event.wait(cls.SLOW_TIMEOUT)
        if s:
            return None  # Event set, operation complete
        # Event not set, slow operation continues
        logger.debug("Slow operation registered")
        slow_event.set()
        SlowOp(
            ts=now,
            expire=now + cls.SLOW_TTL,
            app=app,
            user=user,
            op=op,
            status="R"
        ).save()
        return op

    @classmethod
    def _runner(cls, f, done_event, slow_event, op):
        status = "S"
        reason = "OK"
        try:
            f()
        except Exception, why:
            error_report()
            status = "F"
            reason = str(why)
        # Signal the operation is complete
        done_event.set()
        # Update status for slow events
        if slow_event.is_set:
            SlowOp._get_collection().find_and_modify({
                "op": op
            }, {
                "$set": {
                    "status": status,
                    "reason": reason
                }
            })


class LongOperation(object):
    def __init__(self, f):
        self.f = f
        self.complete = False
        self.status = False
        self.result = None

    @classmethod
    def get(self, uuid):
        pass

    def __call__(self, *args, **kwargs):
        pass