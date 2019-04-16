# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszonerecord set type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        db.execute(
            """
        UPDATE dns_dnszonerecord r
        SET
            type = (
                SELECT type
                FROM dns_dnszonerecordtype
                WHERE
                    id = r.type_id
            )
        """
        )

    def backwards(self):
        pass
