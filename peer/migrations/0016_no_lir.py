# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):
        Maintainer = db.mock_model(model_name='Maintainer', db_table='peer_maintainer',
                                   db_tablespace='', pk_field_name='id',
                                   pk_field_type=models.AutoField)

        rir_id = db.execute("SELECT id FROM peer_rir LIMIT 1")[0][0]
        lir_to_rir = {}
        for lir_id, name in db.execute("SELECT id,name FROM peer_lir"):
            db.execute(
                "INSERT INTO peer_maintainer(maintainer,description,auth,rir_id) VALUES(%s,%s,%s,%s)",
                [name, name, 'NOAUTH', rir_id])
            lir_to_rir[lir_id] = \
                db.execute("SELECT id FROM peer_maintainer WHERE maintainer=%s", [name])[0][0]
        db.add_column("peer_as", "maintainer",
                      models.ForeignKey(Maintainer, verbose_name="Maintainer", null=True,
                                        blank=True))
        for as_id, lir_id in db.execute("SELECT id,lir_id FROM peer_as"):
            db.execute("UPDATE peer_as SET maintainer_id=%s WHERE id=%s",
                       [lir_to_rir[lir_id], as_id])
        db.execute("ALTER TABLE peer_as ALTER maintainer_id SET NOT NULL")
        db.delete_column("peer_as", "lir_id")
        db.delete_table("peer_lir")

    def backwards(self):
        pass
