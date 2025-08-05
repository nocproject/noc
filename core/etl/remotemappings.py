# ----------------------------------------------------------------------
# @mappings decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Iterable, FrozenSet

# Third-party modules
from jinja2 import Template

# NOC modules
from noc.models import is_document
from noc.core.models.inputsources import InputSource

logger = logging.getLogger(__name__)
DEFAULT_SOURCE = InputSource.UNKNOWN.value
DEFAULT_PRIORITY = "uem"


@dataclass(frozen=True)
class RemoteMappingValue(object):
    remote_system: Any
    remote_id: Any
    sources: FrozenSet[InputSource]
    is_master: bool = False

    def __str__(self):
        return f"{self.remote_system.name}@{self.remote_id} ({self.sources})"

    @property
    def name(self) -> str:
        return self.remote_system.name

    @property
    def rs(self) -> Any:
        """short alias for remote_system"""
        return self.remote_system

    @property
    def source_weight(self) -> int:
        """Calculate source weight"""
        return max(x.get_priority_weight(DEFAULT_PRIORITY) for x in self.sources)

    def render_url(self, obj: Any) -> str:
        """"""
        if not self.remote_system.object_url_template:
            return ""
        tpl = Template(self.remote_system.object_url_template)
        url = tpl.render(
            {
                "remote_system": self.remote_system,
                "remote_id": self.remote_id,
                "object": obj,
                "config": self.remote_system.config,
            },
        )
        return url

    def set_remote_id(
        self, remote_id: Any, source: Optional[InputSource] = None
    ) -> "RemoteMappingValue":
        """Update value"""
        sources = self.sources
        if source and source not in self.sources:
            sources = frozenset([source] + list(self.sources))
        return RemoteMappingValue(
            remote_system=self.remote_system,
            remote_id=remote_id,
            sources=sources,
        )

    def update_sources(self, sources: Iterable[InputSource]):
        """"""
        return RemoteMappingValue(
            remote_system=self.remote_system,
            remote_id=self.remote_id,
            sources=frozenset(sources),
        )

    def get_object_form(self, obj: Any) -> Dict[str, str]:
        """Render Mapping Form"""
        return {
            "remote_system": str(self.remote_system.id),
            "remote_system__label": self.remote_system.name,
            "remote_id": self.remote_id,
            "is_master": self.is_master,
            "url": self.render_url(obj),
        }


def iter_model_mappings(self) -> Iterable[RemoteMappingValue]:
    """Iterate mapping over Django Model"""
    from noc.main.models.remotesystem import RemoteSystem

    remote_system = getattr(self, "remote_system", None)
    for m in self.mappings:
        rs = RemoteSystem.get_by_id(m["remote_system"])
        sources = frozenset(InputSource.from_sources(m.get("sources", "u")))
        if remote_system and rs == remote_system:
            yield RemoteMappingValue(
                remote_system=rs,
                remote_id=m["remote_id"],
                sources=frozenset([InputSource.ETL]) | sources,
                is_master=True,
            )
            remote_system = None
            continue
        yield RemoteMappingValue(
            remote_system=rs,
            remote_id=m["remote_id"],
            sources=sources,
        )
    if remote_system:
        yield RemoteMappingValue(
            remote_system=remote_system,
            remote_id=self.remote_id,
            sources=frozenset([InputSource.ETL]),
            is_master=True,
        )


def iter_document_mappings(self) -> Iterable[RemoteMappingValue]:
    """Iterate mapping over Django Model"""
    remote_system = getattr(self, "remote_system", None)
    for m in self.mappings:
        sources = frozenset(InputSource.from_sources(m.sources or "u"))
        if remote_system and m.remote_system == remote_system:
            # Master system
            yield RemoteMappingValue(
                remote_system=self.remote_system,
                remote_id=self.remote_id,
                sources=frozenset([InputSource.ETL]) | sources,
                is_master=True,
            )
            remote_system = None
            continue
        yield RemoteMappingValue(
            remote_system=m.remote_system,
            remote_id=m.remote_id,
            sources=sources,
        )
    if remote_system:
        yield RemoteMappingValue(
            remote_system=remote_system,
            remote_id=self.remote_id,
            sources=frozenset([InputSource.ETL]),
            is_master=True,
        )


def save_document_mappings(self, mappings: List[RemoteMappingValue], dry_run: bool = False):
    """"""
    from noc.main.models.remotemappingsitem import RemoteMappingItem

    self.mappings = [
        RemoteMappingItem(
            remote_system=m.remote_system,
            remote_id=m.remote_id,
            sources=InputSource.to_codes(m.sources),
        )
        for m in mappings
    ]
    if dry_run:
        return
    self.update(mappings=self.mappings)


def save_model_mappings(self, mappings: List[RemoteMappingValue], dry_run: bool = False):
    """"""
    self.mappings = [
        {
            "remote_system": str(m.remote_system.id),
            "remote_id": m.remote_id,
            "sources": InputSource.to_codes(m.sources),
        }
        for m in mappings
    ]
    if dry_run:
        return
    self.objects.filter(id=self.id).update(mappings=self.mappings)
    self.update_init()
    self._reset_caches(self.id, credential=True)


def set_mapping(self, remote_system: Any, remote_id: str, source: Optional[str] = None):
    """
    Set Object mapping
    Args:
        remote_system: Remote System Instance
        remote_id: Id on Remote system
        source:
    """
    source = InputSource(source or "unknown")
    weight = source.get_priority_weight(DEFAULT_PRIORITY)
    new_mappings: List[RemoteMappingValue] = []
    changed, is_new = False, True

    for item in self.iter_remote_mappings():
        # Priority ?
        if (
            item.remote_system.id == remote_system.id
            and item.remote_id != remote_id
            and weight >= item.source_weight
        ):
            item = item.set_remote_id(remote_id, source)
            logger.info("[%s] Set mapping: %s", self, item)
            changed |= True
        elif item.remote_system.id == remote_system.id:
            if source not in item.sources:
                item = item.set_remote_id(remote_id, source)
                logger.info("[%s] Update mapping: %s", self, item)
                changed |= True
            is_new = False
        new_mappings.append(item)
    if is_new:
        new_mappings += [
            RemoteMappingValue(
                remote_system=remote_system,
                remote_id=remote_id,
                sources=frozenset([source]),
            )
        ]
        changed |= True
        logger.info("Adding mapping: %s", new_mappings[-1])
    if changed:
        self.save_remote_mappings(new_mappings)


def get_mapping(self, remote_system: Any) -> Optional[str]:
    """return object mapping for remote_system"""
    for m in self.iter_remote_mappings():
        if m.remote_system.id == remote_system.id:
            return m.remote_id
    return None


def get_mappings(self) -> Dict[str, str]:
    """return object mappings dict"""
    r = {}
    for m in self.iter_remote_mappings():
        r[m.remote_system.name] = m.remote_id
    return r


def update_remote_mappings(self, mappings: Dict[Any, str], source: Optional[str] = None) -> bool:
    """
    Update managed Object mappings
    Source Priority, for mappings on different sources
    If sources is empty - remove mapping
    Attrs:
        mappings: Map remote_system -> remote_id
        source: Source Code
          * m - manual
          * e - elt
          * u - unknown
    """
    source = InputSource(source or DEFAULT_SOURCE)
    weight = source.get_priority_weight(DEFAULT_PRIORITY)
    new_mappings = []
    changed = False
    seen = set()
    for item in self.iter_remote_mappings():
        item: RemoteMappingValue
        rs = item.remote_system
        sources = set(item.sources)
        if rs not in mappings and source in sources:
            # Remove Source
            sources.remove(source)
        elif rs not in mappings:
            # Set on different source
            pass
        elif mappings[rs] != item.remote_id and weight >= item.source_weight:
            # Change ID
            logger.info(
                "[%s] Mapping over priority and will be replace: %s -> %s",
                rs,
                item.remote_id,
                mappings[rs],
            )
            # replace, skip
            item = item.set_remote_id(mappings[rs], source=source)
            sources.add(source)
            changed |= True
        elif mappings[rs] != item.remote_id:
            pass
        elif source not in sources:
            changed |= True
            sources.add(source)
        if not sources:
            # If empty sources - remove mapping
            changed |= True
            continue
        elif sources != item.sources:
            item = item.update_sources(sources)
            logger.info("[%s] Update sources: %s", self, sources)
            changed |= True
        new_mappings.append(item)
        seen.add(rs)
    for rs in set(mappings) - seen:
        new_mappings.append(
            RemoteMappingValue(
                remote_system=rs, remote_id=mappings[rs], sources=frozenset([source])
            )
        )
        changed |= True
    if changed:
        logger.info("[%s] Saving mappings", self)
        self.save_remote_mappings(new_mappings)
    return changed


def mappings(cls):
    """
    @mappings

    Methods contributed to class:
    * update_mappings: Update object remote mappings
    * set_mappings: Set mappings value
    * get_mappings: Getting effective mappings

    """

    cls.update_remote_mappings = update_remote_mappings
    cls.get_mappings = get_mappings
    cls.set_mapping = set_mapping
    # cls.reset_mappings = mappings

    if is_document(cls):
        # MongoEngine model
        cls.iter_remote_mappings = iter_document_mappings
        if not hasattr(cls, "save_remote_mappings"):
            cls.save_remote_mappings = save_document_mappings

    else:
        # Django model
        cls.iter_remote_mappings = iter_model_mappings
        if not hasattr(cls, "save_remote_mappings"):
            cls.save_remote_mappings = save_model_mappings

    return cls
