# ----------------------------------------------------------------------
# ./noc apply-nri-links
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.extnrilink import ExtNRILink
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.core.etl.portmapper.loader import loader


class Command(BaseCommand):
    BATCH_SIZE = 100

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # view command
        subparsers.add_parser("apply")
        # list command
        subparsers.add_parser("status")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_apply(self, *args, **options):
        connect()
        self.mo_cache = {}
        self.mc_cache = {}
        self.bulk = []
        self.collection = ExtNRILink._get_collection()
        self.stdout.write("Apply NRI links from %s\n" % ExtNRILink._meta["collection"])
        for ll in ExtNRILink.objects.filter(link__exists=False):
            # Get objects
            src_mo = ManagedObject.get_by_id(ll.src_mo)
            if not src_mo or src_mo.profile.is_generic:
                continue
            dst_mo = ManagedObject.get_by_id(ll.dst_mo)
            if not dst_mo or dst_mo.profile.is_generic:
                continue
            if src_mo.id == dst_mo.id:
                self.update_warn(ll.id, "Loop link")
                continue
            # Get port mappers
            src_pm = self.get_port_mapper(src_mo)
            if not src_pm:
                self.update_warn(
                    ll.id,
                    "No port mapper for %s (%s)"
                    % (src_mo.name, src_mo.platform or src_mo.profile.name),
                )
                continue
            dst_pm = self.get_port_mapper(dst_mo)
            if not dst_pm:
                self.update_warn(
                    ll.id,
                    "No port mapper for %s (%s)"
                    % (dst_mo.name, dst_mo.platform or dst_mo.profile.name),
                )
                continue
            # Map interfaces
            src_ifname = src_pm(src_mo).to_local(ll.src_interface)
            if not src_ifname:
                self.update_warn(
                    ll.id,
                    "Cannot map interface %s for %s (%s)"
                    % (ll.src_interface, src_mo.name, src_mo.platform or src_mo.profile.name),
                )
                continue
            dst_ifname = dst_pm(dst_mo).to_local(ll.dst_interface)
            if not dst_ifname:
                self.update_warn(
                    ll.id,
                    "Cannot map interface %s for %s (%s)"
                    % (ll.dst_interface, dst_mo.name, dst_mo.platform or dst_mo.profile.name),
                )
                continue
            # Find interfaces in NOC's inventory
            src_iface = self.get_interface(src_mo, src_ifname)
            if not src_iface:
                self.update_warn(ll.id, "Interface not found %s@%s\n" % (src_mo.name, src_ifname))
                continue
            dst_iface = self.get_interface(dst_mo, dst_ifname)
            if not dst_iface:
                self.update_warn(ll.id, "Interface not found %s@%s\n" % (dst_mo.name, dst_ifname))
                continue
            src_link = src_iface.link
            dst_link = dst_iface.link
            if not src_link and not dst_link:
                self.stdout.write(
                    "%s: %s -- %s: %s: Linking\n"
                    % (src_mo.name, src_ifname, dst_mo.name, dst_ifname)
                )
                src_link = src_iface.link_ptp(dst_iface, method="nri")
                self.update_nri(ll.id, link=src_link.id)
            elif src_link and dst_link and src_link.id == dst_link.id:
                self.stdout.write(
                    "%s: %s -- %s: %s: Already linked\n"
                    % (src_mo.name, src_ifname, dst_mo.name, dst_ifname)
                )
                self.update_nri(ll.id, link=src_link.id)
            elif src_link and not dst_link:
                self.update_error(ll.id, "Linked to: %s" % src_link)
            elif src_link is None and dst_link:
                self.update_error(ll.id, "Linked to: %s" % dst_link)
        if self.bulk:
            self.stdout.write("Commiting changes to database\n")
            try:
                self.collection.bulk_write(self.bulk)
                self.stdout.write("Database has been synced\n")
            except BulkWriteError as e:
                self.stdout.write("Bulk write error: '%s'\n", e.details)
        else:
            self.stdout.write("Nothing changed\n")

    @staticmethod
    def get_port_mapper(mo):
        if mo.remote_system:
            return loader.get_loader(mo.remote_system.name)
        return None

    @staticmethod
    def get_interface(managed_object, name):
        return Interface.objects.filter(managed_object=managed_object.id, name=name).first()

    def bulk_op(self, id, **kwargs):
        op_set = {}
        op_unset = {}
        for k in kwargs:
            if kwargs[k] is None:
                op_unset[k] = ""
            else:
                op_set[k] = kwargs[k]
        op = {}
        if op_set:
            op["$set"] = op_set
        if op_unset:
            op["$unset"] = op_unset
        self.bulk += [UpdateOne({"_id": id}, op)]
        if len(self.bulk) % self.BATCH_SIZE == 0:
            self.stdout.write("Commiting changes to database\n")
            try:
                self.collection.bulk_write(self.bulk)
                self.bulk = []
                self.stdout.write("Database has been synced\n")
            except BulkWriteError as e:
                self.stdout.write("Bulk write error: '%s'\n", e.details)

    def update_nri(self, id, **kwargs):
        self.bulk_op(id, error=None, warn=None, **kwargs)

    def update_warn(self, id, msg):
        self.stderr.write("%% %s\n" % msg)
        self.bulk_op(id, warn=msg)

    def update_error(self, id, msg):
        self.stderr.write("%% %s\n" % msg)
        self.bulk_op(id, warn=None, error=msg)

    def handle_status(self):
        n_total = ExtNRILink.objects.count()
        if not n_total:
            self.stdout.write("No NRI links\n")
            return
        n_correct = ExtNRILink.objects.filter(link__exists=True).count()
        n_warn = ExtNRILink.objects.filter(warn__exists=True).count()
        n_error = ExtNRILink.objects.filter(error__exists=True).count()
        n_ignored = n_total - n_correct - n_warn - n_error
        self.stdout.write(
            "\n".join(
                [
                    "NRI Links:Correct  : %d (%.2f%%)" % (n_correct, n_correct * 100.0 / n_total),
                    "Warnings : %d (%.2f%%)" % (n_warn, n_warn * 100.0 / n_total),
                    "Errors   : %d (%.2f%%)" % (n_error, n_error * 100.0 / n_total),
                    "Ignored  : %d (%.2f%%)" % (n_ignored, n_ignored * 100.0 / n_total),
                    "Total    : %d" % n_total,
                ]
            )
        )
        self.stdout.write("\n")


if __name__ == "__main__":
    Command().run()
