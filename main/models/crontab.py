# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cron schedules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField
from mongoengine.errors import ValidationError
import crontab
# NOC modules
from noc.core.model.decorator import on_save, on_delete
from noc.core.handler import get_handler
from noc.core.scheduler.scheduler import Scheduler


@on_save
@on_delete
class CronTab(Document):
    meta = {
        "collections": "crontabs",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    # Handler to execute
    handler = StringField()
    # Crontab
    seconds_expr = StringField(default="0")
    minutes_expr = StringField(default="*")
    hours_expr = StringField(default="*")
    days_expr = StringField(default="*")
    months_expr = StringField(default="*")
    weekdays_expr = StringField(default="*")
    years_expr = StringField(default="*")
    # @todo: notification group
    # @todo: log settings

    SCHEDULER = "scheduler"
    JCLS = "noc.services.scheduler.jobs.cron.CronJob"

    def __unicode__(self):
        return self.name

    def clean(self):
        try:
            self.get_entry()
        except ValueError as e:
            raise ValidationError("Invalid crontab expression: %s" % e)
        if not self.get_handler():
            raise ValidationError("Invalid handler")

    @property
    def crontab_expression(self):
        """
        Returns crontab expression
        :return:
        """
        return " ".join([
            self.seconds_expr or "0",
            self.minutes_expr or "*",
            self.hours_expr or "*",
            self.days_expr or "*",
            self.months_expr or "*",
            self.weekdays_expr or "*",
            self.years_expr or "*"
        ])

    def get_entry(self):
        """
        Crontab Entry
        :return:
        """
        return crontab.CronTab(self.crontab_expression)

    def get_next(self):
        """
        Get next run
        :return: Next datetime or None
        """
        if not self.is_active:
            return None
        entry = self.get_entry()
        delta = next(entry)
        if not delta:
            return None
        return datetime.datetime.now() + datetime.timedelta(seconds=delta)

    def get_handler(self):
        """
        Get callable from handler
        :return:
        """
        return get_handler(self.handler)

    def run(self):
        """
        Called by scheduler job
        :return:
        """
        handler = self.get_handler()
        if handler:
            handler()

    @classmethod
    def get_scheduler(cls):
        return Scheduler(cls.SCHEDULER)

    def on_save(self):
        self.ensure_job()

    def on_delete(self):
        self.is_active = False
        self.ensure_job()

    def ensure_job(self):
        """
        Create or remove scheduler job
        :return:
        """
        scheduler = self.get_scheduler()
        if self.is_active:
            ts = self.get_next()
            if ts:
                scheduler.submit(
                    jcls=self.JCLS,
                    key=self.id,
                    ts=ts
                )
                return
        scheduler.remove_job(
            jcls=self.JCLS,
            key=self.id
        )
