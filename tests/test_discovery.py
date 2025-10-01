# ----------------------------------------------------------------------
# Discovery test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os.path
from collections import defaultdict

# Third-party modules
import pytest
from fs import open_fs
import yaml
import cachetools

# NOC modules
from noc.config import config
from noc.core.scheduler.job import Job
from noc.core.scheduler.scheduler import Scheduler
from noc.core.script.scheme import BEEF
from noc.core.script.loader import loader
from noc.core.script.beef import Beef
from noc.main.models.pool import Pool
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.profile import Profile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobject import ManagedObject
from noc.services.discovery.jobs.box.job import BoxDiscoveryJob
from noc.inv.models.discoveryid import DiscoveryID

_root_ad_cache = {}
_root_segment_cache = {}
_ad_cache = {}
_segmentprofile_cache = {}
_segment_cache = {}
_pool_cache = {}
_profile_cache = {}
_managedobjectprofile_cache = {}
_service_cache = {}
_configs = {}  # mo -> config


class ServiceStub(object):
    def __init__(self, pool):
        self.pool = pool
        self.metrics = defaultdict(list)
        self.service_id = "stub"
        self.address = "127.0.0.1"
        self.port = 0

    def register_metrics(self, table, data):
        self.metrics[table] += data


class BeefCallWrapper(object):
    def __init__(self, obj, name):
        self.name = name
        self.object = obj

    def __call__(self, **kwargs):
        script_name = "%s.%s" % (self.object.profile.name, self.name)
        scls = loader.get_script(script_name)
        # Build credentials
        credentials = {
            "address": self.object.address,
            "cli_protocol": "beef",
            "beef_storage_url": self.object._beef_storage,
            "beef_path": self.object._beef_path,
            "access-preference": "CS",
            "snmp_ro": "public",
        }
        # Build version
        if self.object.vendor and self.object.platform and self.object.version:
            version = {
                "vendor": self.object.vendor.code,
                "platform": self.object.platform.name,
                "version": self.object.version.version,
            }
            if self.object.software_image:
                version["image"] = self.object.software_image
        else:
            version = None
        scr = scls(
            service=get_service(self.object.pool.name),
            credentials=credentials,
            capabilities=self.object.get_caps(),
            version=version,
            timeout=3600,
            name=script_name,
            args=kwargs,
        )
        return scr.run()


def get_discovery_configs():
    r = []
    paths = config.tests.beef_paths or []
    for n, url in enumerate(paths):
        pool_name = "DP%04d" % (n + 1)
        fs = open_fs(url)
        for m, path in enumerate(fs.walk.files(filter=["test-discovery.yml"])):
            data = yaml.safe_load(fs.readbytes(path))
            name = os.path.basename(os.path.dirname(path))
            m = m + 1
            address = "10.%d.%d.%d" % ((m >> 16) & 0xFF, (m >> 8) & 0xFF, m & 0xFF)
            beef_path = os.path.join(os.path.dirname(path), "beef.json.bz2")
            r += [(name, address, pool_name, url, beef_path, data)]
    return r


@cachetools.cached(_service_cache)
def get_service(pool):
    return ServiceStub(pool)


@cachetools.cached(_pool_cache)
def get_pool(name):
    pool = Pool(name=name)
    pool.save()
    return pool


@cachetools.cached(_root_ad_cache)
def get_root_ad():
    ad = AdministrativeDomain(name="Discovery Tests")
    ad.save()
    return ad


@cachetools.cached(_ad_cache)
def get_ad(name):
    ad = AdministrativeDomain(name=name, parent=get_root_ad())
    ad.save()
    return ad


@cachetools.cached(_segmentprofile_cache)
def get_segment_profile():
    nsp = NetworkSegmentProfile(name="discovery test")
    nsp.save()
    return nsp


@cachetools.cached(_root_segment_cache)
def get_root_segment():
    ns = NetworkSegment(name="Discovery Tests", profile=get_segment_profile())
    ns.save()
    return ns


@cachetools.cached(_segment_cache)
def get_segment(name):
    ns = NetworkSegment(name=name, parent=get_root_segment(), profile=get_segment_profile())
    ns.save()
    return ns


@cachetools.cached(_profile_cache)
def get_profile(name):
    return Profile.get_by_name(name)


@cachetools.cached(_managedobjectprofile_cache)
def get_managedobjectprofile():
    mop = ManagedObjectProfile(
        name="disovery tests",
        enable_box_discovery=True,
        enable_box_discovery_version=True,
        enable_box_discovery_caps=True,
        enable_box_discovery_id=True,
        enable_box_discovery_interface=True,
        cli_session_policy="D",  # Must be disabled, overrides BeefCaller
    )
    mop.save()
    return mop


def get_by_path(mo, path):
    """
    Return config value by path or None
    :param mo: Managed object
    :param path: dot-separated path
    :return: value or None
    """
    global _configs
    v = _configs[mo.id]
    for part in path.split("."):
        if part in v:
            v = v[part]
        else:
            return None
    return v


def get_discovery_object_name(x):
    if isinstance(x, tuple):
        return "%s:%s" % (x[2], x[0])
    return None


@pytest.fixture(scope="module", params=get_discovery_configs(), ids=get_discovery_object_name)
def discovery_object(request):
    global _configs
    name, address, pool_name, beef_storage_url, beef_path, data = request.param
    beef = Beef.load(beef_storage_url, beef_path)
    mo = ManagedObject(
        name=name,
        is_managed=True,
        administrative_domain=get_ad(pool_name),
        segment=get_segment(pool_name),
        pool=get_pool(pool_name),
        profile=get_profile(beef.box.profile),
        object_profile=get_managedobjectprofile(),
        scheme=BEEF,
        address=name,
    )
    mo.save()
    # Store beef path
    mo._beef_storage = beef_storage_url
    mo._beef_path = beef_path
    # Shortcut scripts to beef
    mo.set_scripts_caller(BeefCallWrapper)
    _configs[mo.id] = data
    return mo


# @todo: Прогнать profile check, проверить совпадение профииля
# @todo: Прогнать капсы, сверить ожидаемые


def run_job(jcls, mo, checks):
    scheduler = Scheduler("discovery", pool=mo.pool.name, service=get_service(mo.pool))
    job_args = {Job.ATTR_ID: "fakeid", Job.ATTR_KEY: mo.id, "_checks": checks}
    job = jcls(scheduler, job_args)
    # Inject beef managed object
    job.dereference()
    job.object = mo
    # Run job
    job.handler()
    assert not job.problems


def test_box_basic(discovery_object):
    run_job(BoxDiscoveryJob, discovery_object, ["version", "caps", "id", "interface"])


def test_version_vendor(discovery_object):
    expected = get_by_path(discovery_object, "checks.version.vendor")
    if not expected:
        pytest.skip("vendor is not expected")
    assert discovery_object.vendor
    assert discovery_object.vendor.code == expected


def test_version_platform(discovery_object):
    expected = get_by_path(discovery_object, "checks.version.platform")
    if not expected:
        pytest.skip("platform is not expected")
    assert discovery_object.platform
    assert discovery_object.platform.name == expected


def test_version_version(discovery_object):
    expected = get_by_path(discovery_object, "checks.version.version")
    if not expected:
        pytest.skip("version is not expected")
    assert discovery_object.version
    assert discovery_object.version.version == expected


def test_capabilities(discovery_object):
    xcaps = get_by_path(discovery_object, "checks.caps")
    if not xcaps:
        pytest.skip("caps are not expected")
    caps = discovery_object.get_caps()
    for expected in xcaps:
        assert expected["name"] in caps
        assert caps[expected["name"]] == expected["value"]


def test_id_hostname(discovery_object):
    expected = get_by_path(discovery_object, "checks.id.hostname")
    if not expected:
        pytest.skip("hostname is not expected")
    d = DiscoveryID.objects.filter(object=discovery_object.id).first()
    assert d
    assert d.hostname == expected


def test_id_macs(discovery_object):
    xmacs = get_by_path(discovery_object, "checks.id.macs")
    if not xmacs:
        pytest.skip("macs are not expected")
    d = DiscoveryID.objects.filter(object=discovery_object.id).first()
    assert d
    for expected in xmacs:
        first = expected["first"]
        last = expected["last"]
        m = [x for x in d.chassis_mac if x.first_mac == first and x.last_mac == last]
        assert m
        mo = DiscoveryID.find_object(mac=first)
        assert mo
        assert mo.id == discovery_object.id
        mo = DiscoveryID.find_object(mac=last)
        assert mo
        assert mo.id == discovery_object.id
