# Python modules
import argparse
from typing import List, Dict

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.pm.models.metrictype import MetricType
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interfaceprofile import InterfaceProfile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("metrics", nargs=argparse.REMAINDER, help="Crashinfo UUIDs")

    def handle(self, *args, **options):
        if not options.get("metrics"):
            self.die("No requested metrics")
        connect()
        iface_metrics, object_metrics = [], []
        for m in options["metrics"]:
            mt = MetricType.get_by_name(m)
            if not mt:
                self.print(f"Unknown metric name '{m}'. Skipping")
                continue
            if mt.scope.name == "Interface":
                iface_metrics.append(mt)
                continue
            object_metrics.append(mt)
        if object_metrics:
            self.print("Checking Object Metric")
            self.check_object_metrics(object_metrics)
        if iface_metrics:
            self.print("Checking Interface Metric")
            self.check_interface_metrics(iface_metrics)

    def check_object_metrics(self, metrics: List[MetricType]):
        mt_check: Dict[str, MetricType] = {str(mt.id): mt for mt in metrics}
        for mop in ManagedObjectProfile.objects.filter(
            enable_periodic_discovery_metrics=True, enable_periodic_discovery=True
        ):
            checks = set(mt_check)
            for mc in mop.metrics:
                if mc["metric_type"] in checks:
                    checks.remove(mc["metric_type"])
            if checks:
                self.print(
                    f"[{mop.name}] Not configured metrics: ",
                    ",".join(mt_check[c].name for c in checks),
                )

    def check_interface_metrics(self, metrics: List[MetricType]):
        for ip in InterfaceProfile.objects.filter(metrics__exists=True):
            checks = set(metrics)
            for mc in ip.metrics:
                if mc.metric_type in checks:
                    checks.remove(mc.metric_type)
            if checks:
                self.print(
                    f"[{ip.name}] Not configured metrics: ", ",".join(c.name for c in checks)
                )


if __name__ == "__main__":
    Command().run()
