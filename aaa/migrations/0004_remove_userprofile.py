# ----------------------------------------------------------------------
# Remove UserProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.settings import LANGUAGE_CODE


class Migration(BaseMigration):
    depends_on = [("main", "0056_userprofile_heatmap")]

    def migrate(self):
        # Add fields to user
        self.db.add_column(
            "auth_user",
            "preferred_language",
            models.CharField(
                "Preferred Language", max_length=16, null=True, blank=True, default=LANGUAGE_CODE
            ),
        )
        self.db.add_column(
            "auth_user", "heatmap_lon", models.FloatField("Longitude", blank=True, null=True)
        )
        self.db.add_column(
            "auth_user", "heatmap_lat", models.FloatField("Latitude", blank=True, null=True)
        )
        self.db.add_column(
            "auth_user", "heatmap_zoom", models.IntegerField("Zoom", blank=True, null=True)
        )
        # UserContacts
        User = self.db.mock_model(model_name="User", db_table="auth_user")
        TimePattern = self.db.mock_model(model_name="TimePattern", db_table="main_timepattern")
        self.db.create_table(
            "aaa_usercontact",
            (
                ("id", models.AutoField(primary_key=True)),
                ("user", models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)),
                ("notification_method", models.CharField("Method", max_length=16)),
                ("params", models.CharField("Params", max_length=256)),
                (
                    "time_pattern",
                    models.ForeignKey(
                        TimePattern, verbose_name="Time Pattern", on_delete=models.CASCADE
                    ),
                ),
            ),
        )
        # Creating unique_together for [user_profile, time_pattern, notification_method, params] on UserProfileContact.
        self.db.create_index(
            "aaa_usercontact",
            ["user_id", "time_pattern_id", "notification_method", "params"],
            unique=True,
        )
        # Update users
        p_map = {}  # profile_id -> user_id
        data = self.db.execute(
            "SELECT id, user_id, preferred_language, heatmap_lon, heatmap_lat, heatmap_zoom "
            "FROM main_userprofile"
        )
        for p_id, user_id, preferred_language, heatmap_lon, heatmap_lat, heatmap_zoom in data:
            self.db.execute(
                "UPDATE auth_user "
                "SET preferred_language=%s, heatmap_lon=%s, heatmap_lat=%s, heatmap_zoom=%s "
                "WHERE id = %s",
                [preferred_language, heatmap_lon, heatmap_lat, heatmap_zoom, user_id],
            )
            p_map[p_id] = user_id
        # Move contacts
        data = self.db.execute(
            "SELECT user_profile_id, notification_method, params, time_pattern_id "
            "FROM main_userprofilecontact"
        )
        for p_id, notification_method, params, time_pattern_id in data:
            self.db.execute(
                "INSERT INTO aaa_usercontact(user_id, notification_method, params, time_pattern_id) "
                "VALUES(%s, %s, %s, %s)",
                [p_map[p_id], notification_method, params, time_pattern_id],
            )
        # Delete profiles and contacts
        self.db.delete_table("main_userprofilecontact")
        self.db.delete_table("main_userprofile")
