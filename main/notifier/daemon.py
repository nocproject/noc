# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-notifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from collections import defaultdict
import Queue
import threading
import datetime
import time
## Django modules
from django.db import reset_queries
from django.db.models import Q
## NOC modules
from noc.lib.daemon import Daemon
from noc.main.models import Notification
from noc.main.notifier.channels.base import notification_registry


class Notifier(Daemon):
    daemon_name = "noc-notifier"

    def __init__(self):
        self.queues = {}  # method -> Queue
        self.channels = defaultdict(list)  # method -> [Channel]
        self.active_methods = []
        self.last_flush = 0
        self.in_progress = {}  # id -> method
        self.processed_queue = Queue.Queue()
        self.queue_check_interval = 1
        super(Notifier, self).__init__()

    def close_all_channels(self):
        for m in self.channels:
            for c in self.channels[m]:
                c.shutdown()

    def report_result(self, id, status):
        self.processed_queue.put((id, status))

    def load_config(self):
        super(Notifier, self).load_config()
        self.queue_check_interval = self.config.getint(
            "notifier", "queue_check_interval")
        self.close_all_channels()
        for s in self.config.sections():
            if s in ["notifier", "main"]:
                continue
            if not self.config.getboolean(s, "enabled"):
                continue
            if s not in notification_registry:
                logging.error(
                    "Unknown notification channel '%s': skipping" % s)
                continue
            ni = self.config.getint(s, "instances")
            if ni <= 0:
                continue
            if s not in self.queues:
                qs = self.config.getint(s, "queue_size")
                logging.debug("Creating queue name=%s maxlen=%s" % (s, qs))
                self.queues[s] = Queue.Queue(maxsize=qs)
            c_class = notification_registry[s]
            for i in range(ni):
                c = c_class(self, i, self.queues[s])
                t = threading.Thread(target=c.run)
                t.daemon = True
                t.start()
        self.active_methods = list(self.queues)

    def run(self):
        logging.info("Running noc-notifier")
        busy_workers = set()
        while True:
            reset_queries()
            now = datetime.datetime.now()
            # Check which methods must be sent
            qt = (
                (Q(actual_till__isnull=True) | Q(actual_till__gt=now)) &
                (Q(next_try__isnull=True) | Q(next_try__lte=now))
            )
            pm = Notification.objects.filter(qt).filter(
                notification_method__in=self.active_methods)\
                .order_by("notification_method")\
                .distinct("notification_method").\
                values_list("notification_method", flat=True)
            if pm:
                for m in pm:
                    if m in busy_workers:
                        continue
                    for n in Notification.objects.filter(qt).filter(
                            notification_method=m).exclude(
                            id__in=list(self.in_progress)):
                        try:
                            self.queues[n.notification_method].put(
                                (n.id, n.notification_params,
                                 n.subject, n.body, n.link),
                                block=False
                            )
                            self.in_progress[n.id] = m
                            logging.info("Queuing id=%s method=%s to=%s subject=%s" % (
                                n.id, m, n.notification_params, n.subject))
                        except Queue.Full:
                            logging.info("%s worker is busy" % m)
                            busy_workers.add(m)
                            break
            else:
                # Nothing to check
                time.sleep(self.queue_check_interval)
            # Dequeue processed tasks
            t = time.time()
            dequeued_ids = []
            while True:
                try:
                    id, result = self.processed_queue.get(block=False)
                except Queue.Empty:
                    break
                if result:
                    dequeued_ids += [id]
                else:
                    # Set next try
                    nt = now + datetime.timedelta(seconds=60)
                    logging.info("Leaving %s until %s" % (id, nt))
                    Notification.objects.filter(id=id).update(
                        next_try=nt)
                if id in self.in_progress:
                    if self.in_progress[id] in busy_workers:
                        logging.debug("%s worker is ready" % self.in_progress[id])
                        busy_workers.remove(self.in_progress[id])
                    del self.in_progress[id]
            if dequeued_ids:
                for id in dequeued_ids:
                    logging.info("Dequeueing %s" % id)
                Notification.objects.filter(id__in=dequeued_ids).delete()
            # Flush queue
            if t - self.last_flush >= 60:
                Notification.objects.filter(
                    actual_till__lt=now).exclude(
                    id__in=list(self.in_progress)
                ).delete()
                self.last_flush = t
