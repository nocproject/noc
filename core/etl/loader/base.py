# ----------------------------------------------------------------------
# Data Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import os
import logging
import re
import csv
import time
import shutil
import functools
from collections import defaultdict
from io import StringIO, TextIOWrapper
from typing import Any, Optional, Iterable, Tuple, List, Dict, Set, Union

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.fileutils import safe_rewrite
from noc.config import config
from noc.core.comp import smart_text
from noc.core.debug import error_report
from noc.core.etl.compression import compressor
from noc.core.etl.models.typing import MappingItem
from noc.models import get_model_id, LABEL_MODELS
from ..models.base import BaseModel

logger = logging.getLogger(__name__)


class BaseLoader(object):
    """
    Import directory structure:
    var/
        import/
            <system name>/
                <loader name>/
                    import.jsonl[.ext]  -- state to load, must have .ext extension
                                         according to selected compressor
                    mappings.csv -- ID mappings
                    archive/
                        import-YYYY-MM-DD-HH-MM-SS.jsonl.ext -- imported state

    Import file format: CSV, unix end of lines, UTF-8, comma-separated
    First column - record id in the terms of connected system,
    other columns must be defined in *fields* variable.

    File must be sorted by first field either as string or as numbers,
    sort order must not be changed.

    mappings.csv - CSV, unix end of lines, UTF-8 comma separated
    mappings of ID between NOC and remote system. Populated by loader
    automatically.

    :param fields: List of either field names or tuple of
        (field name, related loader name)
    """

    # Loader name
    name: str
    # Loader model (Database)
    model = None
    # Data model
    data_model: BaseModel

    # List of tags to add to the created records
    tags = []

    # Register model as Mapping Scope
    model_mappings: Dict[str, str] = {}  # scope -> Model

    rx_archive = re.compile(
        r"^import-\d{4}(?:-\d{2}){5}.jsonl%s$" % compressor.ext.replace(".", r"\.")
    )

    # Discard records which cannot be dereferenced
    discard_deferred = False
    # Ignore auto-generated unique fields
    ignore_unique = {"bi_id"}
    unique_index: Tuple[str, ...] = None
    # Array fields need merge values
    incremental_change = {"labels", "static_client_groups", "static_service_groups"}
    # Workflow fields
    workflow_state_sync = False
    workflow_fields: Set[str] = {"state", "state_changed", "event"}
    workflow_event_model = False
    workflow_add_event = "seen"
    workflow_delete_event = "missed"
    # Label
    label_enable_setting: Optional[str] = None
    # Incremental
    checkpoint_field = "checkpoint"
    # Post save fields (example - capabilities)
    post_save_fields: Optional[Set[str]] = None

    REPORT_INTERVAL = 1000

    class Deferred(Exception):
        pass

    def __init__(self, chain):
        self.chain = chain
        self.system = chain.system
        self.logger = PrefixLoggerAdapter(logger, "%s][%s" % (self.system.name, self.name))
        self.disable_mappings = False
        self.import_dir = os.path.join(config.path.etl_import, self.system.name, self.name)
        self.archive_dir = os.path.join(self.import_dir, "archive")
        self.mappings_path = os.path.join(self.import_dir, "mappings.csv")
        self.mappings: Dict[str, str] = {}
        self.remote_mappings: Dict[Tuple[str, str], Dict[str, str]] = {}
        self.wf_state_mappings = {}
        self.ensured_labels = set()
        self.new_state_path = None
        self.c_add = 0
        self.c_change = 0
        self.c_delete = 0
        # Mapped fields
        self.mapped_fields: Dict[str, str] = (
            self.data_model.get_mapped_fields()
        )  # field_name -> loader_name
        # Build clean map
        self.clean_map = {}  # field name -> clean function
        self.pending_deletes: List[Tuple[str, BaseModel]] = []  # (id, BaseModel)
        self.referred_errors: List[Tuple[str, BaseModel]] = []  # (id, BaseModel)
        if not self.model:
            return
        if self.is_document:
            import mongoengine.errors

            unique_fields = [
                f.name
                for f in self.model._fields.values()
                if f.unique and f.name not in self.ignore_unique
            ]
            self.integrity_exception = mongoengine.errors.NotUniqueError
        else:
            # Third-party modules
            import django.db.utils

            unique_fields = [
                f.name
                for f in self.model._meta.fields
                if f.unique
                and f.name != self.model._meta.pk.name
                and f.name not in self.ignore_unique
            ]
            self.integrity_exception = django.db.utils.IntegrityError
        if unique_fields:
            self.unique_field = unique_fields[0]
        else:
            self.unique_field = None
        self.has_remote_system: bool = hasattr(self.model, "remote_system")
        if self.workflow_state_sync:
            self.load_wf_state_mappings()
        if self.enable_labels:
            self.load_ensured_labels()

    @property
    def is_document(self):
        """
        Returns True if model is Document, False - if Model
        """
        return hasattr(self.model, "_fields")

    def load_mappings(self):
        """
        Load mappings file
        """
        if self.model:
            if self.is_document:
                self.update_document_clean_map()
            else:
                self.update_model_clean_map()
        if not os.path.exists(self.mappings_path):
            return
        self.logger.info("Loading mappings from %s", self.mappings_path)
        with open(self.mappings_path) as f:
            reader = csv.reader(f)
            for k, v in reader:
                self.mappings[self.clean_str(k)] = v
        self.logger.info("%d mappings restored", len(self.mappings))

    def load_wf_state_mappings(self):
        from noc.wf.models.state import State

        self.logger.info("Loading Workflow states")
        for ws in State.objects.filter():
            self.wf_state_mappings[(str(ws.workflow.id), ws.name)] = ws

    def load_ensured_labels(self):
        from noc.main.models.label import Label

        self.logger.info("Loading Labels: %s", self.enable_labels)
        for ll in Label.objects.filter(allow_models__in=[get_model_id(self.model)]):
            if ll.is_wildcard or ll.is_matched:
                continue
            self.ensured_labels.add(ll.name)

    @classmethod
    def get_remote_mappings(cls, remote_system: str, name: str) -> Dict[str, str]:
        """
        Return mappings from another remote_system

        Args:
            remote_system: Remote System name
            name: Loader name
        """
        from noc.main.models.remotesystem import RemoteSystem

        rs = RemoteSystem.get_by_name(remote_system)
        if not rs:
            raise ValueError("Unknown Remote System: %s" % remote_system)
        ch = rs.get_loader_chain()
        loader = ch.get_loader(name)
        if not loader.mappings:
            loader.load_mappings()
        return loader.mappings

    @classmethod
    def get_mapping(cls, scope: str, value: Optional[str]) -> Optional[Any]:
        """
        Resolve mapping by NOC Mapping

        Args:
            scope: Mapping name
            value: Resolve value
        """
        if scope not in cls.model_mappings:
            raise ValueError("Unknown Scope: %s" % scope)
        model = cls.model_mappings[scope]
        if hasattr(model, "get_by_name"):
            o = model.get_by_name(value)
        else:
            o = model.objects.filter(name=value).first()
        return o

    def get_new_state(self) -> Optional[TextIOWrapper]:
        """
        Returns file object of new state, or None when not present
        """
        # Try import.csv
        path = compressor.get_path(os.path.join(self.import_dir, "import.jsonl"))
        if not os.path.isfile(path):
            return None
        logger.info("Loading from %s", path)
        self.new_state_path = path
        return compressor(path, "r").open()

    def get_current_state(self) -> TextIOWrapper:
        """
        Returns file object of current state
        """
        self.load_mappings()
        if not os.path.isdir(self.archive_dir):
            self.logger.info("Creating archive directory: %s", self.archive_dir)
            try:
                os.mkdir(self.archive_dir)
            except OSError as e:
                self.logger.error("Failed to create directory: %s (%s)", self.archive_dir, e)
                # @todo: Die
        if os.path.isdir(self.archive_dir):
            fn = list(sorted(f for f in os.listdir(self.archive_dir) if self.rx_archive.match(f)))
        else:
            fn = []
        if not fn:
            return StringIO("")
        path = os.path.join(self.archive_dir, fn[-1])
        logger.info("Current state from %s", path)
        return compressor(path, "r").open()

    def iter_jsonl(
        self, f: TextIOWrapper, data_model: Optional[BaseModel] = None
    ) -> Iterable[BaseModel]:
        """
        Iterate over JSONl stream and yield model instances

        Args:
            f:
            data_model:
        """
        dm = data_model or self.data_model
        for line in f:
            yield dm.model_validate_json(line)

    def diff(
        self,
        old: Iterable[BaseModel],
        new: Iterable[BaseModel],
        include_fields: Set = None,
        return_wo_changes: bool = False,
    ) -> Iterable[Tuple[Optional[BaseModel], Optional[BaseModel]]]:
        """
        Compare old and new CSV files and yield pair of matches
        * old, new -- when changed
        * old, None -- when removed
        * None, new -- when added
        """

        o = next(old, None)
        n = next(new, None)
        while o or n:
            if not o:
                # New
                yield None, n
                n = next(new, None)
            elif not n:
                # Removed
                yield o, None
                o = next(old, None)
            else:
                if n.id == o.id:
                    # Changed
                    if n.dict(include=include_fields, exclude={self.checkpoint_field}) != o.dict(
                        include=include_fields, exclude={self.checkpoint_field}
                    ):
                        yield o, n
                    elif return_wo_changes:
                        yield o, n
                    n = next(new, None)
                    o = next(old, None)
                elif n.id < o.id:
                    # Added
                    yield None, n
                    n = next(new, None)
                else:
                    # Removed
                    yield o, None
                    o = next(old, None)

    def load(self, return_wo_changes: bool = False):
        """
        Import new data
        """
        self.logger.info("Importing")
        ns = self.get_new_state()
        if not ns:
            self.logger.info("No new state, skipping")
            self.load_mappings()
            return
        current_state = self.iter_jsonl(self.get_current_state())
        new_state = self.iter_jsonl(ns)
        deferred_add = []
        deferred_change = []
        for o, n in self.diff(current_state, new_state, return_wo_changes=return_wo_changes):
            if o is None and n:
                try:
                    self.on_add(n)
                except self.Deferred:
                    if not self.discard_deferred:
                        deferred_add += [n]
            elif o and n is None:
                self.on_delete(o)
            else:
                try:
                    self.on_change(o, n)
                except self.Deferred:
                    if not self.discard_deferred:
                        deferred_change += [(o, n)]
            rn = self.c_add + self.c_change + self.c_delete
            if rn > 0 and rn % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", rn)
        # Add deferred records
        while len(deferred_add):
            nd = []
            for row in deferred_add:
                try:
                    self.on_add(row)
                except self.Deferred:
                    nd += [row]
            if len(nd) == len(deferred_add):
                raise Exception("Unable to defer references")
            deferred_add = nd
            rn = self.c_add + self.c_change + self.c_delete
            if rn % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", rn)
        # Change deferred records
        while len(deferred_change):
            nd = []
            for o, n in deferred_change:
                try:
                    self.on_change(o, n)
                except self.Deferred:
                    nd += [(o, n)]
            if len(nd) == len(deferred_change):
                raise Exception("Unable to defer references")
            deferred_change = nd
            rn = self.c_add + self.c_change + self.c_delete
            if rn % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", rn)

    def find_object(self, v: Dict[str, Any]) -> Optional[Any]:
        """
        Find object by remote system/remote id
        :param v:
        :return:
        """
        self.logger.debug("Find object: %s", v)
        if not self.has_remote_system:
            return None
        if not v.get("remote_system") or not v.get("remote_id"):
            self.logger.warning("RS or RID not found")
            return None
        find_query = {"remote_system": v.get("remote_system"), "remote_id": v.get("remote_id")}
        try:
            return self.model.objects.get(**find_query)
        except self.model.MultipleObjectsReturned:
            if self.unique_field or self.unique_index:
                if self.unique_field:
                    find_query[self.unique_field] = v.get(self.unique_field)
                else:
                    for i in self.unique_index:
                        find_query[i] = v.get(i)
                r = self.model.objects.filter(**find_query)
                if not r:
                    r = self.model.objects.filter(
                        **{"remote_system": v.get("remote_system"), "remote_id": v.get("remote_id")}
                    )
                return list(r)[-1]
            raise self.model.MultipleObjectsReturned
        except self.model.DoesNotExist:
            self.logger.debug("Object not found")
            return None

    def create_object(
        self,
        v,
        state: Optional[str] = None,
        mappings: Optional[Dict[Any, str]] = None,
    ):
        """
        Create object with attributes. Override to save complex
        data structures
        """
        self.logger.debug("Create object")
        if self.enable_labels and "labels" in v:
            self.ensure_labels(v["labels"])
        o = self.model(**v)
        if not self.workflow_state_sync or not state:
            pass
        elif hasattr(o, "object_profile"):
            o.state = self.clean_wf_state(o.object_profile.workflow, state)
        else:
            o.state = self.clean_wf_state(o.profile.workflow, state)
        if mappings is not None:
            o.update_remote_mappings(mappings, source="e")
        try:
            o.save()
        except self.integrity_exception as e:
            self.logger.warning("Integrity error: %s", e)
            assert self.unique_field or self.unique_index
            if not self.is_document:
                from django.db import connection

                connection._rollback()
            # Fallback to change object
            if self.unique_field:
                q = {self.unique_field: v[self.unique_field]}
            else:
                q = {i: getattr(o, i) for i in self.unique_index}
            o = self.model.objects.get(**q)
            for k, nv in v.items():
                setattr(o, k, nv)
            o.save()
        except Exception as e:
            error_report()
            raise e
        return o

    def change_object(
        self,
        object_id: str,
        v: Dict[str, Any],
        inc_changes: Dict[str, Dict[str, List]] = None,
        state: Optional[str] = None,
        state_changed: Optional[datetime.datetime] = None,
        mappings: Optional[Dict[Any, str]] = None,
    ):
        """
        Change object with attributes
        """
        self.logger.debug("Changed object: %s", v)
        # See: https://code.getnoc.com/noc/noc/merge_requests/49
        try:
            o = self.model.objects.get(pk=object_id)
        except self.model.DoesNotExist:
            self.logger.error("Cannot change %s:%s: Does not exists", self.name, object_id)
            return None
        for k, nv in v.items():
            if k == self.checkpoint_field:
                continue
            if self.enable_labels and k == "labels":
                self.ensure_labels(nv)
            if inc_changes and k in inc_changes:
                ov = getattr(o, k, [])
                nv = list(set(ov).union(set(inc_changes[k]["add"])) - set(inc_changes[k]["remove"]))
            setattr(o, k, nv)
        if self.workflow_state_sync and state:
            self.change_workflow(o, state, state_changed)
        if mappings is not None:
            o.update_remote_mappings(mappings, source="e")
        try:
            o.save()
        except self.integrity_exception as e:
            self.logger.warning("Integrity error: %s", e)
            assert self.unique_field or self.unique_index
            if not self.is_document:
                from django.db import connection

                connection._rollback()
            # Fallback to change object
            if self.unique_field:
                q = {self.unique_field: v[self.unique_field]}
            else:
                q = {i: getattr(o, i) for i in self.unique_index}
            o = self.model.objects.get(**q)
            for k, nv in v.items():
                setattr(o, k, nv)
            o.save()
        except Exception as e:
            error_report()
            raise e
        return o

    @property
    def enable_labels(self) -> bool:
        if not self.model:
            return False
        return get_model_id(self.model) in LABEL_MODELS

    def on_add(self, item: BaseModel) -> None:
        """
        Create new record
        """
        self.logger.debug("Add: %s", item.model_dump())
        v = self.clean(item)
        if "id" in v:
            del v["id"]
        if self.checkpoint_field in v:
            del v[self.checkpoint_field]
        for fn in set(v).intersection(self.workflow_fields):
            del v[fn]
        # Post save update fields (example capabilities)
        psf: Dict[str, Any] = {}
        if self.post_save_fields:
            for fn in self.post_save_fields:
                psf[fn] = v.pop(fn)
        mappings = v.pop("mappings", None)
        o = self.find_object(v)
        if o:
            self.c_change += 1
            # Lost&found object with same remote_id
            self.logger.debug("Lost and Found object")
            vv = {"remote_system": v["remote_system"], "remote_id": v["remote_id"]}
            for fn, nv in v.items():
                if fn in vv:
                    continue
                if getattr(o, fn) != nv:
                    vv[fn] = nv
            o = self.change_object(
                o.id,
                vv,
                state=getattr(item, "state", None),
                state_changed=getattr(item, "state_changed", None),
                mappings=mappings,
            )
        else:
            self.c_add += 1
            o = self.create_object(v, state=getattr(item, "state", None), mappings=mappings)
            if self.workflow_event_model:
                o.fire_event(self.workflow_add_event)
        if o and psf:
            self.post_save(o, psf)
        self.set_mappings(item.id, o.id)

    def on_change(self, o: BaseModel, n: BaseModel):
        """
        Create change record
        """
        self.logger.debug("Change: %s", n.model_dump())
        self.c_change += 1
        nv = self.clean(n)
        changes = {"remote_system": nv["remote_system"], "remote_id": nv["remote_id"]}
        incremental_changes = {}
        ov = self.clean(o)
        # Post save update fields (example capabilities)
        psf: Dict[str, Any] = {}
        mappings = None
        for fn in self.data_model.model_fields:
            if fn == "id" or fn in self.workflow_fields:
                continue
            elif fn == "mappings":
                mappings = nv.pop("mappings")
                if not mappings and o.mappings:
                    mappings = {}
                continue
            if self.post_save_fields and fn in self.post_save_fields:
                psf[fn] = nv.pop(fn)
                continue
            if ov[fn] != nv[fn]:
                self.logger.debug("   %s: %s -> %s", fn, ov[fn], nv[fn])
                changes[fn] = nv[fn]
                if fn in self.incremental_change:
                    incremental_changes[fn] = {
                        "add": list(set(nv[fn] or []) - set(ov[fn] or [])),
                        "remove": list(set(ov[fn] or []) - set(nv[fn] or [])),
                    }
        if n.id not in self.mappings:
            self.logger.error("Cannot map id '%s'. Skipping.", n.id)
            return
        o = self.change_object(
            self.mappings[n.id],
            changes,
            inc_changes=incremental_changes,
            state=getattr(n, "state", None),
            state_changed=getattr(n, "state_changed", None),
            mappings=mappings,
        )
        if o and psf:
            self.post_save(o, psf)

    def on_delete(self, item: BaseModel):
        """
        Delete record
        """
        self.pending_deletes += [(item.id, item)]

    def change_workflow(self, o, state: str, changed_date: Optional[datetime.datetime] = None):
        self.logger.debug("Change Workflow state: %s -> %s", o.state, state)
        if not o:
            return
        if hasattr(o, "object_profile"):
            state = self.clean_wf_state(o.object_profile.workflow, state)
        else:
            state = self.clean_wf_state(o.profile.workflow, state)
        if state and o.state != state:
            self.logger.debug("Change workflow state: %s -> %s", o.state, state)
            o.set_state(state, changed_date)

    def ensure_labels(self, labels: Optional[List[str]]):
        from noc.main.models.label import Label

        if not labels:
            return
        for ll in set(labels or []) - self.ensured_labels:
            Label.ensure_label(ll, [get_model_id(self.model)])

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Delete: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                if self.workflow_event_model:
                    obj.fire_event(self.workflow_delete_event)
                else:
                    obj.delete()
            except ValueError as e:  # Referred Error
                self.logger.error("%s", str(e))
                self.referred_errors += [(r_id, msg)]
            except KeyError as e:
                # Undefined mappings
                self.logger.error("%s", str(e))
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []

    def save_state(self):
        """
        Save current state
        """
        if not self.new_state_path:
            return
        self.logger.info(
            "Summary: %d new, %d changed, %d removed", self.c_add, self.c_change, self.c_delete
        )
        self.logger.info(
            "Error delete by referred: %s", "\n".join(b.json() for _, b in self.referred_errors)
        )
        t = time.localtime()
        archive_path = os.path.join(
            self.archive_dir,
            compressor.get_path("import-%04d-%02d-%02d-%02d-%02d-%02d.jsonl" % tuple(t[:6])),
        )
        self.logger.info("Moving %s to %s", self.new_state_path, archive_path)
        if self.new_state_path.endswith(compressor.ext):
            # Simply move the file
            shutil.move(self.new_state_path, archive_path)
        else:
            # Compress the file
            self.logger.info("Compressing")
            with open(self.new_state_path, "r") as s, compressor(archive_path, "w") as d:
                d.write(s.read())
            os.unlink(self.new_state_path)
        self.logger.info("Saving mappings to %s", self.mappings_path)
        mdata = "\n".join(f"{k},{self.mappings[k]}" for k in sorted(self.mappings))
        safe_rewrite(self.mappings_path, mdata)

    def post_save(self, o, fields: Dict[str, Any]):
        """
        Method fields updated separate method (example - capabilities)
        :param o:
        :param fields:
        :return:
        """
        return

    def clean(self, item: BaseModel) -> Dict[str, Any]:
        """
        Cleanup row and return a dict of field name -> value
        """
        r = {k: self.clean_map.get(k, self.clean_any)(v) for k, v in item.model_dump().items()}
        # Fill integration fields
        r["remote_system"] = self.system.remote_system
        r["remote_id"] = self.clean_str(item.id)
        # Fill mapping
        if "mappings" in r and r["mappings"]:
            r["mappings"] = self.clean_object_mappings(item.mappings)
        return r

    @classmethod
    def clean_object_mappings(cls, value: List[MappingItem]) -> Optional[Dict[Any, str]]:
        from noc.main.models.remotesystem import RemoteSystem

        r = {}
        for m in value:
            rs = RemoteSystem.get_by_name(m.remote_system)
            if not rs:
                continue
            r[rs] = m.remote_id
        return r

    @classmethod
    def clean_ed_list(cls, model, value: List[Dict[str, Any]]):
        if not value:
            return None
        return [model(**v) for v in value]

    @classmethod
    def clean_any(cls, value: Any) -> Any:
        return value

    @classmethod
    def clean_str(cls, value) -> Optional[str]:
        if value:
            if isinstance(value, str):
                return smart_text(value)
            elif not isinstance(value, str):
                return str(value)
            else:
                return value
        else:
            return None

    def clean_map_str(self, mappings: Dict[str, str], loader_name, value):
        value = self.clean_str(value)
        if self.disable_mappings and not mappings:
            return value
        elif value and isinstance(value, dict) and "remote_system" in value:
            return self.clean_remote_reference(value["remote_system"], loader_name, value["id"])
        elif isinstance(value, dict) and "scope" in value:
            return self.get_mapping(value["scope"], value["value"])
        elif value:
            try:
                value = mappings[value]
            except KeyError:
                self.logger.warning("Deferred. Unknown map value: %s", value)
                raise self.Deferred
        return value

    @classmethod
    def clean_bool(cls, value: str) -> Optional[bool]:
        if value == "" or value is None:
            return None
        try:
            return int(value) != 0
        except ValueError:
            pass
        value = value.lower()
        return value in ("t", "true", "y", "yes")

    def clean_remote_reference(self, remote_system, loader_name, value) -> Optional[str]:
        """
        Resolve value on Remote System Mapping

        Args:
            remote_system: Remote System Name
            loader_name: Mapping loader name
            value: Value for resolved
        """
        if (remote_system, loader_name) not in self.remote_mappings:
            self.remote_mappings[(remote_system, loader_name)] = self.get_remote_mappings(
                remote_system,
                loader_name,
            )
        return self.remote_mappings[(remote_system, loader_name)][value]

    def clean_reference(
        self, mappings: Dict[str, str], r_model, loader_name: str, value: Union[str, Dict[str, str]]
    ) -> Optional[str]:
        if not value:
            return None
        elif self.disable_mappings and not mappings:
            return value
        elif isinstance(value, dict) and "remote_system" in value:
            value = self.clean_remote_reference(value["remote_system"], loader_name, value["id"])
            return self.chain.cache[r_model, value]
        elif isinstance(value, dict) and "scope" in value:
            return self.get_mapping(value["scope"], value["value"])
        else:
            # @todo: Get proper mappings
            try:
                value = mappings[value]
            except KeyError:
                self.logger.info("Deferred. Unknown value %s:%s", r_model, value)
                raise self.Deferred()
            return self.chain.cache[r_model, value]

    def clean_int_reference(
        self, mappings: Dict[str, str], r_model, loader_name: str, value: str
    ) -> Optional[int]:
        if not value:
            return None
        elif self.disable_mappings and not mappings:
            return value
        elif isinstance(value, dict) and "remote_system" in value:
            value = self.clean_remote_reference(value["remote_system"], loader_name, value["id"])
            return self.chain.cache[r_model, int(value)]
        elif isinstance(value, dict) and "scope" in value:
            return self.get_mapping(value["scope"], value["value"])
        else:
            # @todo: Get proper mappings
            try:
                value = int(mappings[value])
            except KeyError:
                self.logger.info("Deferred. Unknown value %s:%s", r_model, value)
                raise self.Deferred()
            return self.chain.cache[r_model, value]

    def clean_wf_state(self, workflow, state: str):
        if not state:
            return None
        try:
            return self.wf_state_mappings[(str(workflow.id), state)]
        except KeyError:
            self.logger.error("Unknown Workflow state value %s:%s", workflow, state)
            raise ValueError(f"Unknown Workflow state value {workflow}:{state}", workflow, state)

    def set_mappings(self, rv, lv):
        self.logger.debug("Set mapping remote: %s, local: %s", rv, lv)
        self.mappings[str(rv)] = str(lv)

    def update_document_clean_map(self):
        from mongoengine.fields import BooleanField, ReferenceField, EmbeddedDocumentListField
        from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField

        self.logger.debug("Update Document clean map")
        for fn, ft in self.model._fields.items():
            if fn not in self.data_model.model_fields:
                continue
            if isinstance(ft, BooleanField):
                self.clean_map[fn] = self.clean_bool
            elif isinstance(ft, (PlainReferenceField, ReferenceField)):
                if fn in self.mapped_fields:
                    self.clean_map[fn] = functools.partial(
                        self.clean_reference,
                        self.chain.get_mappings(self.mapped_fields[fn]),
                        ft.document_type,
                        self.mapped_fields[fn],
                    )
            elif isinstance(ft, ForeignKeyField):
                if fn in self.mapped_fields:
                    self.clean_map[fn] = functools.partial(
                        self.clean_int_reference,
                        self.chain.get_mappings(self.mapped_fields[fn]),
                        ft.document_type,
                        self.mapped_fields[fn],
                    )
            elif isinstance(ft, EmbeddedDocumentListField):
                self.clean_map[fn] = functools.partial(
                    self.clean_ed_list,
                    ft.field.document_type,
                )
            elif fn in self.mapped_fields:
                self.clean_map[fn] = functools.partial(
                    self.clean_map_str,
                    self.chain.get_mappings(self.mapped_fields[fn]),
                    self.mapped_fields[fn],
                )

    def update_model_clean_map(self):
        from django.db.models import BooleanField, ForeignKey
        from noc.core.model.fields import DocumentReferenceField

        self.logger.debug("Update Model clean map")
        for f in self.model._meta.fields:
            if f.name not in self.data_model.model_fields:
                continue
            if isinstance(f, BooleanField):
                self.clean_map[f.name] = self.clean_bool
            elif isinstance(f, DocumentReferenceField):
                if f.name in self.mapped_fields:
                    self.clean_map[f.name] = functools.partial(
                        self.clean_reference,
                        self.chain.get_mappings(self.mapped_fields[f.name]),
                        f.document,
                        self.mapped_fields[f.name],
                    )
            elif isinstance(f, ForeignKey):
                if f.name in self.mapped_fields:
                    self.clean_map[f.name] = functools.partial(
                        self.clean_reference,
                        self.chain.get_mappings(self.mapped_fields[f.name]),
                        f.remote_field.model,
                        self.mapped_fields[f.name],
                    )
            elif f.name in self.mapped_fields:
                self.clean_map[f.name] = functools.partial(
                    self.clean_map_str,
                    self.chain.get_mappings(self.mapped_fields[f.name]),
                    self.mapped_fields[f.name],
                )

    def check(self, chain):
        self.logger.info("Checking")
        # Get constraints
        if self.is_document:
            # Document
            required_fields = [
                f.name for f in self.model._fields.values() if f.required or f.unique
            ]
            unique_fields = [f.name for f in self.model._fields.values() if f.unique]
        else:
            # Model
            required_fields = [f.name for f in self.model._meta.fields if not f.blank]
            unique_fields = [
                f.name
                for f in self.model._meta.fields
                if f.unique and f.name != self.model._meta.pk.name
            ]
        if not required_fields and not unique_fields:
            self.logger.info("Nothing to check, skipping")
            return 0
        self.logger.debug("[%s] Required fields: %s", self.model, required_fields)
        self.logger.debug("[%s] Unique fields: %s", self.model, unique_fields)
        self.logger.debug("[%s] Mapped fields: %s", self.model, self.mapped_fields)
        # Prepare data
        ns = self.get_new_state()
        if not ns:
            self.logger.info("No new state, skipping")
            return 0
        new_state = self.iter_jsonl(ns)
        uv: Union[str, Tuple[str, str]] = set()
        m_data = {}  # field_number -> set of mapped ids
        # Load mapped ids
        for f in self.mapped_fields:
            line = chain.get_loader(self.mapped_fields[f])
            ls = line.get_new_state()
            if not ls:
                ls = line.get_current_state()
            ms = self.iter_jsonl(ls, data_model=line.data_model)
            m_data[f] = set(row.id for row in ms)
        r_data = defaultdict(dict)  # remote_system -> field_name -> set of mapped ids
        # Process data
        n_errors = 0
        for row in new_state:
            row = row.model_dump()
            lr = len(row)
            # Check required fields
            for f in required_fields:
                if f not in self.data_model.model_fields:
                    continue
                if f not in row:
                    self.logger.error(
                        "ERROR: Required field #(%s) is missed in row: %s",
                        f,
                        # self.fields[i],
                        row,
                    )
                    n_errors += 1
                    continue
            # Check unique fields
            for f in unique_fields:
                if f in self.ignore_unique:
                    continue
                v = row[f]
                if isinstance(v, dict) and "remote_system" in v:
                    v = (v["remote_system"], v["id"])
                if v in uv:
                    self.logger.error(
                        "ERROR: Field #(%s) value is not unique: %s",
                        f,
                        # self.fields[i],
                        row,
                    )
                    n_errors += 1
                else:
                    uv.add(v)
            # Check mapped fields
            for i, f in enumerate(self.mapped_fields):
                if i >= lr:
                    continue
                v = row[f]
                if v and "remote_system" in v:
                    # Mapping with remote system
                    rs, value = v["remote_system"], v["id"]
                    if rs not in r_data or f not in r_data[rs]:
                        r_data[rs][f] = set(self.get_remote_mappings(rs, self.mapped_fields[f]))
                    if value and value not in r_data[rs][f]:
                        self.logger.error(
                            "ERROR: Field #%d(%s) == '%s::%s' refers to non-existent record: %s",
                            i,
                            f,
                            rs,
                            row[f]["id"],
                            row,
                        )
                        n_errors += 1
                elif isinstance(v, dict) and "scope" in v:
                    value = self.get_mapping(v["scope"], v["value"])
                    if not value:
                        self.logger.error(
                            "ERROR: Field #%d(%s) == '%s::%s' refers to non-existent NOC record: %s",
                            i,
                            f,
                            v["scope"],
                            row[f]["value"],
                            row,
                        )
                        n_errors += 1
                elif v and v not in m_data[f]:
                    self.logger.error(
                        "ERROR: Field #%d(%s) == '%s' refers to non-existent record: %s",
                        i,
                        f,
                        row[f],
                        row,
                    )
                    n_errors += 1
        if n_errors:
            self.logger.info("%d errors found", n_errors)
        else:
            self.logger.info("No errors found")
        return n_errors

    def check_diff(self):
        def dump(cmd, row):
            print("%s %s" % (cmd, row.json()))

        print("--- %s.%s" % (self.chain.system.name, self.name))
        ns = self.get_new_state()
        if not ns:
            return
        current_state = self.iter_jsonl(self.get_current_state())
        new_state = self.iter_jsonl(ns)
        for o, n in self.diff(current_state, new_state):
            if o is None and n:
                dump("+", n)
            elif o and n is None:
                dump("-", o)
            else:
                dump("/", o)
                dump("\\", n)

    def check_diff_summary(self):
        i, u, d = 0, 0, 0
        ns = self.get_new_state()
        if not ns:
            return i, u, d
        current_state = self.iter_jsonl(self.get_current_state())
        new_state = self.iter_jsonl(ns)
        for o, n in self.diff(current_state, new_state):
            if o is None and n:
                i += 1
            elif o and n is None:
                d += 1
            else:
                u += 1
        return i, u, d
