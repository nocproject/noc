# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ReduceTask model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import marshal
import base64
import datetime
import random
import time
import types
from collections import defaultdict
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.main.models import PyRule
from managedobject import ManagedObject
from managedobjectselector import ManagedObjectSelector
from noc.sa.protocols.sae_pb2 import *
from noc.lib.fields import PickledField


class ReduceTask(models.Model):
    class Meta:
        verbose_name = _("Map/Reduce Task")
        verbose_name_plural = _("Map/Reduce Tasks")
        db_table = "sa_reducetask"
        app_label = "sa"

    start_time = models.DateTimeField(_("Start Time"))
    stop_time = models.DateTimeField(_("Stop Time"))
    script = models.TextField(_("Script"))
    script_params = PickledField(_("Params"), null=True, blank=True)

    class NotReady(Exception):
        pass

    def __unicode__(self):
        if self.id:
            return u"%d" % self.id
        else:
            return u"New: %s" % id(self)
    ##
    ##
    ##
    def save(self, **kwargs):
        if callable(self.script):
            # Make bootstrap from callable
            self.script = "import marshal,base64\n"\
            "@pyrule\n"\
            "def rule(*args,**kwargs): pass\n"\
            "rule.func_code=marshal.loads(base64.decodestring('%s'))\n" % (
                    base64.encodestring(marshal.dumps(self.script.func_code)).replace("\n", "\\n"))
        elif self.script.startswith("pyrule:"):
            # Reference to existing pyrule
            r = PyRule.objects.get(name=self.script[7:], interface="IReduceTask")
            self.script = r.text
        # Check syntax
        PyRule.compile_text(self.script)
        # Save
        super(ReduceTask, self).save(**kwargs)

    ##
    ## Check all map tasks are completed
    ##
    @property
    def complete(self):
        return self.stop_time <= datetime.datetime.now()\
            or (self.maptask_set.all().count() == self.maptask_set.filter(status__in=["C", "F"]).count())


    @classmethod
    def create_task(cls, object_selector, reduce_script, reduce_script_params,
                    map_script, map_script_params, timeout=None):
        """
        Create Map/Reduce task

        :param object_selector: One of:
                                * ManagedObjectSelector instance
                                * List of ManagedObject instances or names
                                * ManagedObject's name
        :param reduce_script: One of:
                              * Function. ReduceTask will be passed as first
                                parameter
                              * PyRule

        :param reduce_script_params: Reduce script parameters
        :type reduce_script_params: dict
        :param map_script: Script name either in form of Vendor.OS.script
                           or script
        :type map_script: str
        :param map_script_params: One of:

                                  * List of dicts or callables
                                  * Dict
        :type map_script_params: dict
        :param timeout: Task timeout, if None, timeout will be set
                        according to longest map task timeout
        :type timeout: Int or None
        :return: Task
        :rtype: ReduceTask
        """
        # Normalize map scripts to a list
        if type(map_script) in (types.ListType, types.TupleType):
            # list of map scripts
            map_script_list = map_script
            if type(map_script_params) in (types.ListType, types.TupleType):
                if len(map_script_params) != len(map_script):
                    raise Exception("Mismatched parameter list size")
                map_script_params_list = map_script_params
            else:
                # Expand to list
                map_script_params_list = [map_script_params] * len(map_script_list)
        else:
            # Single map script
            map_script_list = [map_script]
            map_script_params_list = [map_script_params]
        # Normalize a name of map scripts and join with parameters
        msp = []
        for ms, p in zip(map_script_list, map_script_params_list):
            s = ms.split(".")
            if len(s) == 3:
                ms = s[-1]
            elif len(s) != 1:
                raise Exception("Invalid map script: '%s'" % ms)
            msp += [(ms, p)]
        # Convert object_selector to a list of objects
        if type(object_selector) in (types.ListType, types.TupleType):
            objects = object_selector
        elif isinstance(object_selector, ManagedObjectSelector):
            objects = object_selector.managed_objects
        elif isinstance(object_selector, ManagedObject):
            objects = [object_selector]
        elif isinstance(object_selector, basestring):
            objects = [ManagedObject.objects.get(name=object_selector)]
        elif type(object_selector) in (int, long):
            objects = [ManagedObject.objects.get(id=object_selector)]
        else:
            objects = list(object_selector)
        # Resolve strings to managed objects, if returned by selector
        objects = [ManagedObject.objects.get(name=x)
                   if isinstance(x, basestring) else x for x in objects]
        # Auto-detect reduce task timeout, if not set
        if not timeout:
            timeout = 0
            # Split timeouts to pools
            pool_timeouts = {}  # activator_id -> [timeouts]
            pc = {}  # Pool capabilities:  activator_id -> caps
            for o in objects:
                pool = o.activator.id
                ts = pool_timeouts.get(pool, [])
                if pool not in pc:
                    pc[pool] = o.activator.capabilities
                for ms, p in msp:
                    if ms not in o.profile.scripts:
                        continue
                    s = o.profile.scripts[ms]
                    ts += [s.TIMEOUT]
                pool_timeouts[pool] = ts
            # Calculate timeouts by pools
            for pool in pool_timeouts:
                t = 0
                # Get pool capacity
                c = pc[pool]
                if c["members"] > 0:
                    # Add timeouts by generations
                    ms = c["max_scripts"]
                    ts = sorted(pool_timeouts[pool])
                    if not ts:
                        continue
                    lts = len(ts) - 1
                    i = ms - 1
                    while True:
                        i = min(i, lts)
                        t += ts[i]
                        if i >= lts:
                            break
                        i += ms
                elif pool_timeouts[pool]:
                    # Give a try when cannot detect pool capabilities
                    t = max(pool_timeouts[pool])
                timeout = max(timeout, t)
            timeout += 3  # Add guard time
        # Use dumb reduce function if reduce task is none
        if reduce_script is None:
            reduce_script = reduce_dumb
        # Create reduce task
        start_time = datetime.datetime.now()
        r_task = ReduceTask(
            start_time=start_time,
            stop_time=start_time + datetime.timedelta(seconds=timeout),
            script=reduce_script,
            script_params=reduce_script_params if reduce_script_params else {},
        )
        r_task.save()
        # Caculate number of generations
        pc = {}  # Pool capabilities: activator id -> caps
        ngs = defaultdict(int)  # pool_id -> sessions requested
        for o in objects:
            n = len(msp)
            a_id = o.activator.id
            if a_id not in pc:
                pc[a_id] = o.activator.capabilities
            ngs[a_id] += n
        for p in ngs:
            ms = pc[p]["max_scripts"]
            if ms:
                ngs[p] = round(ngs[p] / ms + 0.5)
            else:
                ngs[p] = 0
        # Run map task for each object
        for o in objects:
            ng = ngs[o.activator.id]
            no_sessions = not ng and o.profile_name != "NOC.SAE"
            for ms, p in msp:
                # Set status to "F" if script not found
                if no_sessions or ms not in o.profile.scripts:
                    status = "F"
                else:
                    status = "W"
                # Build full map script name
                msn = "%s.%s" % (o.profile_name, ms)
                # Expand parameter, if callable
                if callable(p):
                    p = p(o)
                # Redistribute tasks
                if ng <= 1:
                    delay = 0
                else:
                    delay = random.randint(0, min(ng * 3, timeout / 2))
                #
                m = MapTask(
                    task=r_task,
                    managed_object=o,
                    map_script=msn,
                    script_params=p,
                    next_try=start_time + datetime.timedelta(seconds=delay),
                    status=status
                )
                if status == "F":
                    if no_sessions:
                        m.script_result = dict(code=ERR_ACTIVATOR_NOT_AVAILABLE,
                                               text="Activator pool is down")
                    else:
                        m.script_result = dict(code=ERR_INVALID_SCRIPT,
                                               text="Invalid script %s" % msn)
                m.save()
        return r_task

    ##
    ## Perform reduce script and execute result
    ##
    def reduce(self):
        return PyRule.compile_text(self.script)(self, **self.script_params)

    ##
    ## Get task result
    ##
    def get_result(self, block=True):
        while True:
            if self.complete:
                result = self.reduce()
                self.delete()
                return result
            else:
                if block:
                    time.sleep(3)
                else:
                    raise ReduceTask.NotReady

    @classmethod
    def wait_for_tasks(cls, tasks):
        """
        Wait until all task complete
        """
        while tasks:
            time.sleep(1)
            rest = []
            for t in tasks:
                if t.complete:
                    t.reduce()  # delete task and trigger reduce task
                    t.delete()
                else:
                    rest += [t]
                tasks = rest

    @classmethod
    def wait_any(cls, tasks):
        """
        Wait for any task to complete
        """
        while tasks:
            time.sleep(1)
            for t in tasks:
                if t.complete:
                    t.reduce()
                    t.delete()
                    return


def reduce_object_script(task):
    mt = task.maptask_set.all()[0]
    if mt.status == "C":
        return mt.script_result
    else:
        return None

def reduce_dumb(task):
    pass

## Avoid circular references
from maptask import MapTask