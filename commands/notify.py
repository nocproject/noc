# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Notification utility
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.core.management.base import BaseCommand
from noc.main.models.template import Template
from noc.main.models.notificationgroup import NotificationGroup


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry Run (Do not send message)"
        )
        parser.add_argument(
            "--notification-group",
            action="append",
            dest="notification_group",
            help="Notification group name",
            required=True
        )
        parser.add_argument(
            "--template",
            action="store",
            dest="template",
            help="Template name"
        )
        parser.add_argument(
            "--subject",
            action="store",
            dest="subject",
            help="Message subject"
        )
        parser.add_argument(
            "--body",
            action="store",
            dest="body",
            help="Message body"
        )
        parser.add_argument(
            "--body-file",
            action="store",
            dest="body_file",
            help="Message body file"
        )
        parser.add_argument(
            "--var",
            action="append",
            dest="var",
            help="Template variable in key=value form"
        )

    def handle(self, notification_group=None, template=None, subject=None,
               body=None, body_file=None, var=None,
               debug=False, dry_run=False,
               *args, **kwargs):
        groups = []
        for ng in notification_group:
            g = NotificationGroup.get_by_name(ng)
            if not g:
                self.die("Invalid notification group '%s'" % ng)
            groups += [g]
        if subject and (body or body_file):
            # Get message from command line
            if body_file:
                with open(body_file) as f:
                    body = f.read()
        elif template:
            # Get message from template
            t = Template.get_by_name(template)
            if not t:
                self.die("Invalid template name '%s'" % template)
            # Convert variables
            var = var or []
            ctx = {}
            for x in var:
                if "=" not in x:
                    continue
                k, v = x.split("=", 1)
                ctx[k.strip()] = v.strip()
            subject = t.render_subject(**ctx)
            body = t.render_body(**ctx)
        else:
            self.die("Either '--template' or '--subject' + '--body' parameters must be set")
        if not subject:
            self.die("Subject is empty")
        if not body:
            self.die("Body is empty")
        if self.is_debug:
            self.print("Subject: %s" % subject)
            self.print("---[Body]---------")
            self.print(body)
            self.print("---[End]----------")
        for g in groups:
            if self.is_debug:
                self.print("Sending message to group: %s" % g.name)
            if not dry_run:
                g.notify(
                    subject=subject,
                    body=body
                )


if __name__ == "__main__":
    Command().run()
