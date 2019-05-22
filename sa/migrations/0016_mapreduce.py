# ----------------------------------------------------------------------
# map reduce
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import PickledField


class Migration(BaseMigration):
    def migrate(self):
        # Model 'ReduceTask'
        self.db.create_table(
            'sa_reducetask', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('start_time', models.DateTimeField("Start Time")), ('stop_time', models.DateTimeField("Stop Time")),
                ('reduce_script', models.CharField("Script", max_length=256)),
                ('script_params', PickledField("Params", null=True, blank=True))
            )
        )

        # Mock Models
        ReduceTask = self.db.mock_model(
            model_name='ReduceTask',
            db_table='sa_reducetask',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        ManagedObject = self.db.mock_model(
            model_name='ManagedObject',
            db_table='sa_managedobject',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Model 'MapTask'
        self.db.create_table(
            'sa_maptask', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('task', models.ForeignKey(ReduceTask, verbose_name="Task")),
                ('managed_object', models.ForeignKey(ManagedObject, verbose_name="Managed Object")),
                ('map_script', models.CharField("Script", max_length=256)),
                ('script_params', PickledField("Params", null=True, blank=True)),
                ('next_try', models.DateTimeField("Next Try")),
                ('retries_left', models.IntegerField("Retries Left", default=1)), (
                    'status',
                    models.CharField(
                        "Status",
                        max_length=1,
                        choices=[("W", "Wait"), ("R", "Running"), ("C", "Complete"), ("F", "Failed")],
                        default="W"
                    )
                ), ('script_result', PickledField("Result", null=True, blank=True))
            )
        )
