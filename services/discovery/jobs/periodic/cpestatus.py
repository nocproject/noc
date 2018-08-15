# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CPE Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo import InsertOne, UpdateOne, UpdateMany
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.cpestatus import CPEStatus


class CPEStatusCheck(DiscoveryCheck):
    """
    Interface status discovery
    """
    name = "cpestatus"
    required_script = "get_cpe_status"
    possible_capabilities = {
        "Network | PON | OLT"
    }
    UNKNOWN_STATUS = "unknown"

    def handler(self):
        policy = self.get_policy()
        # Collect CPE statuses
        if policy == "S":
            current = self.get_current_statuses()
        else:
            current = self.get_current_cpe()
        # Collect last statuses
        last = self.get_last_statuses(current)
        # Apply changes
        self.apply_changes(current, last)

    def get_policy(self):
        if self.is_box:
            return self.object.object_profile.box_discovery_cpestatus_policy
        else:
            return self.object.object_profile.periodic_discovery_cpestatus_policy

    def has_required_capabilities(self):
        caps = set(self.get_caps())
        if caps & self.possible_capabilities:
            return True
        self.logger.info(
            "Object hasn't any of capabilities %s. Skipping",
            ", ".join("'%s'" % c for c in self.possible_capabilities)
        )
        return False

    def get_current_cpe(self):
        """
        Get full CPE attributes from equipment
        :return: dict of global_id -> status
        """
        return dict((x["global_id"], x) for x in self.object.scripts.get_cpe())

    def get_current_statuses(self):
        """
        Get current statuses from equipment
        :return: dict of global_id -> status
        """
        return dict((x["global_id"], x) for x in self.object.scripts.get_cpe_status())

    def get_last_statuses(self, data):
        """
        Get current database statuses. Include:

        * All object's CPEs
        * All Managed Object's CPEs
        :param data: global_id -> current status
        :return: dict of global_id -> status
        """
        gids = list(data)
        q = {
            "managed_object": self.object.id
        }
        if len(gids) == 1:
            q = {
                "$or": [
                    q,
                    {"global_id": gids[0]}
                ]
            }
        elif len(gids) > 1:
            q = {
                "$or": [
                    q,
                    {"global_id": {"$in": gids}}
                ]
            }
        return dict((x["global_id"], x) for x in CPEStatus._get_collection().find(q))

    def apply_changes(self, current, last):
        """
        Apply database changes
        :param current: List of CPE statuses, received from equipment
        :param last:
        :return:
        """
        bulk = []
        left = set(
            global_id
            for global_id in last
            if last[global_id].get("status") != self.UNKNOWN_STATUS
        )
        for global_id in current:
            s = current[global_id]
            s["managed_object"] = self.object.id
            if global_id in last:
                # Already seen
                diff, changes = self.get_difference(last[global_id], s)
                if diff:
                    # Changed
                    self.logger.info(
                        "[%s] CPE status changed: %s",
                        global_id,
                        ", ".join(changes)
                    )
                    bulk += [UpdateOne({
                        "global_id": global_id
                    }, {
                        "$set": diff
                    })]
                if global_id in left:
                    left.remove(global_id)
            else:
                # New
                diff, changes = self.get_difference({}, s)
                self.logger.info(
                    "[%s] New CPE: %s",
                    global_id,
                    ", ".join(changes)
                )
                bulk += [InsertOne(diff)]
        # Update missed statuses
        if left:
            if len(left) == 1:
                bulk += [UpdateOne({
                    "global_id": left.pop()
                }, {
                    "$set": {"status": self.UNKNOWN_STATUS}
                })]
            else:
                bulk += [UpdateMany({
                    "global_id": {"$in": list(left)}
                }, {
                    "$set": {"status": self.UNKNOWN_STATUS}
                })]
            for global_id in sorted(left):
                self.logger.info(
                    "[%s] CPE status missing. Changing status to %s",
                    global_id,
                    self.UNKNOWN_STATUS
                )
        # Apply changes
        if bulk:
            self.logger.info("Saving %d changes", len(bulk))
            CPEStatus._get_collection().bulk_write(bulk)
        else:
            self.logger.info("Nothing changed")

    def get_difference(self, old, new):
        """
        Calculate difference between two dicts
        :param old:
        :param new:
        :return: dict of changes, list of changes
        """
        r = {}
        changes = []
        for k in new:
            if new[k] is None or new[k] == "":
                continue
            if k not in old:
                # New attribute
                r[k] = new[k]
                changes += ["%s = %s" % (k, new[k])]
            elif new[k] != old[k]:
                # Changed attribute
                r[k] = new[k]
                changes += ["%s: %s -> %s" % (k, old[k], new[k])]
        return r, changes
