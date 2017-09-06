# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CLI Command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import argparse
# NOC modules
from noc.core.debug import error_report
from noc.config import config
from noc.core.tz import setup_timezone


class CommandError(Exception):
    pass


class BaseCommand(object):
    LOG_FORMAT = config.log_format

    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self.verbose_level = 0
        self.stdout = stdout
        self.stderr = stderr

    def print(self, *args, **kwargs):
        if "file" not in kwargs:
            kwargs["file"] = self.stdout
        if "flush" in kwargs and kwargs.pop("flush"):
            self.stdout.flush()
        print(*args, **kwargs)

    def run(self):
        """
        Execute command. Usually from script

        if __name__ == "__main__":
            Command().run()
        """
        try:
            setup_timezone()
        except ValueError as e:
            self.die(str(e))
        sys.exit(self.run_from_argv(sys.argv[1:]))

    def run_from_argv(self, argv):
        """
        Execute command. Usually from script

        if __name__ == "__main__":
            import sys
            sys.exit(Command.run_from_argv())
        """
        parser = self.create_parser()
        self.add_default_arguments(parser)
        self.add_arguments(parser)
        options = parser.parse_args(argv)
        cmd_options = vars(options)
        args = cmd_options.pop("args", ())
        loglevel = cmd_options.pop("loglevel")
        if loglevel:
            self.setup_logging(loglevel)
        enable_profiling = cmd_options.pop("enable_profiling", False)
        show_metrics = cmd_options.pop("show_metrics", False)
        if enable_profiling:
            # Start profiler
            import yappi
            yappi.start()
        try:
            return self.handle(*args, **cmd_options) or 0
        except CommandError as e:
            self.print(str(e))
            return 1
        except KeyboardInterrupt:
            self.print("Ctrl+C")
            return 3
        except AssertionError as e:
            if e.args[0]:
                self.print("ERROR: %s" % e.args[0])
            else:
                self.print("Assertion error")
            return 4
        except Exception:
            error_report()
            return 2
        finally:
            if enable_profiling:
                i = yappi.get_func_stats()
                i.print_all(
                    out=self.stdout,
                    columns={
                        0: ("name", 80),
                        1: ("ncall", 10),
                        2: ("tsub", 8),
                        3: ("ttot", 8),
                        4: ("tavg", 8)
                    }
                )
            if show_metrics:
                from noc.core.perf import apply_metrics
                d = apply_metrics({})
                self.print("Internal metrics:")
                for k in d:
                    self.print("%40s : %s" % (k, d[k]))

    def create_parser(self):
        return argparse.ArgumentParser()

    def handle(self, *args, **options):
        """
        Execute command
        """
        pass

    def add_default_arguments(self, parser):
        """
        Apply default parser arguments
        """
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--loglevel",
            action="store",
            dest="loglevel",
            help="Set loglevel",
            choices=[
                "critical", "error", "warning", "info", "debug", "none"
            ],
            default="info"
        )
        group.add_argument(
            "--quiet",
            action="store_const",
            dest="loglevel",
            const="none",
            help="Suppress logging"
        )
        group.add_argument(
            "--debug",
            action="store_const",
            dest="loglevel",
            const="debug",
            help="Debugging output"
        )
        group.add_argument(
            "--enable-profiling",
            action="store_true",
            help="Enable built-in profiler"
        )
        group.add_argument(
            "--show-metrics",
            action="store_true",
            help="Dump internal metrics"
        )

    def add_arguments(self, parser):
        """
        Apply additional parser arguments
        """
        pass

    def die(self, msg):
        raise CommandError(msg)

    def setup_logging(self, loglevel):
        """
        Set loglevel
        """
        import logging

        level = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "none": logging.NOTSET
        }[loglevel]
        # Get Root logger
        logger = logging.getLogger()
        if logger.level != level:
            logger.setLevel(level)
        logging.captureWarnings(True)
        fmt = logging.Formatter(self.LOG_FORMAT, None)
        for h in logger.handlers:
            h.setFormatter(fmt)
        for l in logger.manager.loggerDict.itervalues():
            if hasattr(l, "setLevel"):
                l.setLevel(level)
