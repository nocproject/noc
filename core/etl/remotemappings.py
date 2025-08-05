# ----------------------------------------------------------------------
# @mappings decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Iterable

# Third-party modules
from jinja2 import Template

# NOC modules
from noc.models import is_document
from noc.core.models.inputsources import InputSource, SOURCE_PRIORITY

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RemoteMappingValue(object):
    remote_system: Any
    remote_id: Any
    sources: List[InputSource]
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

    def set_remote_id(self, remote_id: Any, source: Optional[InputSource] = None) -> "RemoteMappingValue":
        """Update value"""
        sources = self.sources
        if source not in self.sources:
            sources.append(source)
        return RemoteMappingValue(
            remote_system=self.remote_system,
            remote_id=remote_id,
            sources=sources,
        )

    def get_object_form(self, obj: Any) -> Dict[str, str]:
        """Render Mapping Form"""
        return {
            "remote_system": self.remote_system,
            "remote_system__label": self.remote_system.name,
            "remote_id": self.remote_id,
            "is_master": self.is_master,
            "url": self.render_url(obj),
        }


def iter_model_mappings(self) -> Iterable[RemoteMappingValue]:
    """Iterate mapping over Django Model"""
    from noc.main.models.remotesystem import RemoteSystem

    for m in self.mappings:
        rs = RemoteSystem.get_by_id(m["remote_system"])
        yield RemoteMappingValue(
            remote_system=rs,
            remote_id=m["remote_id"],
            sources=InputSource.from_sources(m.get("sources", "u")),
        )


def iter_document_mappings(self) -> Iterable[RemoteMappingValue]:
    """Iterate mapping over Django Model"""

    for m in self.mappings:
        yield RemoteMappingValue(
            remote_system=m.remote_system,
            remote_id=m.remote_id,
            sources=InputSource.from_sources(m.sources or "u"),
        )


def save_document_mappings(self, mappings: List[RemoteMappingValue], dry_run: bool = False):
    """"""
    from noc.main.models.remotemappingsitem import RemoteMappingItem

    self.mappings = [RemoteMappingItem(remote_system=m.remote_system, remote_id=m.remote_id, sources=InputSource.to_codes(m.sources)) for m in mappings]
    if dry_run:
        return
    self.update(mappings=self.mappings)


def save_model_mappings(self, mappings: List[RemoteMappingValue], dry_run: bool = False):
    """"""
    self.mappings = [{"remote_system": str(m.remote_system.id), "remote_id": m.remote_id, "sources": InputSource.to_codes(m.sources)} for m in mappings]
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
    source = InputSource(source or "o")
    new_mappings: List[RemoteMappingValue] = []
    changed, is_new = False, True

    for item in self.iter_remote_mappings():
        item: RemoteMappingValue
        if item.remote_system.id == remote_system.id and item.remote_id != remote_id:
            item.set_remote_id(remote_id, source)
            changed |= True
        elif item.remote_system.id == remote_system.id:
            item.set_remote_id(remote_id, source)
            is_new = False
        new_mappings.append(item)
    if is_new:
        new_mappings += [
            RemoteMappingValue(
                remote_system=remote_system,
                remote_id=remote_id,
                sources=[source],
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
    Attrs:
        mappings: Map remote_system -> remote_id
        source: Source Code
          * m - manual
          * e - elt
          * o - other
    """
    source = source or "u"
    priority = "uem"
    new_mappings = []
    changed = False
    seen = set()
    for item in self.iter_remote_mappings():
        item: RemoteMappingValue
        rs = m.remote_system
        sources = set(m.sources or "o")
        max_p = max(priority.index(x) for x in source)
        if rs not in mappings and source in sources:
            # Remove Source
            sources.remove(source)
        elif rs not in mappings:
            # Set on different source
            pass
        elif mappings[rs] != m.remote_id and priority.index(source) >= max_p:
            # Change ID
            logger.info(
                "[%s] Mapping over priority and will be replace: %s -> %s",
                rs,
                m.remote_id,
                mappings[rs],
            )
            # replace, skip
            m.remote_id = mappings[rs]
            sources.add(source)
            changed |= True
        elif mappings[rs] != m.remote_id:
            pass
        elif source not in sources:
            changed |= True
            sources.add(source)
        if not sources:
            changed |= True
            continue
        elif sources != set(m.sources or "o"):
            m.sources = "".join(sorted(sources))
            changed |= True
        new_mappings.append(m)
        seen.add(rs)
    for rs in set(mappings) - seen:
        new_mappings.append(RemoteMappingItem(remote_system=rs, remote_id=mappings[rs], sources=source))
        changed |= True
    if changed:
        self.mappings = new_mappings
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
