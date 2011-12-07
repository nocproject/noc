# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Finite State Machine
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import logging
import re


def check_state(*sargs):
    """
    State checking decorator
    """

    def check_returns(f):
        def new_f(self, *args, **kwds):
            assert self._current_state in sargs,\
            "Function '%s' cannot be called from state '%s' (%s required)" % (
            f.func_name, self._current_state, sargs)
            return f(self, *args, **kwds)

        new_f.func_name = f.func_name
        return new_f

    return check_returns


##
## Exceptions
##
class FSMEventError(Exception):
    def __init__(self, state, event):
        super(FSMEventError, self).__init__(
            "Invalid event '%s' in state '%s'" % (event, state))
        self.state = state
        self.event = event


class FSMStateError(Exception):
    def __init__(self, state):
        super(FSMStateError, self).__init__("Invalid state: '%s'" % state)
        self.state = state


class FSM(object):
    """
    Finite state machine class
    """
    FSM_NAME = "FSM"
    DEFAULT_STATE = "DEFAULT"  # Running state
    STATES = {}                # STATE -> { EVENT -> New State}

    def __init__(self):
        self._current_state = None
        self._state_enter_time = None
        self._state_exit_time = None
        self.set_state(self.DEFAULT_STATE)

    def debug(self, msg):
        logging.debug("[%s(0x%x)]<%s> %s" % (self.__class__.__name__, id(self),
                                             self.get_state(), msg))

    def get_state_handler(self, state, event):
        name = "on_%s_%s" % (state, event)
        try:
            return getattr(self, name)
        except:
            return None

    def call_state_handler(self, state, event, *args):
        h = self.get_state_handler(state, event)
        if h:
            apply(h, args)

    def get_state(self):
        return self._current_state

    def set_state(self, state):
        if state == self._current_state:
            return
        self.debug("==> %s" % state)
        if state not in self.STATES:
            raise FSMStateError(state)
        if self._current_state:
            self.call_state_handler(self._current_state, "exit")
        self._current_state = state
        self._state_enter_time = time.time()
        self._state_exit_time = None
        self.call_state_handler(state, "enter")

    def set_timeout(self, timeout):
        self.debug("set_timeout(%s)" % timeout)
        self._state_exit_time = time.time() + timeout

        ##
    ## Send event to FSM
    ##
    def event(self, event):
        self.debug("event(%s)" % event)
        if event not in self.STATES[self._current_state]:
            raise FSMEventError(self._current_state, event)
        self.call_state_handler(self._current_state, event)
        self.set_state(self.STATES[self._current_state][event])

    def tick(self):
        """
        Method should be called in event loop every second
        to process timeout and tick events
        """
        if self._state_exit_time and self._state_exit_time < time.time():
            self.debug("Timeout expired")
            self.event("timeout")
        else:
            self.call_state_handler(self._current_state, "tick")

    @classmethod
    def get_dot(cls):
        """
        Make nice GraphViz .dot chart
        """
        r = ["digraph {"]
        r += ["label=\"%s state machine\";" % cls.FSM_NAME]
        for s in cls.STATES:
            if s == cls.DEFAULT_STATE:
                r += ["%s [shape=\"doublecircle\"];" % s]
            else:
                r += ["%s;" % s]
            transforms = {}
            for e, ns in cls.STATES[s].items():
                if ns in transforms:
                    transforms[ns].append(e)
                else:
                    transforms[ns] = [e]
            for ns, events in transforms.items():
                r += ["%s -> %s [label=\"%s\"];" % (s, ns,
                                                    ",\\n".join(events))]
        r += ["}", ""]
        return "\n".join(r)

    @classmethod
    def write_dot(cls, path):
        f = open(path, "w")
        f.write(cls.get_dot())
        f.close()


class StreamFSM(FSM):
    """
    StreamFSM also changes state on input stream conditions
    """
    MATCH_TAIL = 0  # Match only N tailing bytes if not 0

    def __init__(self, async_throttle=None):
        self.patterns = []
        self.in_buffer = ""
        self.async_throttle = async_throttle  # Limit to throttle synchronous check
        self.feed_count = 0  # Number of bytes fed from last state transition
        self.cleanup = None
        super(StreamFSM, self).__init__()

    def debug(self, msg):
        logging.debug("[%s(0x%x)]<%s> %s" % (
        self.__class__.__name__, id(self), self.get_state(), msg))

    def set_patterns(self, patterns):
        self.debug("set_patterns(%s)" % repr(patterns))
        self.patterns = [(re.compile(x, re.DOTALL | re.MULTILINE), y) for x, y
                                                                      in
                                                                      patterns]

    def in_async_check(self):
        return (self.async_throttle is not None and
                self.feed_count >= self.async_throttle)

    def check_fsm(self):
        if self.cleanup:
            self.in_buffer = self.cleanup(self.in_buffer)
        while self.in_buffer and self.patterns:
            matched = False
            for rx, event in self.patterns:
                if self.MATCH_TAIL:
                    offset = max(0, len(self.in_buffer) - self.MATCH_TAIL)
                else:
                    offset = 0
                match = rx.search(self.in_buffer, offset)
                if match:
                    matched = True
                    self.feed_count = 0  # Reset counter on event
                    self.debug("match '%s'" % rx.pattern)
                    self.call_state_handler(self._current_state, "match",
                                            self.in_buffer[:match.start(0)],
                                            match)
                    self.in_buffer = self.in_buffer[match.end(0):]
                    self.match = match
                    self.event(event)  # Change state
                    break
            if not matched:
                break

    def feed(self, data, cleanup=None):
        self.in_buffer += data
        self.feed_count += len(data)
        self.cleanup = cleanup
        if not self.in_async_check():
            self.check_fsm()

    def async_check_fsm(self):
        if self.in_async_check():
            self.debug("Asynchronous check")
            self.check_fsm()

    def reset_async_check(self):
        self.feed_count = 0
