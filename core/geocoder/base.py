# ----------------------------------------------------------------------
# BaseGeocoder class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Any, Optional, List, Iterator, Tuple

# NOC modules
from noc.core.http.sync_client import HttpClient
from .errors import GeoCoderError


@dataclass
class GeoCoderResult(object):
    exact: bool
    query: str
    path: List[str]
    lon: Optional[float] = None
    lat: Optional[float] = None
    id: Optional[str] = None
    address: Optional[str] = None
    scope: Optional[str] = None


class BaseGeocoder(object):
    name = None

    def __init__(self, *args, **kwargs):
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
        :param query:
        :param bounds:
        :return:
        """
        raise NotImplementedError()

    def iter_recursive_query(self, query: str, bounds=None) -> Iterator[GeoCoderResult]:
        """
        Get list of all addresses within the query
        :param query:
        :param bounds:
        :return:
        """
        yield from self.iter_query(query, bounds)

    def get(self, url: str) -> Tuple[int, bytes]:
        """
        Perform get request
        :param url:
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
            raise GeoCoderError("HTTP Error %s" % code)

    @staticmethod
    def get_path(data, path):
        """
        Returns nested object referred by dot-separated path, or None
        :param data:
        :param path:
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
    def maybe_float(f: Any) -> Optional[float]:
        if isinstance(f, float):
            return f
        if f:
            return float(f)
        return None
