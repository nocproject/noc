# ----------------------------------------------------------------------
# ClickHouse connection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
from typing import overload, Literal, Any
from urllib.parse import quote as urllib_quote

# NOC modules
from noc.core.http.sync import HttpClient
from noc.config import config
from .error import ClickhouseError


class ClickhouseClient:
    DEFAULT_PORT = 8123

    def __init__(
        self, host: str | None = None, port: int | None = None, read_only: bool = True
    ) -> None:
        self.read_only = read_only
        if read_only:
            self.user = config.clickhouse.ro_user
            self.password = config.clickhouse.ro_password or ""
        else:
            self.user = config.clickhouse.rw_user
            self.password = config.clickhouse.rw_password or ""
        if host:
            self.addresses = [f"{host}:{port or self.DEFAULT_PORT}"]
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

    @overload
    def execute(
        self,
        sql: str | None = None,
        args: list[str] | None = None,
        nodb: bool = False,
        post: str | None = None,
        extra: list[tuple[str, str]] | None = None,
        return_raw: Literal[False] = False,
    ) -> list[list[str]]: ...

    @overload
    def execute(
        self,
        sql: str | None = None,
        args: list[str] | None = None,
        nodb: bool = False,
        post: str | None = None,
        extra: list[tuple[str, str]] | None = None,
        return_raw: Literal[True] = True,
    ) -> bytes: ...

    def execute(
        self,
        sql: str | None = None,
        args: list[str] | None = None,
        nodb: bool = False,
        post: str | None = None,
        extra: list[tuple[str, str]] | None = None,
        return_raw: bool = False,
    ) -> list[list[str]] | bytes:
        """
        Execute query.

        Args:
            sql: Query string
            args: Query arguments
            nodb: Not set config database to request
            post: Request body
            extra: Extra params to query
            return_raw: Return raw binary result

        Returns:
            List of rows: When return_raw is False.
            binary result: When return_raw is True.
        """

        def q(v: Any) -> str:
            # @todo: quote dates
            if isinstance(v, str):
                v = v.replace("\\", "\\\\").replace("'", "\\'")
                return f"'{v}'"
            return str(v)

        qs: list[str] = []
        if not nodb:
            qs.append(f"database={config.clickhouse.db}")
        if extra:
            qs.extend(f"{k}={v}" for k, v in extra)
        if sql:
            if args:
                sql = sql % tuple(q(v) for v in args)
            if post:
                x = urllib_quote(sql.encode("utf8"))
                qs.append(f"query={x}")
            else:
                post = sql
        addr = random.choice(self.addresses)
        q_args = "&".join(qs)
        url = f"http://{addr}/?{q_args}"
        code, _headers, body = self.http_client.post(url, post.encode())
        if code != 200:
            msg = f"{code}: {body}"
            raise ClickhouseError(msg)
        if return_raw:
            return body
        return [row.decode().split("\t") for row in body.splitlines()]

    def ensure_db(self, db_name: str | None = None):
        self.execute(
            post=f"CREATE DATABASE IF NOT EXISTS {db_name or config.clickhouse.db};", nodb=True
        )

    def has_table(self, name: str, is_view: bool = False) -> bool:
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
        return bool(r and r[0][0] == "1")

    def rename_table(self, from_table: str, to_table: str) -> None:
        """
        Rename table `from_table` to `to_table`.

        Args:
            from_table:
            to_table:
        """
        self.execute(post=f"RENAME TABLE `{from_table}` TO `{to_table}`;")


def connection(
    host: str | None = None, port: int | None = None, read_only: bool = True
) -> ClickhouseClient:
    return ClickhouseClient(host=host, port=port, read_only=read_only)
