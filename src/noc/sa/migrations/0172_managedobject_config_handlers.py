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

    def migrate(self) -> None:
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
        pmap = {}  # Check use one pyrule on some function
        # Migrate existing pyrules
        for old_field, new_field in [
            ("config_filter_rule_id", "config_filter_handler"),
            ("config_diff_filter_rule_id", "config_diff_filter_handler"),
            ("config_validation_rule_id", "config_validation_handler"),
        ]:
            for row in self.db.execute(
                f"""
                    SELECT DISTINCT {old_field}
                    FROM sa_managedobject WHERE {old_field} IS NOT NULL"""
            ):
                pyrule_id = row[0]
                if not pyrule_id:
                    continue
                if pyrule_id in pmap:
                    handler = pmap[pyrule_id]
                else:
                    handler = self.migrate_pyrule(new_coll, pyrule_id)
                    pmap[pyrule_id] = handler
                self.db.execute(
                    f"""
                    UPDATE sa_managedobject
                    SET {new_field} = %s
                    WHERE {old_field} = %s
                    """,
                    [handler, pyrule_id],
                )
            self.db.delete_column("sa_managedobject", old_field)

    def migrate_pyrule(self, coll, pyrule_id):
        row = self.db.execute("SELECT text, handler FROM main_pyrule WHERE id = %s", [pyrule_id])
        text, handler = row[0][0], row[0][1]
        if handler and handler.startswith("noc.solutions"):
            # Skip solutions
            return None
        if handler and not text:
            return handler
        match = self.rx_fn.search(text)
        if not match:
            raise ValueError(f"Cannot migrate pyrule {int(pyrule_id)}")
        new_text = self.rx_strip_decorator.sub("", text)
        fn = match.group(1)
        new_name = f"config.filter{int(pyrule_id)}"
        handler = f"noc.pyrules.{new_name}.{fn}"
        coll.insert_one({"name": new_name, "source": new_text})
        return handler
