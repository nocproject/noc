# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLI Command
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import argparse
## NOC modules
from noc.lib.debug import error_report


class CommandError(Exception):
    pass


class BaseCommand(object):
    LOG_FORMAT = "%(asctime)s [%(name)s] %(message)s"

    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self.verbose_level = 0
        self.stdout = stdout
        self.stderr = stderr

    def run(self):
        """
        Execute command. Usually from script

        if __name__ == "__main__":
            Command().run()
        """
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
        try:
            return self.handle(*args, **cmd_options) or 0
        except CommandError, why:
            self.stderr.write(str(why))
            self.stderr.write("\n")
            self.stderr.flush()
            return 1
        except Exception:
            error_report()
            return 2

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
        parser.add_argument(
            "--loglevel",
            action="store",
            dest="loglevel",
            help="Set loglevel",
            choices=[
                "critical", "error", "warning", "info", "debug", "none"
            ],
            default="info"
        )
        parser.add_argument(
            "--quiet",
            action="store_const",
            dest="loglevel",
            const="none",
            help="Suppress logging"
        )
        parser.add_argument(
            "--debug",
            action="store_const",
            dest="loglevel",
            const="debug",
            help="Debugging output"
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
        logger = logging.getLogger()
        logging.captureWarnings(True)
        fmt = logging.Formatter(self.LOG_FORMAT, None)
        for l in logger.manager.loggerDict.itervalues():
            if hasattr(l, "setLevel"):
                l.setLevel({
                    "critical": logging.CRITICAL,
                    "error": logging.ERROR,
                    "warning": logging.WARNING,
                    "info": logging.INFO,
                    "debug": logging.DEBUG,
                    "none": logging.NOTSET
                }[loglevel])
        for h in logger.handlers:
            h.setFormatter(fmt)
