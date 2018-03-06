# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object Config filter handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# Third-party modules
from south.db import db
from django.db import models
# Python modules
from noc.lib.nosql import get_db


class Migration(object):
    rx_fn = re.compile("^@pyrule\s*\ndef\s+([^(]+)\(", re.MULTILINE)
    rx_strip_decorator = re.compile("^@pyrule\s*", re.MULTILINE)

    def forwards(self):
        new_coll = get_db()["pyrules"]
        #  Create handler fields
        db.add_column(
            "sa_managedobject",
            "config_filter_handler",
            models.CharField(
                "Config Filter pyRule",
                max_length=256, null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobject",
            "config_diff_filter_handler",
            models.CharField(
                "Config Diff Filter Handler",
                max_length=256, null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobject",
            "config_validation_handler",
            models.CharField(
                "Config Validation Handler",
                max_length=256, null=True, blank=True
            )
        )
        # Migrate existing pyrules
        for old_field, new_field in [
            ("config_filter_rule_id", "config_filter_handler"),
            ("config_diff_filter_rule_id", "config_diff_filter_handler"),
            ("config_validation_rule_id", "config_validation_handler")
        ]:
            for row in db.execute(
                """
                SELECT DISTINCT %s
                FROM sa_managedobject
                WHERE %s IS NOT NULL
                """ % (old_field, old_field)
            ):
                pyrule_id = row[0]
                if not pyrule_id:
                    continue
                handler = self.migrate_pyrule(new_coll, pyrule_id)
                db.execute(
                    """
                    UPDATE sa_managedobject
                    SET %s = %%s
                    WHERE %s = %%s
                    """ % (new_field, old_field),
                    [handler, pyrule_id]
                )
            db.delete_column("sa_managedobject", old_field)

    def backwards(self):
        pass

    def migrate_pyrule(self, coll, pyrule_id):
        row = db.execute("SELECT text FROM main_pyrule WHERE id = %s", [pyrule_id])
        text = row[0][0]
        match = self.rx_fn.search(text)
        if not match:
            raise ValueError("Cannot migrate pyrule %d" % pyrule_id)
        new_text = self.rx_strip_decorator.sub("", text)
        fn = match.group(1)
        new_name = "config.filter%d" % pyrule_id
        handler = "noc.pyrules.%s.%s" % (new_name, fn)
        coll.insert({
            "name": new_name,
            "source": new_text
        })
        return handler
