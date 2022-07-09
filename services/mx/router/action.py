# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Type, Tuple, Dict, Iterator

# NOC modules
from noc.core.liftbridge.message import Message
from noc.main.models.messageroute import MessageRoute
from noc.core.comp import smart_bytes
from noc.main.models.notificationgroup import NotificationGroup


DROP = ""
ACTION_TYPES: Dict[str, Type["Action"]] = {}


class ActionBase(type):
    def __new__(mcs, name, bases, attrs):
        global ACTION_TYPES
        cls = type.__new__(mcs, name, bases, attrs)
        name = getattr(cls, "name", None)
        if name:
            ACTION_TYPES[name] = cls
        return cls


class Action(object, metaclass=ActionBase):
    name: str

    def __init__(self, mroute: MessageRoute):
        self.headers: Dict[str, bytes] = {h.header: smart_bytes(h.value) for h in mroute.headers}

    @classmethod
    def from_action(cls, mroute: MessageRoute) -> "Action":
        global ACTION_TYPES

        return ACTION_TYPES[mroute.action](mroute)

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        raise NotImplementedError


class DropAction(Action):
    name = "drop"

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        yield DROP, {}


class StreamAction(Action):
    name = "stream"

    def __init__(self, mroute: MessageRoute):
        super().__init__(mroute)
        self.stream: str = mroute.stream

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        yield self.stream, self.headers


class NotificationAction(Action):
    name = "notification"

    def __init__(self, mroute: MessageRoute):
        super().__init__(mroute)
        self.ng: NotificationGroup = mroute.notification_group

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        yield from self.ng.iter_actions()
