# ---------------------------------------------------------------------
# Migrate object notifications
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("cm", "0014_object_notifify_drop_emails")]

    def migrate(self):
        selectors = {}  # administrative domain id -> selector id
        for domain, group in self.db.execute(
            """
                SELECT administrative_domain_id, notification_group_id
                FROM cm_objectnotify
                WHERE type='config'
                """
        ):
            if domain is None and domain not in selectors:
                n = "~~~ALL~~~"
                self.db.execute(
                    """
                INSERT INTO sa_managedobjectselector(name)
                VALUES(%s)
                """,
                    [n],
                )
                sid = self.db.execute("SELECT id FROM sa_managedobjectselector WHERE name=%s", [n])[
                    0
                ][0]
                selectors[None] = sid
            if domain not in selectors:
                # Create selector for domain
                domain_name = self.db.execute(
                    "SELECT name FROM sa_administrativedomain WHERE id = %s", [domain]
                )[0][0]
                s_name = "~~~ON~~~ %s" % domain_name
                self.db.execute(
                    """
                INSERT INTO sa_managedobjectselector(
                    name, description,
                    is_enabled, filter_administrative_domain_id)
                VALUES(%s, %s, %s, %s)
                """,
                    [s_name, "Auto-generated selector for %s domain" % domain_name, True, domain],
                )
                selector_id = self.db.execute(
                    "SELECT id FROM sa_managedobjectselector WHERE name = %s", [s_name]
                )[0][0]
                selectors[domain] = selector_id
            selector = selectors[domain]
            # Set up notification
            self.db.execute(
                """
            INSERT INTO sa_objectnotification(selector_id, notification_group_id, config_changed, alarm_risen,
            alarm_cleared, alarm_commented, new, deleted, version_changed, interface_changed,
            script_failed, config_policy_violation)
            VALUES(%s, %s, %s, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)
            """,
                [selector, group, True],
            )
        # Remove legacy settings
        self.db.execute("DELETE FROM cm_objectnotify WHERE type='config'")
