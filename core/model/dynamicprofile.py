# ----------------------------------------------------------------------
# Dynamic Profile Classification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from functools import partial
from typing import Callable, Optional

# NOC modules
from noc.models import get_model, get_model_id, is_document
from noc.core.matcher import build_matcher
from noc.core.defer import call_later
from noc.core.change.policy import change_tracker
from noc.core.middleware.tls import get_user

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
        if not hasattr(profile_model, "get_effective_profile"):
            # Dynamic classification not supported
            return NotImplementedError("Method 'get_effective_profile' required")
        instance = instance or document
        # Set to Manual if set profile, Default Profile
        policy = getattr(instance, "get_dynamic_classification_policy", None)
        if policy and policy() == "D":
            # Dynamic classification not enabled
            return None
        profile_id = profile_model.get_effective_profile(instance)
        if not profile_id:
            logger.info("[%s] Nothing profile for match", str(instance))
            return None
        profile_field = profile_field or "profile"
        profile = getattr(instance, profile_field)
        if profile_id and profile.id != profile_id:
            profile = profile_model.get_by_id(profile_id)
            setattr(instance, profile_field, profile)

    def on_profile_post_save(
        sender,
        instance=None,
        document=None,
        instance_model_id=None,
        profile_field=profile_field,
        *args,
        **kwargs,
    ):
        instance = instance or document
        if document:
            changed_fields = getattr(document, "_changed_fields", None) or []
        else:
            changed_fields = getattr(instance, "changed_fields", None) or []
        if (
            not changed_fields
            or "match_rules" in changed_fields
            or "dynamic_classification_policy" in changed_fields
        ):
            user = get_user()
            call_later(
                "noc.core.model.dynamicprofile.update_profiles",
                delay=60,
                instance_model_id=instance_model_id,
                profile_model_id=get_model_id(instance),
                profile_field=profile_field,
                profile_id=str(instance.id),
                user=str(user) if user else None,
            )

    def inner(m_cls):
        # Install profile set handlers
        if not hasattr(m_cls, "get_matcher_ctx"):
            raise NotImplementedError("Method 'get_matcher_ctx' required")
        if is_document(m_cls):
            from mongoengine import signals as mongo_signals

            if sync_profile:
                # Profile set handlers
                mongo_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
                mongo_signals.post_save.connect(
                    partial(on_profile_post_save, instance_model_id=get_model_id(m_cls)),
                    sender=get_model(profile_model_id),
                    weak=False,
                )
        else:
            from django.db.models import signals as django_signals

            if sync_profile:
                # Profile set handlers
                django_signals.pre_save.connect(on_pre_save, sender=m_cls, weak=False)
                django_signals.post_save.connect(
                    partial(on_profile_post_save, instance_model_id=get_model_id(m_cls)),
                    sender=get_model(profile_model_id),
                    weak=False,
                )
        # Install Profile Labels expose
        return m_cls

    return inner


def update_profiles(
    instance_model_id,
    profile_model_id,
    profile_field: str = "profile",
    profile_id: Optional[str] = None,
    user: Optional[str] = None,
):
    """Update profile"""

    def get_label(oo):
        if hasattr(oo, "name"):
            label = oo.name
        elif hasattr(oo, "label"):
            label = oo.label
        else:
            label = str(oo)
        return label

    if user:
        logger.info(
            "[%s] Running update Profile for Match Rules (by user '%s')",
            profile_model_id,
            user,
        )
    else:
        logger.info(
            "[%s] Running update Profile for Match Rules",
            profile_id,
        )
    profile_model = get_model(profile_model_id)
    classifier = profile_model.get_profiles_matcher()
    instance_model = get_model(instance_model_id)
    oos = instance_model.objects.filter()
    if profile_id:
        # iter_affected_instances
        profile = profile_model.get_by_id(profile_id)
        oos = instance_model.objects.filter(profile.get_instance_affected_query(include_match=True))
    processed, changed = 0, 0
    with change_tracker.bulk_changes(user=user):
        # Same Profile, Groups, Labels filter
        for o in oos:
            ll = get_label(o)
            processed += 1
            ctx = o.get_matcher_ctx()
            for p_id, matchers in classifier:
                match = any(match(ctx) for match in matchers)
                if match:
                    break
            else:
                logger.debug("[%s|%s] Nothing profile for match", o.id, ll)
                continue
            profile = getattr(o, profile_field)
            if str(p_id) != str(profile.id):
                profile = profile_model.get_by_id(p_id)
                if not profile:
                    logger.error(
                        "[%s|%s] Invalid profile with id '%s'. Skipping",
                        o.id,
                        ll,
                        p_id,
                    )
                    return
                if profile != o.profile:
                    logger.info(
                        "[%s|%s] Object has been classified as '%s'", o.id, ll, profile.name
                    )
                    setattr(o, profile_field, profile)
                    o.save()
                    changed += 1
    logger.info(
        "[%s] End update Profile. Processed: %s/Changed: %s", profile_id, processed, changed
    )
