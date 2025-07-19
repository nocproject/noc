# ----------------------------------------------------------------------
# DIT TT Integration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List
from urllib.parse import urlparse


# Third-party modules
import orjson

# NOC modules
from noc.core.tt.base import BaseTTSystem, TTError
from noc.core.tt.types import (
    EscalationContext,
    DeescalationContext,
    TTActionContext,
    TTInfo,
    TTAction,
    TTChange,
)
from noc.core.span import Span
from noc.core.http.sync_client import HttpClient


class TGBotTTSystem(BaseTTSystem):
    TU_REQUEST_TIMEOUT = 30
    actions = [TTAction.ACK, TTAction.UN_ACK]

    def __init__(self, name, connection):
        """
        Connection is WSDL path
        """
        super(TGBotTTSystem, self).__init__(name, connection)
        p = urlparse(connection)
        self.url = "https://%s%s" % (p.netloc, p.path)
        self.http_client = HttpClient(
            connect_timeout=10,
            timeout=self.TU_REQUEST_TIMEOUT,
            headers={
                "Content-Type": b"application/json",
                "Accept": b"application/json",
            },
        )

    def close(self, ctx: DeescalationContext) -> None:
        """
        Close TT.

        Args:
            ctx: Deescalation context.

        Raises:
            TTError: on deescalation error.
        """
        with Span(server="telegram", service="deleteMessage", in_label=ctx.id):
            self.http_client.post(
                f"{self.url}/deleteMessage",
                orjson.dumps(
                    {
                        "chat_id": ctx.login,
                        "message_id": ctx.id,
                        # "parse_mode": "HTML",
                        # "caption": ctx.subject,
                        # "text": "\n\n".join([ctx.subject, ctx.body or ""]),
                    }
                ),
            )

    @staticmethod
    def get_inline_keyboard(actions: List[TTActionContext]):
        r = []
        if not actions:
            return {}
        for ctx in actions:
            r.append({"text": ctx.label or ctx.action.name, "callback_data": ctx.action.value})
        # if TTAction.ACK in actions:
        #     r.append({"text": "Ack", "callback_data": TTAction.ACK.value})
        # if TTAction.CLOSE in actions:
        #     r.append({"text": "Close", "callback_data": TTAction.CLOSE.value})
        if not r:
            return {}
        return {"inline_keyboard": [r]}

    def create(self, ctx: EscalationContext) -> str:
        """
        "reply_markup": {"inline_keyboard": [[{"text": "Ack", "callback_data": "alarm_id"}]]}}
        """
        print(
            f"{ctx.id}Create document",
            self.url,
            "\n\n".join([ctx.subject, ctx.body or ""]),
            ctx.actions,
        )
        msg = {
            "chat_id": ctx.queue,
            # "chat_id": self.chat_id,
            "text": "\n\n".join([ctx.subject, ctx.body or ""]),
            "parse_mode": "HTML",
        }
        if ctx.actions:
            msg["reply_markup"] = self.get_inline_keyboard(ctx.actions)
        action = "sendMessage"
        if ctx.id:
            # changed
            self.logger.info("Changed TT: %s", ctx.id)
            action = "editMessageText"
            msg["message_id"] = ctx.id
        with Span(server="telegram", service="sendMessage"):
            status, _, body = self.http_client.post(
                f"{self.url}/{action}",
                orjson.dumps(msg),
            )
            body = orjson.loads(body)
            self.logger.info("Telegram send result: %s/%s", body, status)
            if status == 200 and "result" in body:
                return str(body["result"]["message_id"])
            raise TTError(body["description"])

    @staticmethod
    def parse_update_message(self): ...

    def get_updates(
        self,
        last_run: Optional[datetime] = None,
        last_update: Optional[str] = None,
        tt_ids: Optional[List[str]] = None,
    ) -> List[TTChange]:
        status, _, body = self.http_client.get(f"{self.url}/getUpdates")
        r = []
        if status != 200:
            return r
        body = orjson.loads(body)
        if not body["ok"]:
            return r
        for u in body["result"]:
            if "channel_post" in u:
                message = u["channel_post"]
                # Log Action
                r.append(
                    TTChange(
                        document_id=str(message["reply_to_message"]["message_id"]),
                        timestamp=datetime.datetime.fromtimestamp(message["date"]),
                        user="telegram",
                        action=TTAction.LOG,
                        change_id=str(u["update_id"]),
                        message=message["text"],
                    )
                )
            elif "callback_query" in u:
                message = u["callback_query"]
                try:
                    action = TTAction(message["data"])
                except ValueError:
                    self.logger.warning("Unknown Action: %s", message["data"])
                    continue
                # Action Command
                r.append(
                    TTChange(
                        document_id=str(message["message"]["message_id"]),
                        # user=message["from"]["username"],
                        user=str(message["from"]["id"]),
                        action=action,
                        change_id=str(u["update_id"]),
                    )
                )
        return r

    def get_tt(self, tt_id: str) -> Optional[TTInfo]:
        """
        getUpdates
        :param tt_id:
        :return:
        """
