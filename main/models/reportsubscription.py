# ---------------------------------------------------------------------
# ReportSubscription model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import time
import datetime
import os

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, DateTimeField

# NOC modules
from noc.aaa.models.user import User
from noc.main.models.notificationgroup import NotificationGroup
from noc.core.mongo.fields import ForeignKeyField
from noc.services.web.base.site import site
from noc.core.debug import error_report
from noc.core.model.decorator import on_save, on_delete
from noc.core.scheduler.job import Job

logger = logging.getLogger(__name__)


@on_save
@on_delete
class ReportSubscription(Document):
    meta = {"collection": "noc.reportsubscriptions", "strict": False, "auto_create_index": False}

    # File name without extension
    file_name = StringField(unique=True)
    # Subscription is active
    is_active = BooleanField(default=True)
    # email subject
    subject = StringField()
    # Run report as user
    run_as = ForeignKeyField(User)
    # Send result to notification group
    # If empty, only file will be written
    notification_group: "NotificationGroup" = ForeignKeyField(NotificationGroup)
    # Predefined report id
    # <app id>:<variant>
    report = StringField()
    #
    last_status = BooleanField(default=False)
    last_run = DateTimeField()

    PREFIX = "var/reports"
    JCLS = "noc.main.models.reportsubscription.ReportJob"

    class RequestStub(object):
        def __init__(self, user):
            self.user = user

    @classmethod
    def send_reports(cls):
        """
        Calculate and send all reports for today
        :return:
        """
        subscriptions = list(ReportSubscription.objects.filter(is_active=True))
        for s in subscriptions:
            if s.can_run():
                try:
                    path = s.build_report()
                except Exception:
                    path = None
                    error_report()
                s.update_status(bool(path))
                if path and s.notification_group:
                    s.send_report(path)

    def update_status(self, status):
        self._get_collection().update_one(
            {"_id": self.id}, {"$set": {"last_status": status, "last_run": datetime.datetime.now()}}
        )

    def can_run(self):
        """
        Check report must be built today
        :return:
        """
        return True

    def build_report(self):
        """
        Generate report
        :return:
        """
        t0 = time.time()
        logger.info("[%s] Building report", self.file_name)
        app_id, variant = self.report.split(":")
        if app_id not in site.apps:
            logger.error("[%s] Invalid application %s. Skipping", self.file_name, app_id)
            return None
        # Check file can be written
        today = datetime.date.today()
        dirname = os.path.join(
            self.PREFIX, "%04d" % today.year, "%02d" % today.month, "%02d" % today.day
        )
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError as e:
                logger.error("[%s] Failed to create directory %s: %s", self.file_name, dirname, e)
                return None
        path = os.path.join(dirname, self.file_name)
        #
        app = site.apps[app_id]
        args = app.get_predefined_args(variant)
        request = self.RequestStub(user=self.run_as)
        report = app.get_data(request, **args)
        data = report.to_csv()
        logger.info("[%s] Writing file %s", self.file_name, path)
        with open(path, "w") as f:
            f.write(data)
        dt = time.time() - t0
        logger.info("[%s] Done in %.2fs (%d bytes)", self.file_name, dt, len(data))
        return path

    def send_report(self, path):
        addresses = [r.contact for r in self.notification_group.members if r.method == "mail"]
        with open(path) as f:
            data = f.read()
        for a in addresses:
            logger.info("[%s] Sending to %s", self.file_name, a)
            nf = NotificationGroup()
            nf.send_notification(
                "mail",
                a,
                self.subject,
                "",
                attachments=[{"filename": self.file_name, "data": data}],
            )

    def on_save(self):
        if self.has_subscriptions():
            self.submit_job()
        else:
            self.remove_job()

    def on_delete(self):
        if not self.has_subscriptions():
            self.remove_job()

    @classmethod
    def has_subscriptions(cls):
        return ReportSubscription.objects.filter(is_active=True).count() > 0

    def submit_job(self):
        logger.info("Submitting job")
        Job.submit("scheduler", self.JCLS)

    def remove_job(self):
        logger.info("Removing job")
        Job.remove("scheduler", self.JCLS)


class ReportJob(Job):
    name = "daily"
    HOUR = 1  # @todo: Configurable

    def handler(self, **kwargs):
        site.autodiscover()
        ReportSubscription.send_reports()

    def dereference(self):
        return True

    def schedule_next(self, status):
        ts = datetime.date.today() + datetime.timedelta(days=1)
        ts = datetime.datetime.combine(ts, datetime.time(hour=self.HOUR))
        self.scheduler.set_next_run(
            self.attrs[self.ATTR_ID], status=status, ts=ts, duration=self.duration
        )
