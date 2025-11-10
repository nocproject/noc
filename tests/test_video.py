# ----------------------------------------------------------------------
# Test noc.core.video
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.video.resolution import VideoResolution, get_resolution
from noc.core.video.codecs import H264Profile, get_h264_profile_by_id, get_h264_profile_by_name


@pytest.mark.parametrize(
    ("name", "width", "height", "interlace"),
    [
        ("NTSC", 720, 480, True),
        ("480i", 720, 480, True),
        ("PAL", 720, 576, True),
        ("576i", 720, 576, True),
        ("VGA", 640, 480, False),
        ("480p", 720, 480, False),
        ("576p", 720, 576, False),
        ("720p", 1280, 720, False),
        ("1080i", 1920, 1080, True),
        ("1080p", 1920, 1080, False),
        ("4K", 3840, 2160, False),
        ("8K", 7680, 4320, False),
    ],
)
def test_video_resolution(name, width, height, interlace):
    res = get_resolution(name)
    assert res
    assert isinstance(res, VideoResolution)
    assert res.width == width, "Width mismatch"
    assert res.height == height, "Height mismatch"
    assert res.interlace is interlace, "Interlace mismatch"


def test_unknown_resolution():
    assert get_resolution("unknown") is None


@pytest.mark.parametrize(
    ("id", "constraint", "name"),
    [
        (66, 1, "CBP"),
        (66, None, "BP"),
        (88, None, "XP"),
        (77, None, "MP"),
        (100, None, "HiP"),
        (100, 4, "PHiP"),
        (100, 5, "CHiP"),
        (110, None, "Hi10P"),
        (122, None, "Hi422P"),
    ],
)
def test_get_h264_profile_by_name(id, constraint, name):
    profile = get_h264_profile_by_name(name)
    assert profile
    assert isinstance(profile, H264Profile)
    assert profile.name == name
    assert profile.id == id
    assert profile.constraint == constraint


@pytest.mark.parametrize(
    ("id", "constraint", "name"),
    [
        (66, 1, "CBP"),
        (66, None, "BP"),
        (88, None, "XP"),
        (77, None, "MP"),
        (100, None, "HiP"),
        (100, 4, "PHiP"),
        (100, 5, "CHiP"),
        (110, None, "Hi10P"),
        (122, None, "Hi422P"),
    ],
)
def test_get_h264_profile_by_id(id, constraint, name):
    profile = get_h264_profile_by_id(id, constraint)
    assert profile
    assert isinstance(profile, H264Profile)
    assert profile.name == name
    assert profile.id == id
    assert profile.constraint == constraint
