# ---------------------------------------------------------------------
# Reclassify events
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import datetime
import hashlib
import argparse
from html.entities import name2codepoint

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.fm.models.mib import MIB
from noc.services.classifier.ruleset import RuleSet
from noc.core.validators import is_oid
from noc.core.escape import json_escape
from noc.core.comp import smart_bytes


DEFAULT_CLEAN = datetime.timedelta(weeks=4)
CLEAN_WINDOW = datetime.timedelta(weeks=1)

name2codepoint["#39"] = 39
rx_cp = re.compile("&(%s);" % "|".join(name2codepoint))


def unescape(s):
    """
    Unescape HTML string
    """
    return rx_cp.sub(lambda m: chr(name2codepoint[m.group(1)]), s)


class Command(BaseCommand):
    help = "Manage events"

    def add_arguments(self, parser):
        # parser.add_argument("-s", "--selector", dest="selector", help="Selector name"),
        parser.add_argument("-s", "--resource-group", dest="resource_group", help="Group"),
        parser.add_argument("-o", "--object", dest="object", help="Managed Object's name"),
        parser.add_argument("-p", "--profile", dest="profile", help="Object's profile"),
        parser.add_argument("-e", "--event", dest="event", help="Event ID"),
        parser.add_argument("-c", "--class", dest="class", help="Event class name"),
        parser.add_argument("-T", "--trap", dest="trap", help="SNMP Trap OID or name"),
        parser.add_argument("-S", "--syslog", dest="syslog", help="SYSLOG Message RE"),
        parser.add_argument(
            "-d",
            "--suppress-duplicated",
            dest="suppress",
            action="store_true",
            help="Suppress duplicated subjects",
        ),
        parser.add_argument(
            "-l", "--limit", dest="limit", default=0, type=int, help="Limit action to N records"
        )
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        subparsers.add_parser("show")
        subparsers.add_parser("json")
        subparsers.add_parser("reclassify")
        test_rule = subparsers.add_parser("test-rule")
        test_rule.add_argument(
            "rules",
            help="Rules ids list",
            # required=True,
            nargs=argparse.REMAINDER,
        )
        # test_rule.add_argument("-S", "--syslog", dest="syslog", help="SYSLOG Message RE"),
        subparsers.add_parser("inject-event")

    rx_ip = re.compile(r"\d+\.\d+\.\d+\.\d+")
    rx_float = re.compile(r"\d+\.\d+")
    rx_int = re.compile(r"\d+")
    rx_volatile_date = re.compile(r"^.+?(?=%[A-Z])")

    def get_events(self, options):
        """
        Generator returning active events
        """
        c = ActiveEvent.objects.all()
        trap_oid = None
        syslog_re = None
        profile = options["profile"]
        if options["event"]:
            c = c.filter(id=ObjectId(options["event"]))
        if options["object"]:
            try:
                o = ManagedObject.objects.get(name=options["object"])
            except ManagedObject.DoesNotExist:
                self.die("Object not found: %s" % options["object"])
            c = c.filter(managed_object=o.id)
        if options["resource_group"]:
            try:
                s = ResourceGroup.objects.get(name=options["resource_group"])
            except ResourceGroup.DoesNotExist:
                self.die("ResourceGroup not found: %s" % options["resource_group"])
            c = c.filter(managed_object__in=[mo.id for mo in s.managed_objects])
        if options["class"]:
            o = EventClass.objects.filter(name=options["class"]).first()
            if not o:
                self.die("Event class not found: %s" % options["class"])
            c = c.filter(event_class=o.id)
        if options["trap"]:
            if is_oid(options["trap"]):
                trap_oid = options["trap"]
            else:
                trap_oid = MIB.get_oid(options["trap"])
                if trap_oid is None:
                    self.die("Cannot find OID for %s" % options["trap"])
            c = c.filter(raw_vars__source="SNMP Trap")
        if options["syslog"]:
            try:
                syslog_re = re.compile(options["syslog"], re.IGNORECASE)
            except Exception as e:
                self.die("Invalid RE: %s" % str(e))
            c = c.filter(raw_vars__source="syslog")
        for e in c:
            if profile:
                if not e.managed_object.profile == Profile[profile]:
                    continue
            if trap_oid:
                if (
                    "source" in e.raw_vars
                    and e.raw_vars["source"] == "SNMP Trap"
                    and "1.3.6.1.6.3.1.1.4.1.0" in e.raw_vars
                    and e.raw_vars["1.3.6.1.6.3.1.1.4.1.0"] == trap_oid
                ):
                    yield e
            elif syslog_re:
                if (
                    "source" in e.raw_vars
                    and e.raw_vars["source"] == "syslog"
                    and "message" in e.raw_vars
                    and syslog_re.search(e.raw_vars["message"])
                ):
                    yield e
            else:
                yield e

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    # def _handle(self, *args, **options):
    #     connect()
    #     try:
    #         handler = getattr(self, "handle_%s" % options["cmd"].replace("-", "_"))
    #         events = self.get_events(options)
    #         handler(options, events)
    #     except AttributeError:
    #         self.die("Invalid action: %s" % options["action"])

    def handle_show(self, options, events, show_json=False):
        limit = int(options["limit"])
        to_suppress = options["suppress"]
        seen = set()  # Message hashes
        if show_json:
            self.stdout.write("[\n")
            spool = None
        else:
            self.stdout.write("ID, Object, Class, Subject\n")
        for e in events:
            subject = unescape(e.subject)
            if to_suppress:
                # Replace volatile parts
                s = self.rx_volatile_date.sub("", subject)
                s = self.rx_ip.sub("$IP", s)
                s = self.rx_float.sub("$FLOAT", s)
                s = self.rx_int.sub("$INT", s)
                sh = hashlib.sha1(smart_bytes(s)).hexdigest()
                # Check subject is already seen
                if sh in seen:
                    # Suppress seen
                    continue
                seen.add(sh)
            if show_json:
                if spool:
                    print(spool + ",")
                s = ["    {"]
                s += ['        "profile": "%s",' % json_escape(e.managed_object.profile.name)]
                s += ['        "raw_vars": {']
                x = []
                vars = e.raw_vars
                keys = []
                lkeys = [k for k in vars if k not in ("1.3.6.1.2.1.1.3.0",)]
                for k in ("source", "profile", "1.3.6.1.6.3.1.1.4.1.0"):
                    if k in vars:
                        keys += [k]
                        lkeys.remove(k)
                keys += sorted(lkeys)
                for k in keys:
                    if k in ("collector",):
                        continue
                    x += ['            "%s": "%s"' % (json_escape(k), json_escape(vars[k]))]
                s += [",\n".join(x)]
                s += ["        }"]
                s += ["    }"]
                spool = "\n".join(s)
            else:
                self.stdout.write(
                    "%s, %s, %s, %s\n" % (e.id, e.managed_object.name, e.event_class.name, subject)
                )
            if limit:
                limit -= 1
                if not limit:
                    break
        if show_json:
            if spool:
                self.stdout.write(spool)
            print("]")

    def handle_json(self, option, events):
        return self.handle_show(option, events, show_json=True)

    @staticmethod
    def handle_reclassify(options, events):
        limit = int(options["limit"])
        for e in events:
            e.mark_as_new("Reclassification requested via CLI")
            print(e.id)
            if limit:
                limit -= 1
                if not limit:
                    break

    def handle_test_rule(self, rules, **kwargs):
        ruleset = RuleSet()
        ruleset.load()
        event_class_rules = EventClassificationRule.objects.filter(id__in=rules)
        for event_class_rule in event_class_rules:
            for event, v in event_class_rule.iter_cases():
                rule, e_vars = ruleset.find_rule(event, v)
                if rule is None:
                    self.print(
                        f"[{event_class_rule.name}] Testing with result: Cannot find matching rule"
                    )
                self.print(
                    f"[{event_class_rule.name}] Testing with result: {rule.name}: '{rule.event_class}': {e_vars}"
                )
                assert (
                    rule.event_class == event_class_rule.event_class
                ), f"Mismatched event class '{rule.event_class.name}' vs '{event_class_rule.event_class.name}'"
                var_ctx = {"message": event.message}
                var_ctx |= v
                var_ctx |= e_vars
                for t in rule.vars_transform or []:
                    t.transform(e_vars, var_ctx)
                if "interface__ifindex" in e_vars and "interface_mock" in v:
                    e_vars["interface"] = v.pop("interface_mock")
                elif "interface__ifindex" in e_vars:
                    assert (
                        "interface_mock" in e_vars
                    ), "interface_mock Required for ifindex transform test"
                try:
                    vv = ruleset.eval_vars(event, rule.event_class, e_vars)
                    self.print("End variables: ", vv)
                except Exception as e:
                    self.print(e)
                    self.print("End variables: ", var_ctx)


if __name__ == "__main__":
    Command().run()
