# ----------------------------------------------------------------------
#  PatternSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import logging
import re

# NOC modules
from noc.core.validators import is_oid
from noc.core.fm.event import Event
from noc.core.fm.enum import EventSource
from noc.fm.models.ignorepattern import IgnorePattern


logger = logging.getLogger(__name__)


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
                logging.debug("Setting ignore patterns for %s: %s", source, mask)
                return [re.compile(x) for x in mask]
        return []

    def find_ignore_rule(self, event: Event):
        """
        Find first matching ignore pattern
        :param event: Event instance
        :type event: Event
        :returns: True if matching pattern
        """
        ignore_mask = self.find_ignore_masks(event.type.source.value)
        if ignore_mask:
            if event.type.source == EventSource.SYSLOG:
                msg = event.message or ""
                if any(r for r in ignore_mask if r.search(msg)):
                    logging.debug("Ignored")
                    return True
            elif event.type.source == EventSource.SNMP_TRAP:
                oid = event.type.id or ""
                if not oid or not is_oid(oid):
                    return False
                if any(r for r in ignore_mask if r.search(oid)):
                    logging.debug("Ignored")
                    return True
