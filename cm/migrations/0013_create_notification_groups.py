# ----------------------------------------------------------------------
# create notification groups
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def create_notification_group(self, name, emails):
        self.db.execute("INSERT INTO main_notificationgroup(name) values(%s)", [name])
        ng_id = self.db.execute("SELECT id FROM main_notificationgroup WHERE name=%s", [name])[0][0]
        for m in emails:
            u = self.db.execute("SELECT id FROM auth_user WHERE email=%s", [m])
            if u:
                user_id = u[0][0]
                self.db.execute(
                    "INSERT INTO main_notificationgroupuser(notification_group_id,time_pattern_id,user_id)"
                    "VALUES (%s,%s,%s)",
                    [ng_id, self.time_pattern_id, user_id],
                )
            else:
                self.db.execute(
                    "INSERT INTO main_notificationgroupother(notification_group_id,time_pattern_id, "
                    "notification_method,params) VALUES (%s,%s,%s,%s)",
                    [ng_id, self.time_pattern_id, "mail", m],
                )
        return ng_id

    def migrate(self):
        if (
            self.db.execute("SELECT COUNT(*) FROM main_timepattern WHERE name=%s", ["Any"])[0][0]
            == 0
        ):
            self.db.execute(
                "INSERT INTO main_timepattern(name,description) values(%s,%s)",
                ["Any", "Always match"],
            )
        self.time_pattern_id = self.db.execute(
            "SELECT id FROM main_timepattern WHERE name=%s", ["Any"]
        )[0][0]

        for on_id, on_emails in self.db.execute("SELECT id,emails FROM cm_objectnotify"):
            emails = [x.strip() for x in on_emails.split()]
            ng_id = self.create_notification_group("cm_autocreated_%d" % on_id, emails)
            self.db.execute(
                "UPDATE cm_objectnotify SET notification_group_id=%s WHERE id=%s", [ng_id, on_id]
            )
