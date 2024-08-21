# ---------------------------------------------------------------------
# ./noc clean-asset
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.management.base import BaseCommand
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.object import Object


class Command(BaseCommand):
    help = "Clean asset"

    def handle(self, *args, **options):
        clean = set()
        for expr in args:
            for obj in ResourceGroup.get_objects_from_expression(expr, model_id="sa.ManagedObject"):
                if obj.id in clean:
                    continue  # Already cleaned
                self.clean_managed_object(obj)
                clean.add(obj.id)

    def clean_managed_object(self, object):
        for o in Object.objects.filter(
            data__match={"interface": "management", "attr": "managed_object", "value": object.id}
        ):
            self.clean_obj(o)

    def clean_obj(self, obj):
        print(f"Cleaning {obj.model.name} {obj.name} ({obj.id})")
        # Clean children and inner connections
        for child in obj.iter_children():
            self.clean_obj(child)
        obj.delete()


if __name__ == "__main__":
    Command().run()
