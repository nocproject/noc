# ----------------------------------------------------------------------
# Update checkers Job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from collections import defaultdict

# Third-party modules
import orjson

# NOC modules
from noc.core.checkers.base import CheckResult
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.error import ClickhouseError
from noc.core.scheduler.job import Job
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.service import Service
from noc.config import config


WAIT_DEFAULT_INTERVAL_SEC = 180
MIN_NEXT_SHIFT_SEC = 30
MAX_DEPTH_INTERVAL = config.scheduler.diagnostic_check_depth_interval

SQL = """
select managed_object, service, max(last_ts), groupArray((check_name, c_status, args, remote_system,
 map('port', toString(port), 'address', address, 'skipped', toString(skipped), 'ttl', toString(ttl), 'data', data,
 'error', error, 'error_code', error_code,
 'is_available', toString(is_available), 'is_access', toString(is_access)))
 ) as checks
 from (
  select check_name, argMax(status, ts) as c_status, args, argMax(ts, ts) as last_ts,
   argMax(port, ts) as port, IPv4NumToString(argMax(address, ts)) as address,
   argMax(skipped, ts) as skipped, argMax(ttl, ts) as ttl, argMax(data, ts) as data,
   argMax(error, ts) as error, argMax(error_code, ts) as error_code,
   argMax(is_available, ts) as is_available, argMax(is_access, ts) as is_access,
   remote_system, managed_object, service
  from noc.checkhistory c
  where source <> 'discovery' and date > %s
  group by check_name, args, remote_system, managed_object, service
 )
 where last_ts > %s
 group by managed_object, service
 FORMAT JSON
"""


class UpdateCheckersJob(PeriodicJob):
    """Update checkers from History"""

    def handler(self, **kwargs):
        # LIMIT BY 3 checks and calculate diff
        depth: datetime.datetime = datetime.datetime.now() - datetime.timedelta(
            seconds=MAX_DEPTH_INTERVAL
        )
        last_success = self.attrs.get(Job.ATTR_LAST_SUCCESS, depth).replace(microsecond=0)
        self.logger.info("Start update objects checks from history from: %s", last_success)
        ch = connection()
        try:
            data = orjson.loads(
                ch.execute(
                    SQL,
                    return_raw=True,
                    args=[depth.date().isoformat(), last_success.isoformat(sep=" ")],
                ),
            )
        except ClickhouseError as e:
            self.logger.info("Error when getting data from Clickhouse: %s", e)
            return
        if not data.get("data"):
            return
        mos_checks = defaultdict(list)
        services_checks = defaultdict(list)
        common_checks = []
        processed = 0
        for d in data["data"]:
            processed += 1
            mo = int(d.get("managed_object", 0))
            svc = int(d.get("service", 0))
            for check, status, args, rs, data in d["checks"]:
                rs = int(rs)
                if rs:
                    rs = RemoteSystem.get_by_bi_id(rs)
                    if rs:
                        rs = rs.name
                c = CheckResult.from_history(check, status, args, rs, data)
                if mo:
                    mos_checks[mo].append(c)
                if svc:
                    services_checks[svc].append(c)
                if not mo and not svc:
                    common_checks.append(c)
        self.logger.info(
            "Processed checks items: %s. Objects: %d, Service: %d, Common: %d",
            processed,
            len(mos_checks),
            len(services_checks),
            len(common_checks),
        )
        print(mos_checks, services_checks)
        if services_checks:
            for svc in Service.objects.filter(bi_id__in=services_checks):
                svc.diagnostic.update_checks(services_checks[svc.bi_id])
        if mos_checks:
            for mo in ManagedObject.objects.filter(bi_id__in=mos_checks):
                mo.diagnostic.update_checks(mos_checks[mo.bi_id])

    def can_run(self):
        return True

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return WAIT_DEFAULT_INTERVAL_SEC
