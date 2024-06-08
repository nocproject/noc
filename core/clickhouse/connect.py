# ----------------------------------------------------------------------
# ClickHouse connection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
from typing import List, Union, Optional, Tuple
from urllib.parse import quote as urllib_quote

# NOC modules
from noc.core.http.sync_client import HttpClient
from noc.core.comp import smart_text, DEFAULT_ENCODING
from noc.config import config
from .error import ClickhouseError


class ClickhouseClient(object):
    def __init__(self, host=None, port=None, read_only=True):
        self.read_only = read_only
        if read_only:
            self.user = config.clickhouse.ro_user
            self.password = config.clickhouse.ro_password or ""
        else:
            self.user = config.clickhouse.rw_user
            self.password = config.clickhouse.rw_password or ""
        if host:
            self.addresses = ["%s:%s" % (host, port or 8123)]
        elif read_only:
            self.addresses = [str(x) for x in config.clickhouse.ro_addresses]
        else:
            self.addresses = [str(x) for x in config.clickhouse.rw_addresses]
        self.http_client = HttpClient(
            connect_timeout=config.clickhouse.connect_timeout,
            timeout=config.clickhouse.request_timeout,
            user=self.user,
            password=self.password,
        )

    def execute(
        self,
        sql: Optional[str] = None,
        args: Optional[List[str]] = None,
        nodb: bool = False,
        post: str = None,
        extra: List[Tuple[str, str]] = None,
        return_raw: bool = False,
    ) -> Union[List[str], str]:
        """

        :param sql: Query string
        :param args: Query arguments
        :param nodb: Not set config database to request
        :param post: Request body
        :param extra: Extra params to query
        :param return_raw: Return raw binary result
        :return:
        """

        def q(v):
            # @todo: quote dates
            if isinstance(v, str):
                return "'%s'" % (v.replace("\\", "\\\\").replace("'", "\\'"))
            else:
                return str(v)

        qs = []
        if not nodb:
            qs += ["database=%s" % config.clickhouse.db]
        if extra:
            qs += ["%s=%s" % (k, v) for k, v in extra]
        if sql:
            if args:
                sql = sql % tuple(q(v) for v in args)
            if post:
                qs += ["query=%s" % urllib_quote(sql.encode("utf8"))]
            else:
                post = sql
        url = "http://%s/?%s" % (random.choice(self.addresses), "&".join(qs))
        code, headers, body = self.http_client.post(url, post.encode(DEFAULT_ENCODING))
        if code != 200:
            raise ClickhouseError("%s: %s" % (code, body))
        if return_raw:
            return body
        return [smart_text(row).split("\t") for row in body.splitlines()]

    def ensure_db(self, db_name=None):
        self.execute(
            post=f"CREATE DATABASE IF NOT EXISTS {db_name or config.clickhouse.db};", nodb=True
        )

    def has_table(self, name, is_view=False):
        r = self.execute(
            f"""
            SELECT COUNT(*)
            FROM system.tables
            WHERE
              database=%s
              AND name = %s
              AND engine {"!=" if not is_view else "="} 'View'
        """,
            [config.clickhouse.db, name],
        )
        return r and r[0][0] == "1"

    def rename_table(self, from_table: str, to_table: str):
        """
        Rename table `from_table` to `to_table`
        :param from_table:
        :param to_table:
        :return:
        """
        self.execute(post=f"RENAME TABLE `{from_table}` TO `{to_table}`;")


def connection(host=None, port=None, read_only=True):
    return ClickhouseClient(host=host, port=port, read_only=read_only)
