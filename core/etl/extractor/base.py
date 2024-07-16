# ----------------------------------------------------------------------
# Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import os
import csv
import itertools
import io
import contextlib
import dataclasses
import operator
import re
from time import perf_counter
from typing import Any, List, Iterable, Type, Union, Tuple, Set, Optional

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.config import config
from noc.core.comp import smart_text
from noc.core.etl.compression import compressor
from ..models.base import BaseModel
from ..remotesystem.base import BaseRemoteSystem

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Problem(object):
    line: int
    is_rej: bool
    p_class: str
    message: str
    row: List[Any]


@dataclasses.dataclass
class RemovedItem(object):
    id: str


class BaseExtractor(object):
    """
    Data extractor interface. Subclasses must provide
    *iter_data* method
    """

    name: str
    PREFIX = config.path.etl_import
    REPORT_INTERVAL = 1000
    # Type of model
    model: Type[BaseModel]
    # List of rows to be used as constant data
    data: List[BaseModel] = []
    # Suppress deduplication message
    suppress_deduplication_log: bool = False

    rx_archive = re.compile(
        r"^import-\d{4}(?:-\d{2}){5}.jsonl%s$" % compressor.ext.replace(".", r"\.")
    )

    def __init__(self, system: "BaseRemoteSystem"):
        self.system = system
        self.config = system.config
        self.logger = PrefixLoggerAdapter(logger, "%s][%s" % (system.name, self.name))
        self.import_dir = os.path.join(self.PREFIX, system.name, self.name)
        self.fatal_problems: List[Problem] = []
        self.quality_problems: List[Problem] = []
        # Checkpoint
        self._force_checkpoint: Optional[str] = None

    def register_quality_problem(
        self, line: int, p_class: str, message: str, row: List[Any]
    ) -> None:
        self.quality_problems += [
            Problem(line=line + 1, is_rej=False, p_class=p_class, message=message, row=row)
        ]

    def register_fatal_problem(self, line: int, p_class: str, message: str, row: List[Any]) -> None:
        self.fatal_problems += [
            Problem(line=line + 1, is_rej=True, p_class=p_class, message=message, row=row)
        ]

    def ensure_import_dir(self) -> None:
        """
        Ensure import directory is exists
        :return:
        """
        if os.path.isdir(self.import_dir):
            return
        self.logger.info("Creating directory %s", self.import_dir)
        os.makedirs(self.import_dir)

    def get_new_state(self) -> io.TextIOBase:
        self.ensure_import_dir()
        path = compressor.get_path(os.path.join(self.import_dir, "import.jsonl"))
        self.logger.info("Writing to %s", path)
        return compressor(path, "w").open()

    @contextlib.contextmanager
    def with_new_state(self):
        """
        New state context manager. Usage::

        with e.with_new_state() as f:
            ...

        :return:
        """
        f = self.get_new_state()
        try:
            yield f
        finally:
            f.close()

    def get_problem_file(self) -> io.TextIOBase:
        self.ensure_import_dir()
        path = compressor.get_path(os.path.join(self.import_dir, "import.csv.rej"))
        self.logger.info("Writing to %s", path)
        return compressor(path, "w").open()

    @contextlib.contextmanager
    def with_problem_file(self):
        """
        New state context manager. Usage::

        with e.with_problem_file() as f:
            ...

        :return:
        """
        f = self.get_problem_file()
        try:
            yield f
        finally:
            f.close()

    def iter_data(
        self, *, checkpoint: Optional[str] = None, **kwargs
    ) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        """
        Iterator to extract data.

        Args:
            checkpoint: Incremental extraction from checkpoint, if set.
            kwargs: Parameters for future use. Unknown parameters
                must be ignored.

        Returns:
            Iterable of the extracted items.
        """
        yield from self.data

    def filter(self, row) -> bool:
        return True

    def clean(self, row):
        return row

    def read_current_state(self) -> Optional[List[BaseModel]]:
        """
        Read current state.

        Returns:
            List of items or None
        """
        # Check if import_dir is exists
        if not os.path.isdir(self.import_dir):
            return None  # No state
        # Check if archive dir is exists
        archive_dir = os.path.join(self.import_dir, "archive")
        if not os.path.isdir(archive_dir):
            return None  # No archive
        # Read list of archive files
        fn = list(
            sorted((f for f in os.listdir(archive_dir) if self.rx_archive.match(f)), reverse=True)
        )
        if not fn:
            return None  # No files
        # Read file
        path = os.path.join(self.import_dir, "archive", fn[0])
        self.logger.info("Reading current state from %s", path)
        data = []
        with compressor(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data.append(self.model.model_validate_json(line))
        return data

    def get_checkpoint(self, data: List[BaseModel]) -> Optional[str]:
        """
        Get latest checkpoint from the state.

        Args:
            data: List of last state's records.

        Returns:
            Latest checkpoint, if any. None otherwise.
        """
        cp = None
        if self._force_checkpoint:
            return self._force_checkpoint
        if not hasattr(self.model, "checkpoint"):
            self.logger.info("Extractor not supported attribute checkpoint")
            return cp
        for item in data:
            if item.checkpoint and (not cp or item.checkpoint > cp):
                cp = item.checkpoint
        return cp

    def iter_merge_data(
        self, current: Optional[List[BaseModel]], delta: Optional[List[BaseModel]]
    ) -> Iterable[BaseModel]:
        """
        Merge current state with delta.

        Args:
            current: Current state.
            delta: Incremental changes.

        Returns:
            Resulting list
        """
        if not delta:
            return  # No changes
        if not current:
            yield from delta  # No current state
            return
        iter_c = iter(sorted(current, key=operator.attrgetter("id")))
        iter_d = iter(sorted(delta, key=operator.attrgetter("id")))
        c = next(iter_c, None)
        d = next(iter_d, None)
        while c or d:
            if c and not d:
                # Delta is over, stream current
                yield c  # Already fetched
                yield from iter_c  # Left
                return
            if not c and d:
                # Current is over, stream delta
                yield d  # Already fetched
                yield from iter_d  # Left
                return
            if c.id < d.id:
                # Less than next delta, yield current
                yield c
                c = next(iter_c, None)
            elif c.id == d.id:
                # Exact match, stream delta
                yield d
                c = next(iter_c, None)
                d = next(iter_d, None)
            else:
                # Delta less than current, yield delta
                yield d
                d = next(iter_d, None)

    def extract(self, incremental: bool = False, **kwargs) -> None:
        def q(s: Any) -> str:
            if s == "" or s is None:
                return ""
            if isinstance(s, str):
                return s
            return str(s)

        def get_model(raw: Union[BaseModel, Tuple[Any, ...]]) -> BaseModel:
            if isinstance(raw, BaseModel):
                return raw
            return self.model.from_iter(q(x) for x in row)

        # Fetch data
        self.logger.info(
            "Extracting %s from %s (%s)",
            self.name,
            self.system.name,
            "Incremental" if incremental else "Full",
        )
        # Prepare iterator
        current: Optional[List[BaseModel]] = None
        checkpoint: Optional[str] = None
        if incremental:
            # Incremental extract
            current = self.read_current_state()
            if current:
                # Has state
                checkpoint = self.get_checkpoint(current)
                if checkpoint:
                    self.logger.info("Resuming from checkpoint %s", checkpoint)
                else:
                    self.logger.info("Checkpoint not found. Falling back to full extract")
            else:
                # No current state
                self.logger.info("No current state. Falling back to full extract")
        # Extract
        t0 = perf_counter()
        data: List[BaseModel] = []
        n = 0
        seen: Set[str] = set()
        removed: Set[str] = set()
        for row in self.iter_data(checkpoint=checkpoint):
            if not self.filter(row):
                continue
            if isinstance(row, RemovedItem):
                removed.add(row.id)
                continue
            row = self.clean(row)
            # Do not use get_model(self.clean(row)), to zip_longest broken row
            row = get_model(row)
            if row.id in seen:
                if not self.suppress_deduplication_log:
                    self.logger.error("Duplicated row truncated: %r", row)
                continue
            seen.add(row.id)
            data += [row]
            n += 1
            if n % self.REPORT_INTERVAL == 0:
                self.logger.info("   ... %d records", n)
        dt = perf_counter() - t0
        speed = n / dt
        self.logger.info("%d records extracted in %.2fs (%d records/s)", n, dt, speed)
        # Merge incremental data
        if incremental:
            # Prune removed items
            if removed and current:
                current = [x for x in current if x.id not in removed]
            # Merge
            data = list(self.iter_merge_data(current, data))
        if incremental and not data:
            return
        # Write
        with self.with_new_state() as f:
            for n, item in enumerate(sorted(data, key=operator.attrgetter("id"))):
                if n:
                    f.write("\n")
                f.write(item.json(exclude_defaults=True, exclude_unset=True))
        # Report fatal problems
        if self.fatal_problems or self.quality_problems:
            self.logger.warning(
                "Detect problems on extracting, fatal: %d, quality: %d",
                len(self.fatal_problems),
                len(self.quality_problems),
            )
            self.logger.warning("Line num\tType\tProblem string")
            for p in self.fatal_problems:
                self.logger.warning(
                    "Fatal problem, line was rejected: %s\t%s\t%s" % (p.line, p.p_class, p.message)
                )
            for p in self.quality_problems:
                self.logger.warning(
                    "Data quality problem in line:  %s\t%s\t%s" % (p.line, p.p_class, p.message)
                )
            # Dump problem to file
            try:
                with self.with_problem_file() as f:
                    writer = csv.writer(f, delimiter=";")
                    for p in itertools.chain(self.quality_problems, self.fatal_problems):
                        writer.writerow(
                            [smart_text(c) for c in p.row]
                            + [
                                (
                                    "Fatal problem, line was rejected"
                                    if p.is_rej
                                    else "Data quality problem"
                                )
                            ]
                            + [p.message.encode("utf-8")]
                        )
            except IOError as e:
                self.logger.error("Error when saved problems %s", e)
        else:
            self.logger.info("No problems detected")
