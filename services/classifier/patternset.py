# ----------------------------------------------------------------------
#  PatternSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import re
from collections import defaultdict
from typing import Dict, List, Tuple

# NOC modules
from noc.core.validators import is_oid
from noc.core.fm.event import Event
from noc.core.fm.enum import EventSource
from noc.fm.models.ignorepattern import IgnorePattern


logger = logging.getLogger(__name__)


class PatternSet(object):
    def __init__(self):
        self.i_patterns: Dict[str, List[Tuple[str, str]]] = (
            {}
        )  # (profile, chain) -> [rule, ..., rule]
        self.add_patterns = 0

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
            i_patterns[p.source.value] += [str(p.id), p.pattern]
            n += 1
        self.i_patterns = i_patterns
        logger.info("%d Ignore patterns are loaded in the %d chains", n, len(self.i_patterns))

    def update_pattern(self, rid: str, data):
        """Update rule from lookup"""
        source = data["sources"][0]
        r = []
        try:
            re.compile(data["message_rx"])
        except re.error as e:
            logger.error("Invalid ignore pattern '%s' (%s)" % (data["message_rx"], e))
            return
        update = False
        for p in self.i_patterns.get(source) or []:
            if p[0] == rid:
                r.append((rid, data["message_rx"]))
                update |= True
                logger.info("[%s] Update Ignore Pattern: %s", rid, data["message_rx"])
                continue
            r.append(p)
        if not update:
            r.append((rid, data["message_rx"]))
            logger.info("[%s] New Ignore Pattern: %s", rid, data["message_rx"])
            self.add_patterns += 1
        self.i_patterns[source] = r

    def delete_pattern(self, rid: str):
        """Remove rule from lookup"""
        r = []
        for source in self.i_patterns:
            for p in self.i_patterns[source]:
                if p[0] == rid:
                    logger.info("[%s] Delete Ignore Pattern", rid)
                    continue
                r.append(p)
            if len(self.i_patterns[source]) != len(r):
                self.i_patterns[source] = r

    def find_ignore_masks(self, source):
        if self.i_patterns:
            mask = self.i_patterns.get(source)
            if mask:
                logging.debug("Setting ignore patterns for %s: %s", source, mask)
                return [re.compile(x) for _, x in mask]
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
