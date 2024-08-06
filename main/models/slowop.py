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
from time import sleep
from typing import Dict

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import DateTimeField, FloatField, StringField, DictField

# NOC modules
from noc.core.defer import call_later
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from bson.objectid import ObjectId

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
    STATUS_PARTIALLY = "P"
    SLOW_TIMEOUT = 5.0
    SLOW_TTL = datetime.timedelta(days=1)

    ts = DateTimeField()
    expire = DateTimeField()
    app_id = StringField()
    user = StringField()
    status = StringField(choices=[STATUS_RUNNING, STATUS_COMPLETE, STATUS_FAILED, STATUS_PARTIALLY])
    duration = FloatField()
    pickled_result = DictField()
    params = DictField()
    status_mo = DictField()
    last_update = DateTimeField(default=datetime.datetime.now)

    @classmethod
    def validate_params(cls, action, params):
        """Validate action parameters"""
        required_params = {param.name for param in action.params if getattr(param, 'is_required', False)}
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
        return True

    @classmethod
    def submit(cls, a, user=None, **kwargs):
        try:
            cls.validate_params(a, kwargs)
        except ValueError as e:
            return {"status": False, "message": "Bad request", "traceback": str(e)}

        now = datetime.datetime.now()
        ls_mo_id = kwargs['ids'].split(',')
        dc_mo_status = {mo_id: cls.STATUS_RUNNING for mo_id in ls_mo_id}
        del kwargs['ids']
        dc_arg = {"action_id": a.id, "arg": kwargs}
        so = SlowOp(
            ts=now,
            expire=now + cls.SLOW_TTL,
            status=cls.STATUS_RUNNING,
            user=user,
            params=dc_arg,
            status_mo=dc_mo_status,
        )
        so.save()
        call_later(
            "noc.main.models.slowop.call_rec_slowop", scheduler="scheduler", delay=1, so_id=so.id
        )
        return {"so_id": str(so.id)}

    @classmethod
    def list_slw(cls, request):
        """ Список задач для пользователя, набор полей описан в
            API статуса задачи

        GET /api/futures/?ls_user=all
        """
        param_p = request.GET.get('ls_user', None)
        if param_p == 'all':
            ls_slow_objs = cls.objects.all()
        else:
            ls_slow_objs = cls.objects.filter(user=request.user.username)
        try:
            ls_task = [cls.status_slw(str(slow_obj.id), request) for slow_obj in ls_slow_objs]
            return ls_task
        except Exception as e:
            dc_result = {'res': 'list_slw',
                         'user': request.user.username,
                         'ls_slow_objs': f"Error: {e}"}

        return dc_result

    @classmethod
    def get_last_update(cls):
        """ Возвращает время последнего обновления

        """
        ls_slow_objs = cls.objects.all()
        res_last_update = max([slow_obj.last_update for slow_obj in ls_slow_objs])
        return res_last_update


    @classmethod
    def statuses_slw(cls, request):
        """ Краткий список задач, используется для кнопки задач

            GET /api/futures/statuses/
        """
        timeout = 3600
        start_time = datetime.datetime.now()
        ls_slow_objs = cls.objects.all()
        ls_sm_task = []
        param_wait = request.GET.get('wait', None)

        if param_wait:
            while True:
                sleep(10)
                # Проверяем последнее обновление
                if cls.get_last_update() > start_time:
                    break
                # Проверка таймаута
                if (datetime.datetime.now() - start_time).total_seconds() > timeout:
                    return {"message": "No updates within the specified timeout."}

        for slow_obj in ls_slow_objs:
            action_id = slow_obj.get_params("action_id")
            action_obj = Action.objects.get(id=action_id)
            is_completed = False if slow_obj.status == cls.STATUS_RUNNING else True

            allowed_values = {"error", "null"}
            all_values_dc_1 = set(slow_obj.pickled_result.values())
            if all(value in allowed_values for value in all_values_dc_1):
                has_result = False
            else:
                has_result = True

            sm_task = {'label' : action_obj.description,
                     'status': slow_obj.status,
                     'is_completed': is_completed,
                     'has_result': has_result,
                     'progress': slow_obj.get_progres,
                     'last_update': slow_obj.last_update,
                     }
            ls_sm_task.append(sm_task)
        return ls_sm_task

    @classmethod
    def status_slw(cls, future_id, request):
        """ Статус задачи

        GET /api/main/<future_id>/futures/
        """
        object_id = ObjectId(future_id)
        slow_obj = SlowOp.objects.get(id=object_id)
        action_id = slow_obj.get_params("action_id")
        action_obj = Action.objects.get(id=action_id)

        is_completed = False if slow_obj.status == cls.STATUS_RUNNING else True
        allowed_values = {"error", "null"}
        all_values_dc_1 = set(slow_obj.pickled_result.values())
        if all(value in allowed_values for value in all_values_dc_1):
            has_result = False
        else:
            has_result = True

        dc_status = {
            "future_id": future_id,
            'ts': slow_obj.ts,
            'label': action_obj.description,
            'user': slow_obj.user,
            'user__label': request.user.username,
            'status': slow_obj.status,
            'is_completed': is_completed,
            'duration': int(slow_obj.duration),
            'error': slow_obj.error_description,
            'has_result': has_result
        }
        return dc_status

    def result(self):
        return json.loads(self.pickled_result)

    @property
    def get_progres(self) -> int:
        """ Возвращает кол-во незавершенных задач для объектов
        из поля status_mo документа SlowOp
        """
        total_tasks = len(self.status_mo)
        if self.status in [self.STATUS_COMPLETE, self.STATUS_FAILED, self.STATUS_PARTIALLY]:
            return 100
        elif total_tasks == 0:
            return 0
        completed_tasks = sum(1 for status in self.status_mo.values() if status == self.STATUS_COMPLETE)
        progress = (completed_tasks / total_tasks) * 100
        return int(progress)

    @property
    def error_description(self) ->str:
        """ Возвращает описание ошибки для задания в целом
        """
        errors = [mo_id for mo_id, result in self.pickled_result.items() if result == "error"]
        if errors:
            return f"The task was completed with an error for objects with id {', '.join(errors)}."
        return "No errors found."

    def get_params(self, name_prm: str) -> Dict:
        return self.params[name_prm]

    @property
    def get_status_mo(self) -> Dict:
        return self.status_mo


def call_rec_slowop(so_id):
    slow_obj = SlowOp.objects.get(id=so_id)
    action_id = slow_obj.get_params("action_id")
    action_obj = Action.objects.get(id=action_id)
    dc_arg = slow_obj.get_params("arg")
    dc_status_mo = dict()
    dc_result_mo = dict()
    start_dt = datetime.datetime.now()
    for mo_id in slow_obj.get_status_mo:
        mo_obj = ManagedObject.get_by_id(mo_id)
        try:
            # logger.info(f"Обновление статуса SlowOp: {so_id=}")
            if mo_obj and action_obj:
                # logger.info(f"Запуск выполнения задания SlowOp: {mo_id=}, {so_id=}, {dc_arg=}")
                result = action_obj.execute(mo_obj, **dc_arg)
                # logger.info(f"Результат выполнения задания: {result=}")
                pickled_result = json.dumps(result)
                # logger.info(f"Задание выполнено SlowOp: {mo_id=}, {so_id=}, {dc_arg=}, замена статуса на {SlowOp.STATUS_COMPLETE}")
                dc_status_mo[mo_id] = SlowOp.STATUS_COMPLETE
                dc_result_mo[mo_id] = pickled_result
            else:
                # logger.info(f"Задание не выполнено SlowOp {mo_id=} {so_id=}, замена статуса на {SlowOp.STATUS_FAILED}")
                dc_status_mo[mo_id] = SlowOp.STATUS_FAILED
        except Exception as e:
            # logger.error(f"Ошибка выполнения задания SlowOp: {mo_id=}, {so_id=}, {dc_arg=}. Error: {e}")
            dc_status_mo[mo_id] = SlowOp.STATUS_FAILED
            dc_result_mo[mo_id] = 'error'
        finally:
            SlowOp.objects(id=so_id).update_one(set__pickled_result=dc_result_mo,
                                                set__status_mo=dc_status_mo,
                                                set__last_update=datetime.datetime.now())

    duration = (datetime.datetime.now() - start_dt).total_seconds()
    SlowOp.objects(id=so_id).update_one(set__duration=duration)
    if SlowOp.STATUS_FAILED in dc_status_mo.values() and SlowOp.STATUS_COMPLETE in dc_status_mo.values():
        SlowOp.objects(id=so_id).update_one(set__status=SlowOp.STATUS_PARTIALLY,
                                            set__last_update=datetime.datetime.now())
    elif SlowOp.STATUS_COMPLETE in dc_status_mo.values():
        SlowOp.objects(id=so_id).update_one(set__status=SlowOp.STATUS_COMPLETE,
                                            set__last_update=datetime.datetime.now())
    else:
        SlowOp.objects(id=so_id).update_one(set__status=SlowOp.STATUS_FAILED,
                                            set__last_update=datetime.datetime.now())

