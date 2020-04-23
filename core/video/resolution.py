# ----------------------------------------------------------------------
# Video resolution helpers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple

VideoResolution = namedtuple("VideoResolution", ["width", "height", "interlace"])

# SDTV
RES_480i = VideoResolution(width=720, height=480, interlace=True)
RES_576i = VideoResolution(width=720, height=576, interlace=True)

# EDTV
RES_480p = VideoResolution(width=720, height=480, interlace=False)
RES_576p = VideoResolution(width=720, height=576, interlace=False)

# HDTV
RES_720p = VideoResolution(width=1280, height=720, interlace=False)
RES_1080i = VideoResolution(width=1920, height=1080, interlace=True)
RES_1080p = VideoResolution(width=1920, height=1080, interlace=False)

# UHDTV
RES_4K = VideoResolution(width=3840, height=2160, interlace=False)
RES_8K = VideoResolution(width=7680, height=4320, interlace=False)

# Display
RES_QVGA = VideoResolution(width=320, height=240, interlace=False)
RES_VGA = VideoResolution(width=640, height=480, interlace=False)
RES_QUADVGA = VideoResolution(width=1280, height=960, interlace=False)
RES_SXGA = VideoResolution(width=1280, height=1024, interlace=False)

# Video conferencing standards
RES_SQIF = VideoResolution(width=128, height=96, interlace=False)
RES_QCIF = VideoResolution(width=176, height=144, interlace=False)
RES_CIF = VideoResolution(width=352, height=288, interlace=False)
RES_SIF = VideoResolution(width=352, height=240, interlace=False)
RES_4CIF = VideoResolution(width=704, height=576, interlace=False)
RES_16CIF = VideoResolution(width=1408, height=1152, interlace=False)

_RESOLUTIONS = {
    "ntsc": RES_480i,
    "480i": RES_480i,
    "pal": RES_576i,
    "576i": RES_576i,
    "480p": RES_480p,
    "vga": RES_VGA,
    "qvga": RES_QVGA,
    "quadvga": RES_QUADVGA,
    "sxga": RES_QUADVGA,
    "576p": RES_576p,
    "720p": RES_720p,
    "1080i": RES_1080i,
    "1080p": RES_1080p,
    "4k": RES_4K,
    "8k": RES_8K,
    "sqcif": RES_SQIF,
    "qcif": RES_QCIF,
    "cif": RES_CIF,
    "sif": RES_SIF,
    "4cif": RES_4CIF,
    "16cif": RES_16CIF,
}


def get_resolution(name):
    """
    Get VideoResolution for name alias

    :param name: Video Resolution name
    :return: VideoResolution instance or None
    """
    global _RESOLUTIONS

    return _RESOLUTIONS.get(name.lower())
