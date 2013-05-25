# encoding: utf-8
from south.db import db
from django.db import models
from noc.lib.ip import IPv4

class Migration:
    depends_on = [
        ("main", "0035_prefix_table")
    ]

    def forwards(self):
        PrefixTable = db.mock_model(model_name="PrefixTable",
            db_table="main_prefixtable", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        db.add_column(
            "sa_activator", "prefix_table",
            models.ForeignKey(
                PrefixTable,
                verbose_name=_("Prefix Table"), null=True, blank=True)
        )
        # Migrate data
        for id, name, ip, to_ip in db.execute(
                "SELECT id, name, ip, to_ip FROM sa_activator"):
            pt_name = "Activator::%s" % name
            db.execute(
                """
                INSERT INTO main_prefixtable(name)
                VALUES(%s)
                """, [pt_name])
            pt_id, = db.execute("SELECT id FROM main_prefixtable WHERE name = %s", [pt_name])[0]
            for p in IPv4.range_to_prefixes(ip, to_ip):
                db.execute("""
                    INSERT INTO main_prefixtableprefix(table_id, afi, prefix)
                    VALUES(%s, '4', %s)
                    """, [pt_id, p.prefix])
            db.execute("UPDATE sa_activator SET prefix_table_id=%s WHERE id=%s", [pt_id, id])

    def backwards(self):
        pass
