# ---------------------------------------------------------------------
# Environment implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Optional, Iterable, Tuple


class Environment(object):
    """
    Environment.

    Environment is a nested dict-like structure.
    In case of miss, keys are searched in parent's
    environment.
    """

    def __init__(self, data: Optional[Dict[str, str]] = None) -> None:
        self._data: Dict[str, str] = {}
        if data:
            self._data.update(data.items())
        self._parent: Optional[Environment] = None
        self._is_dirty = False

    @property
    def is_dirty(self) -> bool:
        """
        Check if ennvironment is modified
        """
        return self._is_dirty

    def clear_dirty(self) -> None:
        """
        Clear dirty status.
        """
        self._is_dirty = False

    def raw_data(self) -> Dict[str, str]:
        """
        Returns data directly belonging to the environment.
        """
        return self._data

    def set_parent(self, parent: "Environment") -> None:
        """
        Set parent environment.
        """
        self._parent = parent

    def get(self, name: str) -> Optional[str]:
        """
        Check for key.

        Refer to the parent, if necessary.

        Args:
            name: Key name.
        Returns:
            Nearest key value: if found
            None: if not found.
        """
        item = self._data.get(name)
        if item:
            return item
        if self._parent:
            return self._parent.get(name)
        return None

    def __getitem__(self, name: str) -> str:
        """
        Square bracket access.
        """
        item = self.get(name)
        if item is None:
            raise KeyError()
        return item

    def __setitem__(self, name: str, value: str) -> None:
        """
        Square bracket setter.
        """
        if self._parent:
            self._parent._data[name] = value
            self._parent._is_dirty = True
        else:
            self._data[name] = value
            self._is_dirty = True

    def __iter__(self) -> Iterable["str"]:
        return self.keys()

    def _iter_parents(self) -> Iterable["Environment"]:
        """
        Iterate over parents.

        Starting for closer one to the deepest.
        """
        p = self._parent
        while p is not None:
            yield p
            p = p._parent

    def __contains__(self, name: str) -> bool:
        """
        Check if key is in environment.
        """
        if name in self._data:
            return True
        for p in self._iter_parents():
            if name in p._data:
                return True
        return False

    def keys(self) -> Iterable[str]:
        """Iterate over keys."""
        seen = set(self._data)
        yield from self._data.keys()
        for parent in self._iter_parents():
            for k in parent._data:
                if k not in seen:
                    yield k
                    seen.add(k)

    def values(self) -> Iterable[str]:
        """Iterate over values."""
        seen = set(self._data)
        yield from self._data.values()
        for parent in self._iter_parents():
            for k, v in parent._data.items():
                if k not in seen:
                    yield v
                    seen.add(k)

    def items(self) -> Iterable[Tuple[str, str]]:
        """Iterate over key-values pairs."""
        seen = set(self._data)
        yield from self._data.items()
        for parent in self._iter_parents():
            for k, v in parent._data.items():
                if k not in seen:
                    yield (k, v)
                    seen.add(k)
