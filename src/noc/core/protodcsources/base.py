# ----------------------------------------------------------------------
# DiscriminatorSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config


@dataclass(frozen=True)
class DiscriminatorDataItem:
    interface: str
    attr: str
    value: Any


class BaseDiscriminatorSource(ABC):
    """DataSource and fields description"""

    name: str

    def __init__(self, protocol, data: list[DiscriminatorDataItem] | None = None) -> None:
        self.protocol = protocol
        self.data = data

    def __iter__(self) -> Iterable[str]:
        """
        Iterate over Discriminator code
        """

    def __contains__(self, item) -> bool:
        """
        Check discriminator code exists
        """

    @abstractmethod
    def get_data(self, code: str) -> list[DiscriminatorDataItem]:
        """
        Get Discriminator Data by code
        """
        ...

    @abstractmethod
    def get_code(self, data: list[DiscriminatorDataItem]) -> str:
        """
        Get Discriminator Code by data
        """
        ...

    def get_discriminator_instance(self, code: str):
        """
        Getting Discriminator Instance by Code
        :return:
        """


discriminator_source_loader = Loader[type[BaseDiscriminatorSource]](
    bases=config.iter_customized_bases("noc.core.protodcsources"),
    exclude=("base",),
)
