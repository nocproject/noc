# ----------------------------------------------------------------------
# CLI Command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import os
import argparse
from typing import NoReturn

# NOC modules
from noc.config import config
from noc.core.tz import setup_timezone


class CommandError(Exception):
    pass


class BaseCommand(object):
    LOG_FORMAT = config.log_format
    help = ""  # Help text (shows ./noc help)

    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self.verbose_level = 0
        self.stdout = stdout
        self.stderr = stderr
        self.is_debug = False

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
        show_usage = cmd_options.pop("show_usage", False)
        self.no_progressbar = cmd_options.pop("no_progressbar", False)
        if enable_profiling:
            # Start profiler
            import yappi

            yappi.start()
        try:
            if show_usage:
                import resource

                start_usage = resource.getrusage(resource.RUSAGE_SELF)
            return self.handle(*args, **cmd_options) or 0
        except CommandError as e:
            self.print(str(e))
            return 1
        except KeyboardInterrupt:
            self.print("Ctrl+C")
            return 3
        except AssertionError as e:
            if e.args and e.args[0]:
                self.print("ERROR: %s" % e.args[0])
            else:
                self.print("Assertion error: %s" % e)
            return 4
        except Exception:
            from noc.core.debug import error_report

            error_report()
            return 2
        finally:
            if show_usage:
                stop_usage = resource.getrusage(resource.RUSAGE_SELF)
                self.show_usage(start_usage, stop_usage)
            if enable_profiling:
                i = yappi.get_func_stats()
                i.print_all(
                    out=self.stdout,
                    columns={
                        0: ("name", 80),
                        1: ("ncall", 10),
                        2: ("tsub", 8),
                        3: ("ttot", 8),
                        4: ("tavg", 8),
                    },
                )
            if show_metrics:
                from noc.core.perf import apply_metrics

                d = apply_metrics({})
                self.print("Internal metrics:")
                for k in d:
                    self.print("%40s : %s" % (k, d[k]))

    def create_parser(self) -> argparse.ArgumentParser:
        cmd = os.path.basename(sys.argv[0])
        if cmd.endswith(".py"):
            cmd = "noc %s" % cmd[:-3]
        return argparse.ArgumentParser(prog=cmd)

    def handle(self, *args, **options):
        """
        Execute command
        """

    def add_default_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Apply default parser arguments
        """
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--loglevel",
            action="store",
            dest="loglevel",
            help="Set loglevel",
            choices=["critical", "error", "warning", "info", "debug", "none"],
            default="info",
        )
        group.add_argument(
            "--quiet", action="store_const", dest="loglevel", const="none", help="Suppress logging"
        )
        group.add_argument(
            "--debug", action="store_const", dest="loglevel", const="debug", help="Debugging output"
        )
        group.add_argument(
            "--enable-profiling", action="store_true", help="Enable built-in profiler"
        )
        group.add_argument("--show-metrics", action="store_true", help="Dump internal metrics")
        group.add_argument("--no-progressbar", action="store_true", help="Disable progressbar")
        group.add_argument(
            "--show-usage", action="store_true", help="Dump resource usage statistics"
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Apply additional parser arguments
        """

    def die(self, msg: str) -> NoReturn:
        raise CommandError(msg)

    def setup_logging(self, loglevel: str) -> None:
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
            "none": logging.NOTSET,
        }[loglevel]
        # Get Root logger
        logger = logging.getLogger()
        if logger.level != level:
            logger.setLevel(level)
        logging.captureWarnings(True)
        fmt = logging.Formatter(self.LOG_FORMAT, None)
        for h in logger.handlers:
            h.setFormatter(fmt)
        for lg in logger.manager.loggerDict.values():
            if isinstance(lg, logging.Logger) and lg.name.startswith("pymongo"):
                # Fix spam debug messages on pymongo
                lg.setLevel(logging.INFO)
                continue
            if hasattr(lg, "setLevel"):
                lg.setLevel(level)
        self.is_debug = level <= logging.DEBUG

    def progress(self, iter, max_value=None):
        """
        Yield iterable and show progressbar
        :param iter:
        :param max_value:
        :return:
        """
        if self.no_progressbar:
            yield from iter
        else:
            import progressbar

            yield from progressbar.progressbar(iter, max_value=max_value)

    def show_usage(self, start, stop):
        """
        Show resource usage
        :param start:
        :param stop:
        :return:
        """
        r = [
            "Resource usage:",
            f"             User time   : {stop.ru_utime - start.ru_utime:.6f}",
            f"             System time : {stop.ru_stime - start.ru_stime:.6f}",
            f"             Max RSS     : {stop.ru_maxrss - start.ru_maxrss}k",
            f"        Shared mem. size : {stop.ru_ixrss - start.ru_ixrss}k",
            f"      Unshared mem. size : {stop.ru_idrss - start.ru_idrss}k",
            f"     Unshared stack size : {stop.ru_isrss - start.ru_isrss}k",
            f"    Page faults w/o. I/O : {stop.ru_minflt - start.ru_minflt}",
            f"      Page faults w. I/O : {stop.ru_majflt - start.ru_majflt}",
            f"               Swap outs : {stop.ru_nswap - start.ru_nswap}",
            f"               In blocks : {stop.ru_inblock - start.ru_inblock}",
            f"              Out blocks : {stop.ru_oublock - start.ru_oublock}",
            f"           Messages sent : {stop.ru_msgsnd - start.ru_msgsnd}",
            f"       Messages received : {stop.ru_msgrcv - start.ru_msgrcv}",
            f"                 Signals : {stop.ru_nsignals - start.ru_nsignals}",
            f"   Voluntary context sw. : {stop.ru_nvcsw - start.ru_nvcsw}",
            f" Involuntary context sw. : {stop.ru_nivcsw - start.ru_nivcsw}",
        ]
        self.print("\n".join(r))
