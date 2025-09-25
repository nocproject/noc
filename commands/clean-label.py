# ----------------------------------------------------------------------
# cleaning label commands
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import connection
from pymongo import UpdateMany

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.models import get_model
from noc.main.models.label import Label


models = [
    ("fm.ActiveAlarm", "labels"),
    ("fm.ArchivedAlarm", "labels"),
    ("sa.ManagedObject", "labels"),
    ("sla.SLAProbe", "labels"),
]


class Command(BaseCommand):
    help = "Cleaning label"

    def add_arguments(self, parser):
        (
            parser.add_argument(
                "label",
                help="label name",
            ),
        )

    def is_document(self, klass):
        """
        Check klass is Document instance
        :param cls:
        :return:
        """
        return isinstance(klass._meta, dict)

    def delete_label(self, model, field, label_name):
        self.print(f"began cleaning {model}...")
        model_ins = get_model(model)
        if self.is_document(model_ins):
            coll = model_ins._get_collection()
            coll.bulk_write(
                [
                    UpdateMany(
                        {field: {"$in": [label_name]}},
                        {"$pull": {field: label_name}},
                    )
                ]
            )
        else:
            label = '{"%s"}' % label_name
            sql = f"""
            UPDATE {model_ins._meta.db_table}
            SET {field}=array_remove({field}, '{label_name}')
            WHERE {field} @> '{label}'::varchar(250)[]
            """
            cursor = connection.cursor()
            cursor.execute(sql)

        self.print(f"finished {model}\n")

    def reading_models(self, label):
        for model, field in models:
            self.delete_label(model, field, label)

    def handle(self, label, *args, **options):
        connect()
        if Label.objects.filter(name=label).first():
            self.print(f"Label: {label}\n")
            self.reading_models(label)
            self.print("Done")
        else:
            self.print(f"{label} doesn't exist")


if __name__ == "__main__":
    Command().run()
