# ----------------------------------------------------------------------
# BaseGeocoder class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any, Iterator

# NOC modules
from noc.core.http.sync_client import HttpClient
from .errors import GeoCoderError


@dataclass
class GeoCoderResult:
    exact: bool
    query: str
    path: list[str]
    lon: float | None = None
    lat: float | None = None
    id: str | None = None
    address: str | None = None
    scope: str | None = None


class BaseGeocoder:
    name = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    def forward(self, query: str, bounds=None) -> GeoCoderResult:
        """
        Forward lookup
        :param query: Address as string
        :type query: str
        :return: GeoCoderResult or None
        """
        try:
            return next(self.iter_query(query, bounds))
        except StopIteration:
            return None

    def iter_query(self, query: str, bounds=None) -> Iterator[GeoCoderResult]:
        """
        Get list of probable address candidates
        :return:
        """
        raise NotImplementedError()

    def iter_recursive_query(self, query: str, bounds=None) -> Iterator[GeoCoderResult]:
        """
        Get list of all addresses within the query
        :return:
        """
        yield from self.iter_query(query, bounds)

    def get(self, url: str) -> tuple[int, bytes]:
        """
        Perform get request
        :type url: str
        :return:
        """
        with HttpClient(
            timeout=60,
            allow_proxy=True,
            validate_cert=False,
        ) as client:
            code, headers, body = client.get(url)
            if 200 <= code <= 299:
                return code, body
            raise GeoCoderError(f"HTTP Error {code}")

    @staticmethod
    def get_path(data, path):
        """
        Returns nested object referred by dot-separated path, or None
        :return:
        """
        o = data
        for p in path.split("."):
            if p in o:
                o = o[p]
            else:
                return None
        return o

    @staticmethod
    def maybe_float(f: Any) -> float | None:
        if isinstance(f, float):
            return f
        if f:
            return float(f)
        return None
