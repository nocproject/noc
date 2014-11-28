## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rate-limiting utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import threading


class TokenBucket(object):
    """
    Token bucket algorithm
    """
    def __init__(self, rate=1, capacity=1):
        self.capacity = float(capacity)
        self.rate = float(rate)
        self.tokens = self.capacity
        self.ts = time.time()

    def get_tokens(self):
        if self.tokens < self.capacity:
            now = time.time()
            d = self.rate * (now - self.ts)
            self.tokens = min(self.capacity, self.tokens + d)
            self.ts = now
        return self.tokens

    def consume(self, amount=1.0):
        if amount <= self.get_tokens():
            self.tokens -= amount
            return True
        else:
            return False

    def configure(self, rate=None, capacity=None):
        if rate:
            self.rate = rate
        if capacity:
            self.capacity = float(capacity)
            self.tokens = min(self.tokens, capacity)


class SafeTokenBucket(TokenBucket):
    """
    Thread-safe implementation of token bucket
    """
    def __init__(self, rate=1, capacity=1):
        super(SafeTokenBucket, self).__init__(rate, capacity)
        self.lock = threading.Lock()

    def consume(self, amount=1.0):
        with self.lock:
            return super(SafeTokenBucket, self).consume(amount)

    def configure(self, rate=None, capacity=None):
        with self.lock:
            super(SafeTokenBucket, self).configure(capacity, rate)
