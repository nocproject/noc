# ----------------------------------------------------------------------
#  PatternSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import logging
import re

# NOC modules
from noc.core.validators import is_oid
from noc.fm.models.ignorepattern import IgnorePattern


logger = logging.getLogger(__name__)

E_SRC_SYSLOG = "syslog"
E_SRC_SNMP_TRAP = "SNMP Trap"


class PatternSet(object):
    def __init__(self):
        self.i_patterns = {}  # (profile, chain) -> [rule, ..., rule]

    def load(self):
        """
        Load Ignore Patterns from database
        """
        logger.info("Loading Ignore Patterns")
        n = 0
        i_patterns = defaultdict(list)
        # Initialize Ignore Patterns
        for p in IgnorePattern.objects.filter(is_active=True):
            try:
                re.compile(p.pattern)
            except re.error as e:
                logger.error("Invalid ignore pattern '%s' (%s)" % (p.pattern, e))
                continue
            i_patterns[p.source] += [p.pattern]
            n += 1
        self.i_patterns = i_patterns
        logger.info("%d Ignore patterns are loaded in the %d chains", n, len(self.i_patterns))

    def find_ignore_masks(self, source):
        if self.i_patterns:
            mask = self.i_patterns.get(source)
            if mask:
                logging.debug("Setting ignore patterns for %s: %s" % (source, mask))
                return [re.compile(x) for x in mask]
        return []

    def find_ignore_rule(self, event, vars):
        """
        Find first matching ignore pattern
        :param event: Event
        :param vars: raw and resolved variables
        :type vars: dict
        :returns: True if matching pattern
        """
        ignore_mask = self.find_ignore_masks(event.source)
        if ignore_mask:
            if event.source == E_SRC_SYSLOG:
                msg = vars.get("message", "")
                if any(r for r in ignore_mask if r.search(msg)):
                    logging.debug("Ignored")
                    return True
            elif event.source == E_SRC_SNMP_TRAP:
                oid = vars.get("1.3.6.1.6.3.1.1.4.1.0", "")
                if not oid or not is_oid(oid):
                    return False
                if any(r for r in ignore_mask if r.search(oid)):
                    logging.debug("Ignored")
                    return True
