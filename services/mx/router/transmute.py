# ----------------------------------------------------------------------
# Transmute
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Typing
from typing import Type, Union, Any, Dict, Iterator, Callable

# Third-party modules
from jinja2 import Template
import orjson

# NOC modules
from noc.main.models.messageroute import MRTransmute
from noc.core.comp import smart_text


TRANSMUTE_TYPES: Dict[str, Type["Transmutation"]] = {}

T_BODY = Union[bytes, Any]


class TransmutationBase(type):
    def __new__(mcs, name, bases, attrs):
        global TRANSMUTE_TYPES
        cls = type.__new__(mcs, name, bases, attrs)
        name = getattr(cls, "name", None)
        if name:
            TRANSMUTE_TYPES[name] = cls
        return cls


class Transmutation(object, metaclass=TransmutationBase):
    name: str

    def __init__(self, transmute: MRTransmute):
        pass

    def iter_transmute(
        self, headers: Dict[str, bytes], iter_data: Iterator[T_BODY]
    ) -> Iterator[T_BODY]:
        """
        Apply mutations to the message and return the result

        :param headers:
        :param iter_data:
        :return:
        """
        yield from iter_data

    @classmethod
    def from_transmute(cls, transmute: MRTransmute) -> "Transmutation":
        global TRANSMUTE_TYPES

        return TRANSMUTE_TYPES[transmute.type](transmute)


class TemplateTransmutation(Transmutation):
    name = "template"

    def __init__(self, transmute: MRTransmute):
        super().__init__(transmute)
        self.template: Template = Template(transmute.template.body)

    def iter_transmute(
        self, headers: Dict[str, bytes], iter_data: Iterator[T_BODY]
    ) -> Iterator[T_BODY]:
        h_ctx = {h: smart_text(headers[h]) for h in headers}
        for data in iter_data:
            if isinstance(data, bytes):
                data = orjson.loads(data)
            ctx = {"headers": h_ctx, **data}
            yield self.template.render(**ctx)


class HandlerTransmutation(Transmutation):
    name = "handler"

    def __init__(self, transmute: MRTransmute):
        super().__init__(transmute)
        self.handler: Callable[
            [Dict[str, bytes], Iterator[T_BODY]], Iterator[T_BODY]
        ] = transmute.handler.get_handler()

    def iter_transmute(
        self, headers: Dict[str, bytes], iter_data: Iterator[T_BODY]
    ) -> Iterator[T_BODY]:
        yield from self.handler(headers, iter_data)
