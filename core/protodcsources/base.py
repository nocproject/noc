# ----------------------------------------------------------------------
# DiscriminatorSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Iterable, Any


@dataclass(frozen=True)
class DiscriminatorDataItem(object):
    interface: str
    attr: str
    value: Any


class BaseDiscriminatorSource(ABC):
    """DataSource and fields description"""

    name: str

    def __init__(self, protocol, data: List[DiscriminatorDataItem] = None):
        self.protocol = protocol
        self.data = data

    def __iter__(self) -> Iterable[str]:
        """
        Iterate over Discriminator code
        """
        ...

    def __contains__(self, item) -> bool:
        """
        Check discriminator code exists
        """
        ...

    @abstractmethod
    def get_data(self, code: str) -> List[DiscriminatorDataItem]:
        """
        Get Discriminator Data by code
        """
        ...

    @abstractmethod
    def get_code(self, data: List[DiscriminatorDataItem]) -> str:
        """
        Get Discriminator Code by data
        """
        ...

    def get_discriminator_instance(self, code: str):
        """
        Getting Discriminator Instance by Code
        :return:
        """
