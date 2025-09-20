# ----------------------------------------------------------------------
# Dynamic Profile Classification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Callable

# NOC modules
from noc.models import get_model, is_document
from noc.core.matcher import build_matcher

logger = logging.getLogger()


def get_matcher(self) -> Callable:
    """"""
    expr = []
    for r in self.match_rules:
        expr.append(r.get_match_expr())
    if len(expr) == 1:
        return build_matcher(expr[0])
    return build_matcher({"$or": expr})


def is_match(self, o) -> bool:
    """Local Match rules"""
    matcher = self.get_matcher()
    ctx = o.get_matcher_ctx()
    return matcher(ctx)


# apply_effective_labels
# apply_effective_groups
# apply_effective_profile


def dynamic_profile(
    profile_model_id: str,
    profile_field: str = "profile",
    sync_profile: bool = True,
    append_labels: bool = False,
):
    """
    Args:
        profile_model_id: Profile Model, that assigned
        profile_field: Model profile field
        sync_profile: Assigned profile by match rules
        append_labels: Expose profile labels to reference instances
    """

    def on_pre_save(
        sender,
        instance=None,
        document=None,
        profile_model_id=profile_model_id,
        profile_field=profile_field,
        *args,
        **kwargs,
    ):
        """
        Args:
            sender:
            instance:
            document:
            profile_model_id:
            profile_field:
            args:
            kwargs:
        """
        profile_model = get_model(profile_model_id)
        if not hasattr(profile_model, "match_rules"):
            # Dynamic classification not supported
            return NotImplementedError("Method 'match_rules' required")
        instance = instance or document
        policy = getattr(instance, "get_dynamic_classification_policy", None)
        if policy and policy() == "D":
            # Dynamic classification not enabled
            return
        ctx = instance.get_matcher_ctx()
        for profile_id, match in profile_model.get_profiles_matcher():
            if match(ctx):
                break
        else:
            logger.info("[%s] Nothing profile for match", instance.name)
            return
        profile_field = profile_field or "profile"
        profile = getattr(instance, profile_field)
        if profile_id and profile.id != profile_id:
            profile = profile_model.get_by_id(profile_id)
            setattr(instance, profile_field, profile)

    def inner(m_cls):
        # Install profile set handlers
        if not hasattr(m_cls, "get_matcher_ctx"):
            raise NotImplementedError("Method 'get_matcher_ctx' required")
        if is_document(m_cls):
            from mongoengine import signals as mongo_signals

            if sync_profile:
                # Profile set handlers
                mongo_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
        else:
            from django.db.models import signals as django_signals

            if sync_profile:
                # Profile set handlers
                django_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)

        # Install Profile Labels expose
        return m_cls

    return inner
