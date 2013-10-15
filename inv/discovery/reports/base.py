## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base report class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.main.models import (ResourceState, SystemTemplate,
                             SystemNotification)


class Report(object):
    """
    Report usage pattern:
    1. Create report in job's handler
    2. Submit data to report
    3. Call .send()
    """
    system_notification = None

    def __init__(self, job, enabled=True, to_save=False):
        self.job = job
        self.object = job.object
        self.enabled = enabled
        self.to_save = to_save
        self.set_object_context()

    def die(self, msg):
        self.job.scheduler.daemon.die(msg)

    def info(self, msg):
        self.job.info(msg)

    def error(self, msg):
        self.job.error(msg)

    def update_if_changed(self, obj, values):
        """
        Update fields if changed.
        :param obj: Document instance
        :type obj: Document
        :param values: New values
        :type values: dict
        :returns: List of changed (key, value)
        :rtype: list
        """
        changes = []
        for k, v in values.items():
            vv = getattr(obj, k)
            if v != vv:
                if type(v) != int or not hasattr(vv, "id") or v != vv.id:
                    setattr(obj, k, v)
                    changes += [(k, v)]
        if changes:
            obj.save()
        return changes

    def log_changes(self, msg, changes):
        """
        Log changes
        :param msg: Message
        :type msg: str
        """
        if changes:
            self.info("%s: %s" % (
                msg, ", ".join("%s = %s" % (k, v) for k, v in changes)))

    def get_state_map(self, s):
        """
        Process from state -> to state; ....; from state -> to state syntax
        and return a map of {state: state}
        :param s:
        :return:
        """
        def get_state(name):
            try:
                return ResourceState.objects.get(name=name)
            except ResourceState.DoesNotExist:
                self.die("Unknown resource state: '%s'" % name)

        m = {}
        for x in s.split(";"):
            x = x.strip()
            if not x:
                continue
            if "->" not in x:
                self.die("Invalid state map expression: '%s'" % x)
            f, t = [get_state(y.strip()) for y in x.split("->")]
            m[f.id] = t
        return m

    def set_object_context(self):
        """
        Generate object part of context for get_fqdn
        """
        name = self.object.name
        if "." in name:
            host, domain = name.split(".", 1)
        else:
            host = name
            domain = None
        self.context = {
            "object": self.object,
            "name": name,
            "host": host,
            "domain": domain
        }

    def send(self):
        pass

    def send_system_notification(self, subject, body):
        SystemNotification.notify(
            self.system_notification, subject=subject, body=body)

    def notify(self, template_name, context):
        """
        Render template and send notifications
        :param template_name:
        :param context:
        :return:
        """
        tpl = SystemTemplate.objects.get(
            name=template_name).template
        subject = tpl.render_subject(**context)
        body = tpl.render_body(**context)
        self.send_system_notification(subject, body)
