# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Slow operations registry
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
import concurrent.futures
import cPickle
import time
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, FloatField, StringField
## NOC modules
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
    STATUS_RUNNING = "R"
    STATUS_COMPLETE = "C"
    STATUS_FAILED = "F"
    SLOW_TIMEOUT = 5.0
    SLOW_TTL = datetime.timedelta(days=1)

    ts = DateTimeField()
    expire = DateTimeField()
    app_id = StringField()
    user = StringField()
    status = StringField(choices=[STATUS_RUNNING, STATUS_COMPLETE,
                                  STATUS_FAILED])
    duration = FloatField()
    pickled_result = StringField()
    pool = concurrent.futures.ThreadPoolExecutor(100)

    TimeoutError = concurrent.futures.TimeoutError

    @classmethod
    def submit(cls, fn, app_id=None, user=None, *args, **kwargs):
        def on_complete(f):
            logger.debug("Completion slow operation %s", so.id)
            if f.exception():
                so.status = cls.STATUS_FAILED
                try:
                    f.result()
                except Exception:
                    error_report()
                so.pickled_result = cPickle.dumps(f.exception())
            else:
                so.status = cls.STATUS_COMPLETE
                so.pickled_result = cPickle.dumps(f.result())
            so.duration = time.time() - t0
            so.save()

        so = None
        t0 = time.time()
        future = cls.pool.submit(fn, *args, **kwargs)
        try:
            future.result(cls.SLOW_TIMEOUT)
        except concurrent.futures.TimeoutError:
            logger.debug("Continuing slow operation %s (app=%s, user=%s)",
                         fn, app_id, user)
            # Save slow op
            now = datetime.datetime.now()
            so = SlowOp(
                ts=now,
                expire=now + cls.SLOW_TTL,
                status=cls.STATUS_RUNNING,
                app_id=app_id,
                user=user
            )
            so.save()
            future.add_done_callback(on_complete)
        future.slow_op = so
        return future

    def is_ready(self):
        return self.status in (self.STATUS_COMPLETE, self.STATUS_FAILED)

    def result(self):
        return cPickle.loads(str(self.pickled_result))
