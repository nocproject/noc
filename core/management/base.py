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
        self.add_arguments(parser)
        options = parser.parse_args(argv)
        cmd_options = vars(options)
        args = cmd_options.pop("args", ())
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

    def add_arguments(self, parser):
        """
        Apply additional parser arguments
        """
        pass

    def die(self, msg):
        raise CommandError(msg)
