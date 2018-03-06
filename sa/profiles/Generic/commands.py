# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.commands
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from threading import Lock
# Third-party modules
import six
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.icommands import ICommands

rx_lock = Lock()


class Script(BaseScript):
    """
    Execute a list of CLI commands and return a list of results
    """
    name = "Generic.commands"
    interface = ICommands
    requires = []

    def execute(self, commands, ignore_cli_errors=False, include_commands=False):
        cli = self.safe_cli if ignore_cli_errors else self.cli
        r = []
        for c in self.format_multiline(commands):
            if include_commands:
                r += [c + "\n\n" + cli(c)]
            else:
                r += [cli(c)]
        return r

    def safe_cli(self, cmd):
        """
        Safer version of Script.cli. Always returns text on syntax error
        :param cmd:
        :return:
        """
        try:
            return self.cli(cmd)
        except self.CLISyntaxError as e:
            return "%%ERROR: %s" % e

    def format_multiline(self, commands):
        """
        Reformat commands according to Profile.pattern_multiline_commands
        :param commands:
        :return:
        """
        # No multiline commands support
        if not self.profile.pattern_multiline_commands:
            return commands
        # Compile patterns
        with rx_lock:
            patterns = getattr(self.profile, "_pattern_multiline_commands", None)
            if not patterns:
                if isinstance(self.profile.pattern_multiline_commands, six.string_types):
                    patterns = [re.compile(self.profile.pattern_multiline_commands)]
                else:
                    patterns = [re.compile(p) for p in self.profile.pattern_multiline_commands]
                self.profile._pattern_multiline_commands = patterns
        # Reformat text
        r = []
        delimiter = None
        continuation = False
        for cmd in commands:
            if continuation:
                # Extend previous line
                r[-1] = r[-1] + self.profile.command_submit + cmd
                if delimiter:
                    if delimiter in cmd:
                        # Delimiter found, stop continuation
                        continuation = False
                        delimiter = None
                    continue
                # Continuations without delimiters can extend
                # multiple lines, so pass to next check
            else:
                # No continuation, add new command
                r += [cmd]
            match = self.find_match(patterns, cmd)
            if match:
                if match.groups():
                    delimiter = match.group(1)
                else:
                    delimiter = None  # No delimiter
                # Mark next line as continuation
                continuation = True
            else:
                continuation = False
                delimiter = None
        # Check for unterminated continuation
        if continuation:
            raise self.CLISyntaxError("Unterminated multiline string")
        return r

    def find_match(self, patterns, s):
        """
        Return match object for list of patterns against string
        :param patterns:
        :param s:
        :return:
        """
        for rx in patterns:
            match = rx.match(s)
            if match:
                return match
        return None
