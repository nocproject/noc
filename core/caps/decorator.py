# ----------------------------------------------------------------------
# @capabilities decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, List, Dict, Any, Iterable

# NOC modules
from noc.models import is_document, get_model_id
from noc.core.models.inputsources import InputSource
from noc.core.change.policy import change_tracker
from noc.core.change.model import ChangeField
from noc.core.change.decorator import get_datastreams, get_domains, get_applied_rules
from .types import CapsValue, CapsConfig

caps_logger = logging.getLogger(__name__)


def iter_model_caps(
    self, scope: Optional[str] = None, include_default: bool = False
) -> Iterable[CapsValue]:
    """Iterate over Model Capabilities"""
    from noc.inv.models.capability import Capability

    configs = self.get_caps_config()

    for ci in self.caps or []:
        c = Capability.get_by_id(ci["capability"])
        if not c:
            caps_logger.info("Removing unknown capability id %s", ci["capability"])
            continue
        cs = ci.get("scope") or None
        if scope and scope != cs:
            continue
        try:
            source = InputSource(ci.get("source", "manual"))
        except ValueError:
            caps_logger.info("[%s] Unknown InputSource '%s'. Skipping...", c.name, ci.get("source"))
            continue
        value = ci.get("value")
        value = c.clean_value(value)
        yield CapsValue(
            capability=c,
            value=value,
            source=source,
            scope=cs,
            config=configs.pop(str(c.id), CapsConfig()),
        )
    if not include_default:
        return
    for c, cfg in configs.items():
        c = Capability.get_by_id(c)
        yield CapsValue(
            capability=c,
            value=c.clean_value(cfg.default_value) if cfg.default_value else None,
            source=InputSource.CONFIG,
            config=cfg,
        )


def iter_document_caps(
    self, scope: Optional[str] = None, include_default: bool = False
) -> Iterable[CapsValue]:
    """Iterate over document Capabilities"""
    from noc.inv.models.capability import Capability

    configs = self.get_caps_config()
    processed = set()
    for ci in self.caps or []:
        if scope and scope != ci.scope:
            continue
        try:
            cs = InputSource(ci.source or "manual")
        except ValueError:
            cs = InputSource.UNKNOWN
        cv = ci.value
        cv = ci.capability.clean_value(cv)
        yield CapsValue(
            capability=ci.capability,
            value=cv,
            source=cs,
            scope=ci.scope or None,
            config=configs.get(str(ci.capability.id), CapsConfig()),
        )
        processed.add(ci.capability.id)
    if not include_default:
        return
    for c, cfg in configs.items():
        c = Capability.get_by_id(c)
        if c.id in processed:
            continue
        yield CapsValue(
            capability=c,
            value=c.clean_value(cfg.default_value) if cfg.default_value else None,
            source=InputSource.CONFIG,
            config=cfg,
        )


def save_document_caps(
    self,
    caps: List[CapsValue],
    dry_run: bool = False,
    bulk=None,
    changed_fields: Optional[List[ChangeField]] = None,
):
    """"""
    from noc.inv.models.capsitem import CapsItem

    prev_labels, caps_labels, new_caps = set(), set(), []
    for c in self.iter_caps():
        if c.config.set_label:
            prev_labels |= set(c.get_labels()) | {c.config.set_label}

    for c in caps:
        new_caps.append(
            CapsItem(
                capability=c.capability, value=c.value, source=c.source.value, scope=c.scope or ""
            )
        )
        if c.config.set_label:
            caps_labels |= set(c.get_labels()) | {c.config.set_label}
    self.caps = new_caps
    if dry_run or self._created:
        return
    set_op = {"caps": self.caps}
    # Update database include effective labels directly
    # to avoid full save
    if hasattr(self, "effective_labels") and bool(caps_labels.symmetric_difference(prev_labels)):
        obj_labels = set(self.effective_labels)
        if obj_labels and prev_labels:
            obj_labels -= set(prev_labels)
        if caps_labels:
            obj_labels.update(caps_labels)
        changed_fields.append(ChangeField(field="effective_labels", new=sorted(obj_labels)))
        set_op["effective_labels"] = sorted(obj_labels)
    # Register changes
    change_tracker.register(
        "update",
        get_model_id(self),
        str(self.id),
        fields=changed_fields,
        audit=True,
        datastreams=get_datastreams(self),
        domains=get_domains(self, changed_fields),
        reactions_rules=get_applied_rules(self, "update", changed_fields=changed_fields),
        caps=[cf.field for cf in changed_fields or []],
    )
    self.update(**set_op)
    if hasattr(self, "on_save_caps"):
        self.on_save_caps(changed_fields, dry_run=dry_run)


def save_model_caps(
    self,
    caps: List[CapsValue],
    dry_run: bool = False,
    bulk=None,
    changed_fields: Optional[List[ChangeField]] = None,
):
    """"""
    prev_labels, caps_labels, new_caps = set(), set(), []
    for c in self.iter_caps():
        if c.config.set_label:
            prev_labels |= set(c.get_labels()) | {c.config.set_label}
    for c in caps:
        new_caps.append(
            {
                "capability": str(c.capability.id),
                "value": c.value,
                "source": c.source.value,
                "scope": c.scope or "",
            }
        )
        if c.config.set_label:
            caps_labels |= set(c.get_labels()) | {c.config.set_label}
    self.caps = new_caps
    if dry_run or not self.id:
        return
    set_op = {"caps": self.caps}
    # Update database include effective labels directly
    # to avoid full save
    if hasattr(self, "effective_labels") and bool(caps_labels.symmetric_difference(prev_labels)):
        obj_labels = set(self.effective_labels)
        if obj_labels and prev_labels:
            obj_labels -= set(prev_labels)
        if caps_labels:
            obj_labels.update(caps_labels)
        changed_fields.append(ChangeField(field="effective_labels", new=sorted(obj_labels)))
        set_op["effective_labels"] = sorted(obj_labels)
    # Register changes
    change_tracker.register(
        "update",
        get_model_id(self),
        str(self.id),
        fields=changed_fields,
        audit=True,
        datastreams=get_datastreams(self),
        domains=get_domains(self, changed_fields),
        reactions_rules=get_applied_rules(self, "update", changed_fields=changed_fields),
        caps=[cf.field for cf in changed_fields or []],
    )
    self.__class__.objects.filter(id=self.id).update(**set_op)
    self.update_init()
    self._reset_caches(self.id, credential=True)


def get_caps(self, scope: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a dict of effective object capabilities
    """

    caps = {}
    for c in self.iter_caps(scope=scope):
        if c.name in caps and c.scope:
            continue
        caps[c.name] = c.value
    return caps


def get_caps_config(self) -> Dict[str, CapsConfig]:
    """Return Dict with Local Capabilities Config"""
    if hasattr(self, "profile") and hasattr(self.profile, "get_caps_config"):
        return self.profile.get_caps_config()
    return {}


def set_caps(
    self, key: str, value: Any, source: str = "manual", scope: Optional[str] = None
) -> None:
    """
    Set capability or update
    Args:
        key: Capability name
        value: Capability value
        source: Source setting value
        scope: Capability value scope
    """
    from noc.inv.models.capability import Capability

    new_caps: List[CapsValue] = []
    caps = Capability.get_by_name(key)
    if not caps:
        return

    configs = self.get_caps_config()
    value = caps.clean_value(value)
    try:
        source = InputSource(source)
    except ValueError:
        source = InputSource.UNKNOWN
    scope = scope or None
    changed, is_new, changed_fields = False, True, []
    for item in self.iter_caps():
        if item.capability == caps:
            # Set found scope
            if is_new and item.scope == scope:
                # Add Manual Source
                is_new = False
            if item.scope == scope and item.value != value:
                new_caps.append(item.set_value(value))
                changed |= True
                caps_logger.info("Change capability value: %s -> %s", item, value)
                # Register changes
                changed_fields = [ChangeField(field=item.name, old=item.value, new=value)]
                continue
        new_caps += [item]
    if is_new:
        new_caps += [
            CapsValue(
                capability=caps,
                value=value,
                source=source,
                scope=scope or "",
                config=configs.get(str(caps.id), CapsConfig()),
            )
        ]
        changed |= True
        changed_fields = [ChangeField(field=caps.name, old=None, new=value)]
        caps_logger.info("Adding capability: %s", new_caps[-1])
    if changed:
        self.save_caps(new_caps, changed_fields=changed_fields)


def reset_caps(
    self,
    caps: Optional[str] = None,
    scope: Optional[str] = None,
    source: Optional[str] = None,
):
    """
    Remove caps from object
    Args:
        self: Object
        caps: Caps Name
        scope: Scope name
        source: Source set
    """
    new_caps, changed_fields = [], []
    if source:
        source = InputSource(source)
    changed = False
    for item in self.iter_caps():
        if scope and scope == item.scope:
            changed |= True
            caps_logger.info("Removing capability by scope: %s", scope)
            changed_fields += [ChangeField(field=item.name, old=str(item.value), new=None)]
            continue
        if caps and caps == item.name and (not source or source == item.source):
            changed |= True
            caps_logger.info("Removing capability by name: %s", caps)
            changed_fields += [ChangeField(field=item.name, old=str(item.value), new=None)]
            continue
        new_caps.append(item)
    if changed:
        self.save_caps(new_caps, changed_fields=changed_fields)


def update_caps(
    self,
    caps: Dict[str, Any],
    source: str,
    scope: Optional[str] = None,
    dry_run: bool = False,
    bulk=None,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """
    Update existing capabilities with a new ones.
    * if set scope - processed items over that scope
    * if not set scope - priority over if not set scope
    * For source in same scope - priority by default, Manual, Discovery
    Args:
        self:
        caps: dict of caps name -> caps value
        source: Source name
        scope: Scope name
        dry_run: Not save changes
        bulk: Changes aggregator
    """
    from noc.inv.models.capability import Capability

    o_label = f"{scope or ''}|{self}|{source}"
    try:
        source = InputSource(source)
    except ValueError:
        source = InputSource.UNKNOWN
    # Update existing capabilities
    logger = logger or caps_logger
    new_caps: List[CapsValue] = []
    seen = set()
    changed = False
    changed_fields = []
    for ci in self.iter_caps():
        if not scope or (scope and scope == ci.scope):
            seen.add(ci.name)
        if (scope and scope != ci.scope) or (not scope and ci.scope):
            # For Separate scope - skipping update (ETL)
            logger.debug(
                "[%s] Not changing capability %s: from other scope '%s'",
                o_label,
                ci.name,
                ci.scope or "",
            )
        elif ci.source == InputSource.MANUAL:
            # Manual Source set only for set_caps method
            logger.info(
                "[%s] Not changing capability %s: Already set with source '%s'",
                o_label,
                ci.name,
                ci.source,
            )
        elif ci.source == InputSource.DATABASE and not ci.scope:
            # Skip Database Caps without source, that set after separate discovery process
            # If not set scope - it clean.
            continue
        elif ci.name in caps:
            value = ci.capability.clean_value(caps[ci.name])
            if ci.value != value:
                logger.info(
                    "[%s] Changing capability %s: %s -> %s",
                    o_label,
                    ci.name,
                    ci.value,
                    value,
                )
                changed_fields.append(
                    ChangeField(
                        field=ci.name,
                        old=ci.value,
                        new=value,
                    )
                )
                ci = ci.set_value(value)
                changed |= True
            else:
                logger.debug(
                    "[%s] Caps value is same for '%s': Set with source '%s'",
                    o_label,
                    ci.name,
                    ci.source.name,
                )
        elif ci.name not in caps and source == ci.source:
            logger.info("[%s] Removing capability %s", o_label, ci)
            changed |= True
            changed_fields.append(
                ChangeField(
                    field=ci.name,
                    old=ci.value,
                    new=None,
                )
            )
            continue
        new_caps += [ci]
    # Add new capabilities
    for cn in set(caps) - seen:
        c = Capability.get_by_name(cn)
        if not c:
            logger.info("[%s] Unknown capability %s, ignoring", o_label, cn)
            continue
        value = c.clean_value(caps[cn])
        logger.info("[%s] Adding capability %s = %s", o_label, cn, value)
        new_caps.append(
            CapsValue(
                capability=c,
                value=value,
                source=source,
                scope=scope or "",
            )
        )
        changed |= True
        changed_fields.append(
            ChangeField(
                field=c.name,
                old=None,
                new=value,
            )
        )

    if changed or changed_fields:
        logger.info("[%s] Saving changes", o_label)
        self.save_caps(new_caps, dry_run=dry_run, changed_fields=changed_fields)
    # get_caps
    caps = {}
    for ci in new_caps:
        caps[ci.name] = ci.value
    return caps


def capabilities(cls):
    """
    @capabilities

    Methods contributed to class:
    * update_caps: Update object capabilities
    * set_caps: Set capabilities value
    * get_caps: Getting effective capabilities

    """

    cls.update_caps = update_caps
    cls.get_caps = get_caps
    cls.set_caps = set_caps
    cls.reset_caps = reset_caps

    if is_document(cls):
        # MongoEngine model
        cls.iter_caps = iter_document_caps
        if not hasattr(cls, "save_caps"):
            cls.save_caps = save_document_caps
        if not hasattr(cls, "get_caps_config"):
            cls.get_caps_config = get_caps_config

    else:
        # Django model
        cls.iter_caps = iter_model_caps
        if not hasattr(cls, "save_caps"):
            cls.save_caps = save_model_caps
        if not hasattr(cls, "get_caps_config"):
            cls.get_caps_config = get_caps_config

    return cls
