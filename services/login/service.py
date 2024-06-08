#!./bin/python
# ---------------------------------------------------------------------
# Login service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import orjson
import heapq
import datetime
import asyncio

# import time

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config
from noc.core.msgstream.message import Message
from noc.services.login.auth import get_exp_from_jwt
from noc.core.comp import smart_bytes


class LoginService(FastAPIService):
    name = "login"
    process_name = "noc-%(name).10s-%(instance).2s"
    use_mongo = True
    use_translation = True
    use_watchdog = config.watchdog.enable_watchdog
    traefik_routes_rule = "PathPrefix(`/api/login`) || PathPrefix(`/api/auth/auth`)"

    OPENAPI_TAGS_DOCS = {
        "login": "Authentication services",
        "ext-ui": "Legacy ExtJS UI services. To be removed with decline of legacy UI",
    }

    def __init__(self):
        super().__init__()
        self.revoked_tokens = set()
        self.revoked_expiry = []
        self.revoked_cond = asyncio.Condition()

    async def revoke_token(self, token: str, audience: str) -> None:
        """
        Mark token as revoked. Any futher use will be prohibited
        :param token:
        :param audience:
        :return: str
        """
        ts = datetime.datetime.utcnow()
        if token in self.revoked_tokens:
            return None
        exp = datetime.datetime.fromtimestamp(get_exp_from_jwt(token, audience))
        msg = {
            "token": token,
            "ts": ts.isoformat(),
            "expired": exp.isoformat(),
        }
        self.publish(smart_bytes(orjson.dumps(msg)), "revokedtokens", 0)
        while token not in self.revoked_tokens:
            async with self.revoked_cond:
                await self.revoked_cond.wait()
        e2e = (datetime.datetime.utcnow() - ts).total_seconds()
        timeout = min(max(e2e * 3, 1), 30)
        await asyncio.sleep(timeout)

    def is_revoked(self, token: str) -> bool:
        """
        Check if token is revoked
        :param token: encoded JWT token to check
        :return: True if token is revoked
        """
        return token in self.revoked_tokens

    async def on_revoked_token(self, msg: Message) -> None:
        msg_dict = orjson.loads(msg.value)
        self.revoked_tokens.add(msg_dict["token"])
        heapq.heappush(
            self.revoked_expiry,
            (
                datetime.datetime.strptime(msg_dict["expired"], "%Y-%m-%dT%H:%M:%S"),
                msg_dict["token"],
            ),
        )
        # Check expired tokens
        heapq.heapify(self.revoked_expiry)
        for r in self.revoked_expiry.copy():
            if r[0] >= datetime.datetime.utcnow():
                break
            self.revoked_tokens.remove(r[1])
            heapq.heappop(self.revoked_expiry)

        async with self.revoked_cond:
            self.revoked_cond.notify_all()

    async def subscribe_lift(self):
        # revokedtokens is optional, so mark liftbridge as non-critical service.
        config.find_parameter("liftbridge.addresses").set_critical(False)
        # expire = config.login.session_ttl
        # start_timestamp = time.time() - expire
        await self.subscribe_stream(
            "revokedtokens",
            0,
            self.on_revoked_token,
            # Disable on Liftbridge Bug for subscribe by timestamp
            # start_timestamp=start_timestamp,
            # start_position=StartPosition.TIMESTAMP,
            auto_set_cursor=False,
        )

    async def on_activate(self):
        self.loop.create_task(self.subscribe_lift())


if __name__ == "__main__":
    LoginService().start()
