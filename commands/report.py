# ----------------------------------------------------------------------
# ./noc report command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import os
import re
from typing import Optional, Dict, Any

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import RunParams, OutputType
from noc.core.datasources.loader import loader
from noc.aaa.models.user import User
from noc.main.models.report import Report


class Command(BaseCommand):
    DEFAULT_LIMIT = 20

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        #
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument("--report", "-r", help="Report to run", required=True)
        run_parser.add_argument("--user", "-u", help="User ")
        run_parser.add_argument("--lang", "-l", default="en", help="Report language")
        run_parser.add_argument("--out-type", "-o", default="csv", help="Report Output type")
        run_parser.add_argument(
            "arguments", nargs=argparse.REMAINDER, help="Arguments passed to script"
        )
        subparsers.add_parser("list")
        subparsers.add_parser("list-ds")
        query_ds_parser = subparsers.add_parser("query-ds")
        query_ds_parser.add_argument("--datasource", "-d", help="Datasource")
        query_ds_parser.add_argument("query", nargs=1, help="Datasource Query")
        query_ds_parser.add_argument(
            "arguments", nargs=argparse.REMAINDER, help="Arguments passed to script"
        )

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_run(
        self,
        report: str,
        arguments,
        user: Optional[str] = None,
        lang="en",
        out_type="csv",
        **kwargs,
    ):
        if user:
            user = User.get_by_username(user)
        if user:
            pref_lang = user.preferred_language
        else:
            pref_lang = lang
        report: "Report" = Report.get_by_id(report)
        report_engine = ReportEngine(
            report_execution_history=False,
            report_print_error=True,
        )
        args = self.get_report_args(arguments)
        self.print(f"Running report with arguments: {args}")
        rp = RunParams(
            report=report.get_config(pref_lang),
            output_type=OutputType(out_type),
            params=args,
        )
        try:
            out_doc = report_engine.run_report(r_params=rp)
        except ValueError as e:
            self.print(f"Error when execute report: {e}")
            self.die(str(e))
        self.print(out_doc.get_content())

    def handle_list(self, **kwargs):
        for r in Report.objects.filter().order_by("name"):
            self.print(f"Report: {r.id} | {r.name} ({r.title})")
            # Language params, user param, List all params for report (r - required)

    def handle_list_ds(self, **kwargs):
        for ds in loader:
            self.print(f"Datasource: {ds}")

    def handle_query_ds(self, datasource, query, arguments, **kwargs):
        args = self.get_report_args(arguments)
        ds = loader[datasource]
        self.print(f"Running DataSource with arguments: {args}")
        r = ds.query_sync(**args)
        self.print(r.sql(query[0]))

    rx_arg = re.compile(r"^(?P<name>[a-zA-Z][a-zA-Z0-9_]*)(?P<op>:?=@?)(?P<value>.*)$")

    def get_report_args(self, arguments) -> Dict[str, Any]:
        """
        Parse arguments and return script's
        """

        def read_file(path):
            if not os.path.exists(path):
                self.die("Cannot open file '%s'" % path)
            with open(path) as f:
                return f.read()

        def parse_json(j):
            try:
                return orjson.loads(j)
            except ValueError as e:
                self.die("Failed to parse JSON: %s" % e)

        args = {}
        for a in arguments:
            match = self.rx_arg.match(a)
            if not match:
                self.die("Malformed parameter: '%s'" % a)
            name, op, value = match.groups()
            if op == "=":
                # Set parameter
                args[name] = value
            elif op == "=@":
                # Read from file
                args[name] = read_file(value)
            elif op == ":=":
                # Set to JSON value
                args[name] = parse_json(value)
            elif op == ":=@":
                # Set to JSON value from a file
                args[name] = parse_json(read_file(value))
        return args


if __name__ == "__main__":
    Command().run()
