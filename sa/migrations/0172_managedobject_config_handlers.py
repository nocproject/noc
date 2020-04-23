# ----------------------------------------------------------------------
# Managed Object Config filter handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    rx_fn = re.compile(r"^@pyrule\s*\ndef\s+([^(]+)\(", re.MULTILINE)
    rx_strip_decorator = re.compile(r"^@pyrule\s*", re.MULTILINE)

    def migrate(self):
        new_coll = self.mongo_db["pyrules"]
        #  Create handler fields
        self.db.add_column(
            "sa_managedobject",
            "config_filter_handler",
            models.CharField("Config Filter pyRule", max_length=256, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "config_diff_filter_handler",
            models.CharField("Config Diff Filter Handler", max_length=256, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "config_validation_handler",
            models.CharField("Config Validation Handler", max_length=256, null=True, blank=True),
        )
        # Migrate existing pyrules
        for old_field, new_field in [
            ("config_filter_rule_id", "config_filter_handler"),
            ("config_diff_filter_rule_id", "config_diff_filter_handler"),
            ("config_validation_rule_id", "config_validation_handler"),
        ]:
            for row in self.db.execute(
                """
                    SELECT DISTINCT %s
                    FROM sa_managedobject WHERE %s IS NOT NULL"""
                % (old_field, old_field)
            ):
                pyrule_id = row[0]
                if not pyrule_id:
                    continue
                handler = self.migrate_pyrule(new_coll, pyrule_id)
                self.db.execute(
                    """
                    UPDATE sa_managedobject
                    SET %s = %%s
                    WHERE %s = %%s
                    """
                    % (new_field, old_field),
                    [handler, pyrule_id],
                )
            self.db.delete_column("sa_managedobject", old_field)
