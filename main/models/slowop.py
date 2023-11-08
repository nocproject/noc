# ---------------------------------------------------------------------
# Slow operations registry
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
import json
from typing import Dict

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, FloatField, StringField, DictField

# NOC modules
from noc.core.defer import call_later

logger = logging.getLogger(__name__)


class SlowOp(Document):
    meta = {
        "collection": "noc.slowops",
        "strict": False,
        "auto_create_index": False,
        "indexes": [{"fields": ["expire"], "expireAfterSeconds": 0}],
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
    status = StringField(choices=[STATUS_RUNNING, STATUS_COMPLETE, STATUS_FAILED])
    duration = FloatField()
    pickled_result = StringField()
    params = DictField()

    @classmethod
    def submit(cls, o, a, user=None, **kwargs):
        now = datetime.datetime.now()
        dc_arg = {"mo_id": o.id, "act_id": a.id, "arg": kwargs}
        so = SlowOp(
            ts=now, expire=now + cls.SLOW_TTL, status=cls.STATUS_RUNNING, user=user, params=dc_arg
        )
        so.save()
        call_later(
            "noc.main.models.slowop.call_rec_slowop", scheduler="scheduler", delay=1, so_id=so.id
        )
        return {"so_id": str(so.id)}

    def is_ready(self):
        return self.status in (self.STATUS_COMPLETE, self.STATUS_FAILED)

    def result(self):
        return json.loads(self.pickled_result)

    def get_params(self, name_prm: str) -> Dict:
        return self.params[name_prm]


def call_rec_slowop(so_id):
    from noc.sa.models.action import Action
    from noc.sa.models.managedobject import ManagedObject

    slow_obj = SlowOp.objects.get(id=so_id)
    om_obj = ManagedObject.get_by_id(slow_obj.get_params("mo_id"))
    act_obj = Action.objects.get(id=slow_obj.get_params("act_id"))
    try:
        result = act_obj.execute(om_obj, **slow_obj.get_params("arg"))
    except Exception as e:
        SlowOp.objects(id=so_id).update_one(set__status=SlowOp.STATUS_FAILED)
        logger.info(f"Error call_rec_slowop(): %s" % e)
    else:
        pickled_result = json.dumps(result)
        SlowOp.objects(id=so_id).update_one(
            set__pickled_result=pickled_result, set__status=SlowOp.STATUS_COMPLETE
        )
