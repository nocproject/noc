# ----------------------------------------------------------------------
# Video Codecs Parameters
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python files
from collections import namedtuple

H264Profile = namedtuple("H264Profile", ["name", "id", "constraint"])

H264_PROFILES = [
    H264Profile("CBP", 66, 1),
    H264Profile("BP", 66, None),
    H264Profile("XP", 88, None),
    H264Profile("MP", 77, None),
    H264Profile("HiP", 100, None),
    H264Profile("PHiP", 100, 4),
    H264Profile("CHiP", 100, 5),
    H264Profile("Hi10P", 110, None),
    H264Profile("Hi422P", 122, None),
    H264Profile("Hi444PP", 244, None),
    H264Profile("High 10 Intra", 110, 3),
    H264Profile("High 4:2:2 Intra", 122, 3),
    H264Profile("High 4:4:4 Intra", 233, 3),
    H264Profile("CAVLC 4:4:4 Intra", 44, None),
]

_H264_PROFILE_BY_NAME = {p.name.lower(): p for p in H264_PROFILES}
_H264_PROFILE_BY_ID = {(p.id, p.constraint): p for p in H264_PROFILES}


def get_h264_profile_by_name(name):
    """
    Get H.264 profile by name

    :param name: Profile name
    :return: H264Profile instance or None
    """
    global _H264_PROFILE_BY_NAME

    return _H264_PROFILE_BY_NAME.get(name.lower())


def get_h264_profile_by_id(id, constraint=None):
    """
    Get H.264 profile by name

    :param id: Profile id
    :param constraint: Constraint set id or None
    :return: H264Profile instance or None
    """
    global _H264_PROFILE_BY_ID

    return _H264_PROFILE_BY_ID.get((id, constraint))
