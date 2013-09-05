# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Migrate object notifications
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    depends_on = [
        ("cm", "0014_object_notifify_drop_emails")
    ]

    def forwards(self):
        selectors = {}  # administrative domain id -> selector id
        for domain, group in db.execute("""
            SELECT administrative_domain_id, notification_group_id
            FROM cm_objectnotify
            WHERE type='config'
            """):
            if domain is None and domain not in selectors:
                n = "~~~ALL~~~"
                db.execute("""
                INSERT INTO sa_managedobjectselector(name)
                VALUES(%s)
                """, [n])
                sid = db.execute("SELECT id FROM sa_managedobjectselector WHERE name=%s", [n])[0][0]
                selectors[None] = sid
            if domain not in selectors:
                # Create selector for domain
                domain_name = db.execute(
                    "SELECT name FROM sa_administrativedomain WHERE id = %s",
                    [domain]
                )[0][0]
                s_name = "~~~ON~~~ %s" % domain_name
                db.execute("""
                INSERT INTO sa_managedobjectselector(
                    name, description,
                    is_enabled, filter_administrative_domain_id)
                VALUES(%s, %s, %s, %s)
                """, [
                    s_name,
                    "Auto-generated selector for %s domain" % domain_name,
                    True, domain
                ])
                selector_id = db.execute(
                    "SELECT id FROM sa_managedobjectselector WHERE name = %s",
                    [s_name]
                )[0][0]
                selectors[domain] = selector_id
            selector = selectors[domain]
            # Set up notification
            db.execute("""
            INSERT INTO sa_objectnotification(selector_id, notification_group_id, config_changed)
            VALUES(%s, %s, %s)
            """, [selector, group, True])
        # Remove legacy settings
        db.execute("DELETE FROM cm_objectnotify WHERE type='config'")

    def backwards(self):
        pass
