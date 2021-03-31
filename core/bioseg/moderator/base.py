# ----------------------------------------------------------------------
# Biosegmentation moderator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Tuple, Type

# NOC modules
from noc.inv.models.biosegtrial import BioSegTrial
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.networksegmentprofile import BioCollisionPolicy
from noc.sa.models.managedobject import ManagedObject
from ..policies.base import Opponent
from ..policies.loader import loader

logger = logging.getLogger(__name__)


def moderate_pending() -> None:
    """
    Moderate pending trials
    :return:
    """
    pending = list(BioSegTrial.objects.filter(processed=False).order_by("id"))
    for trial in pending:
        moderate_trial(trial)


def moderate_trial(trial: BioSegTrial) -> None:
    """
    Moderate single trial

    :param trial:
    :return:
    """
    # Get objects when necessary
    attacker_object = None
    if trial.attacker_object_id:
        attacker_object = ManagedObject.get_by_id(trial.attacker_object_id)
        if not attacker_object:
            logger.info("Attacker's object is not found")
            trial.set_error("Attacker's object is not found", fatal=True)
            return
    target_object = None
    if trial.target_object_id:
        target_object = ManagedObject.get_by_id(trial.target_object_id)
        if not target_object:
            logger.info("Target's object is not found")
            trial.set_error("Target's object is not found", fatal=True)
            return
    # Get segments
    attacker = NetworkSegment.get_by_id(trial.attacker_id)
    if attacker_object and (not attacker or attacker.id != attacker_object.segment.id):
        attacker = attacker_object.segment
        logger.info("Attacker has been changed to %s" % attacker.name)
    if not attacker:
        logger.info("Attacker is not found")
        trial.set_error("Attacker is not found", fatal=True)
        return
    target = NetworkSegment.get_by_id(trial.target_id)
    if target_object and (not target or target.id != target_object.segment.id):
        target = target_object.segment
        logger.info("Target has been changed to %s" % target.name)
    if not target:
        logger.info("Target is not found")
        trial.set_error("Target is not found", fatal=True)
        return
    if attacker_object and target_object:
        logger.info(
            "Trying '%s' vs '%s' over '%s' -- '%s'",
            attacker.name,
            target.name,
            attacker_object.name,
            target_object.name,
        )
    else:
        logger.info("Trying '%s' vs '%s'", attacker.name, target.name)
    if attacker.id == target.id:
        logger.info("Cannot attack self")
        trial.set_error("Cannot attack self", fatal=True)
        return
    if attacker.profile.is_persistent and target.profile.is_persistent:
        # Persistent segment can attack persistent segment in case of ring topology,
        # when two calcified segments are finally tied together to close the ring.
        # Both calcified segments must share common parent
        if attacker.parent != target.parent:
            logger.info("Attack on persistent segment with other parent is declined")
            trial.set_error("Attack on persistent segment declined", fatal=True)
            return
    try:
        outcome, err, fatal = moderate(attacker, target, attacker_object, target_object)
        if outcome:
            logger.info("Outcome: %s", outcome)
            trial.set_outcome(outcome)
        else:
            logger.error("Error: %s", err)
            trial.set_error(err, fatal=fatal)
    except Exception as e:
        logger.error("ERROR: %s", e)
        trial.set_error(str(e), fatal=False)


def moderate(
    attacker: NetworkSegment,
    target: NetworkSegment,
    attacker_object: Optional[ManagedObject] = None,
    target_object: Optional[ManagedObject] = None,
) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Perform trial moderation

    :param attacker:
    :param target:
    :param attacker_object:
    :param target_object:
    :return: outcome, error, fatal
    """
    attacker_c_policy = get_collision_policy(
        attacker,
        target.profile.is_persistent,
        attacker_object=attacker_object,
        target_object=target_object,
    )
    if not attacker_c_policy:
        return None, "Not matched rule", True
    attacker_policy = loader.get_class(attacker_c_policy.policy)
    if not attacker_policy:
        return None, "Cannot determine attacker policy", True
    logger.info("Attacker policy is %s" % attacker_policy.name)
    target_c_policy = get_collision_policy(
        target,
        attacker.profile.is_persistent,
        attacker_object=attacker_object,
        target_object=target_object,
    )
    if not target_c_policy:
        return None, "Not matched rule", True
    target_policy = loader.get_class(target_c_policy.policy)
    if not target_policy:
        return None, "Cannot determine target policy", False
    logger.info("Target policy is %s" % target_policy.name)
    # Calculate effective policy
    effective_policy_name = target_policy.get_effective_policy_name(target, attacker_policy.name)
    effective_policy = loader.get_class(effective_policy_name)
    if not effective_policy:
        return None, "Unknown policy '%s'" % effective_policy_name, False
    logger.info("Effective policy is %s" % effective_policy.name)
    # Get settings
    if effective_policy_name == attacker_c_policy.policy:
        cp, power_funcs = attacker_c_policy.calcified_profile, attacker_c_policy.power_function
    else:
        cp, power_funcs = target_c_policy.calcified_profile, target_c_policy.power_function
    logger.info("Effective settings is: %s:%s", cp, power_funcs)
    # Do trial
    outcome = effective_policy(
        Opponent(attacker, attacker_object),
        Opponent(target, target_object),
        logger=logger,
        calcified_profile=cp,
        segment_power_function=power_funcs,
    ).trial()
    return outcome, None, False


def get_collision_policy(
    seg: NetworkSegment,
    is_persistent: bool,
    attacker_object: Optional[ManagedObject] = None,
    target_object: Optional[ManagedObject] = None,
) -> Optional[Type[BioCollisionPolicy]]:
    attacker_level = attacker_object.object_profile.level if attacker_object else None
    target_level = target_object.object_profile.level if target_object else None
    for cp in seg.profile.bio_collision_policy:
        logger.debug(
            "Check policy rule: %s, result: %s, policy: %s",
            cp,
            cp.check(is_persistent, attacker_level, target_level),
            cp.policy,
        )
        if cp.check(is_persistent, attacker_level, target_level):
            return cp
    return None
