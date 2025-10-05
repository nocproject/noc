# ----------------------------------------------------------------------
# Palette and color manipulation tools
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
from typing import Tuple

# Material 2014 color scheme from
# https://material.io/design/color/the-color-system.html#tools-for-picking-colors

# Color sets
RED50 = [
    "#FFEBEE",  # Red 50
    "#FFCDD2",  # 100
    "#EF9A9A",  # 200
    "#E57373",  # 300
    "#EF5350",  # 400
    "#F44336",  # 500
    "#E53935",  # 600
    "#D32F2F",  # 700
    "#C62828",  # 800
    "#B71C1C",  # 900
    "#FF8A80",  # A100
    "#FF5252",  # A200
    "#FF1744",  # A400
    "#D50000",  # A700
]

PINK50 = [
    "#FCE4EC",  # Pink 50
    "#F8BBD0",  # 100
    "#F48FB1",  # 200
    "#F06292",  # 300
    "#EC407A",  # 400
    "#E91E63",  # 500
    "#D81B60",  # 600
    "#C2185B",  # 700
    "#AD1457",  # 800
    "#880E4F",  # 900
    "#FF80AB",  # A100
    "#FF4081",  # A200
    "#F50057",  # A400
    "#C51162",  # A700
]

PURPLE50 = [
    "#F3E5F5",  # Purple 50
    "#E1BEE7",  # 100
    "#CE93D8",  # 200
    "#BA68C8",  # 300
    "#AB47BC",  # 400
    "#9C27B0",  # 500
    "#8E24AA",  # 600
    "#7B1FA2",  # 700
    "#6A1B9A",  # 800
    "#4A148C",  # 900
    "#EA80FC",  # A100
    "#E040FB",  # A200
    "#D500F9",  # A400
    "#AA00FF",  # A700
]

DEEP_PURPLE50 = [
    "#EDE7F6",  # Deep Purple 50
    "#D1C4E9",  # 100
    "#B39DDB",  # 200
    "#9575CD",  # 300
    "#7E57C2",  # 400
    "#673AB7",  # 500
    "#5E35B1",  # 600
    "#512DA8",  # 700
    "#4527A0",  # 800
    "#311B92",  # 900
    "#B388FF",  # A100
    "#7C4DFF",  # A200
    "#651FFF",  # A400
    "#6200EA",  # A700
]

INDIGO50 = [
    "#E8EAF6",  # Indigo 50
    "#C5CAE9",  # 100
    "#9FA8DA",  # 200
    "#7986CB",  # 300
    "#5C6BC0",  # 400
    "#3F51B5",  # 500
    "#3949AB",  # 600
    "#303F9F",  # 700
    "#283593",  # 800
    "#1A237E",  # 900
    "#8C9EFF",  # A100
    "#536DFE",  # A200
    "#3D5AFE",  # A400
    "#304FFE",  # A700
]

BLUE50 = [
    "#E3F2FD",  # Blue 50
    "#BBDEFB",  # 100
    "#90CAF9",  # 200
    "#64B5F6",  # 300
    "#42A5F5",  # 400
    "#2196F3",  # 500
    "#1E88E5",  # 600
    "#1976D2",  # 700
    "#1565C0",  # 800
    "#0D47A1",  # 900
    "#82B1FF",  # A100
    "#448AFF",  # A200
    "#2979FF",  # A400
    "#2962FF",  # A700
]

LIGHT_BLUE50 = [
    "#E1F5FE",  # Light Blue 50
    "#B3E5FC",  # 100
    "#81D4FA",  # 200
    "#4FC3F7",  # 300
    "#29B6F6",  # 400
    "#03A9F4",  # 500
    "#039BE5",  # 600
    "#0288D1",  # 700
    "#0277BD",  # 800
    "#01579B",  # 900
    "#80D8FF",  # A100
    "#40C4FF",  # A200
    "#00B0FF",  # A400
    "#0091EA",  # A700
]

CYAN50 = [
    "#E0F7FA",  # Cyan 50
    "#B2EBF2",  # 100
    "#80DEEA",  # 200
    "#4DD0E1",  # 300
    "#26C6DA",  # 400
    "#00BCD4",  # 500
    "#00ACC1",  # 600
    "#0097A7",  # 700
    "#00838F",  # 800
    "#006064",  # 900
    "#84FFFF",  # A100
    "#18FFFF",  # A200
    "#00E5FF",  # A400
    "#00B8D4",  # A700
]

TEAL50 = [
    "#E0F2F1",  # Teal 50
    "#B2DFDB",  # 100
    "#80CBC4",  # 200
    "#4DB6AC",  # 300
    "#26A69A",  # 400
    "#009688",  # 500
    "#00897B",  # 600
    "#00796B",  # 700
    "#00695C",  # 800
    "#004D40",  # 900
    "#A7FFEB",  # A100
    "#64FFDA",  # A200
    "#1DE9B6",  # A400
    "#00BFA5",  # A700
]

GREEN50 = [
    "#E8F5E9",  # Green 50
    "#C8E6C9",  # 100
    "#A5D6A7",  # 200
    "#81C784",  # 300
    "#66BB6A",  # 400
    "#4CAF50",  # 500
    "#43A047",  # 600
    "#388E3C",  # 700
    "#2E7D32",  # 800
    "#1B5E20",  # 900
    "#B9F6CA",  # A100
    "#69F0AE",  # A200
    "#00E676",  # A400
    "#00C853",  # A700
]

LIGHT_GREEN50 = [
    "#F1F8E9",  # Light Green 50
    "#DCEDC8",  # 100
    "#C5E1A5",  # 200
    "#AED581",  # 300
    "#9CCC65",  # 400
    "#8BC34A",  # 500
    "#7CB342",  # 600
    "#689F38",  # 700
    "#558B2F",  # 800
    "#33691E",  # 900
    "#CCFF90",  # A100
    "#B2FF59",  # A200
    "#76FF03",  # A400
    "#64DD17",  # A700
]

LIME50 = [
    "#F9FBE7",  # Lime 50
    "#F0F4C3",  # 100
    "#E6EE9C",  # 200
    "#DCE775",  # 300
    "#D4E157",  # 400
    "#CDDC39",  # 500
    "#C0CA33",  # 600
    "#AFB42B",  # 700
    "#9E9D24",  # 800
    "#827717",  # 900
    "#F4FF81",  # A100
    "#EEFF41",  # A200
    "#C6FF00",  # A400
    "#AEEA00",  # A700
]

YELLOW50 = [
    "#FFFDE7",  # Yellow 50
    "#FFF9C4",  # 100
    "#FFF59D",  # 200
    "#FFF176",  # 300
    "#FFEE58",  # 400
    "#FFEB3B",  # 500
    "#FDD835",  # 600
    "#FBC02D",  # 700
    "#F9A825",  # 800
    "#F57F17",  # 900
    "#FFFF8D",  # A100
    "#FFFF00",  # A200
    "#FFEA00",  # A400
    "#FFD600",  # A700
]

AMBER50 = [
    "#FFF8E1",  # Amber 50
    "#FFECB3",  # 100
    "#FFE082",  # 200
    "#FFD54F",  # 300
    "#FFCA28",  # 400
    "#FFC107",  # 500
    "#FFB300",  # 600
    "#FFA000",  # 700
    "#FF8F00",  # 800
    "#FF6F00",  # 900
    "#FFE57F",  # A100
    "#FFD740",  # A200
    "#FFC400",  # A400
    "#FFAB00",  # A700
]

ORANGE50 = [
    "#FFF3E0",  # Orange 50
    "#FFE0B2",  # 100
    "#FFCC80",  # 200
    "#FFB74D",  # 300
    "#FFA726",  # 400
    "#FF9800",  # 500
    "#FB8C00",  # 600
    "#F57C00",  # 700
    "#EF6C00",  # 800
    "#E65100",  # 900
    "#FFD180",  # A100
    "#FFAB40",  # A200
    "#FF9100",  # A400
    "#FF6D00",  # A700
]

DEEP_ORANGE50 = [
    "#FBE9E7",  # Deep Orange 50
    "#FFCCBC",  # 100
    "#FFAB91",  # 200
    "#FF8A65",  # 300
    "#FF7043",  # 400
    "#FF5722",  # 500
    "#F4511E",  # 600
    "#E64A19",  # 700
    "#D84315",  # 800
    "#BF360C",  # 900
    "#FF9E80",  # A100
    "#FF6E40",  # A200
    "#FF3D00",  # A400
    "#DD2C00",  # A700
]

BROWN50 = [
    "#EFEBE9",  # Brown 50
    "#D7CCC8",  # 100
    "#BCAAA4",  # 200
    "#A1887F",  # 300
    "#8D6E63",  # 400
    "#795548",  # 500
    "#6D4C41",  # 600
    "#5D4037",  # 700
    "#4E342E",  # 800
    "#3E2723",  # 900
]

GRAY50 = [
    "#FAFAFA",  # Gray 50
    "#F5F5F5",  # 100
    "#EEEEEE",  # 200
    "#E0E0E0",  # 300
    "#BDBDBD",  # 400
    "#9E9E9E",  # 500
    "#757575",  # 600
    "#616161",  # 700
    "#424242",  # 800
    "#212121",  # 900
]

BLUE_GRAY50 = [
    "#ECEFF1",  # Blue Gray 50
    "#CFD8DC",  # 100
    "#B0BEC5",  # 200
    "#90A4AE",  # 300
    "#78909C",  # 400
    "#607D8B",  # 500
    "#546E7A",  # 600
    "#455A64",  # 700
    "#37474F",  # 800
    "#263238",  # 900
]

BW = [
    "#000000",  # Black
    "#FFFFFF",  # White
]

FG = BW  # Foreground

COLOR_PALETTES = [
    RED50,
    PINK50,
    PURPLE50,
    DEEP_PURPLE50,
    INDIGO50,
    BLUE50,
    LIGHT_BLUE50,
    CYAN50,
    TEAL50,
    GREEN50,
    LIGHT_GREEN50,
    LIME50,
    YELLOW50,
    AMBER50,
    ORANGE50,
    DEEP_ORANGE50,
]

TONE_PALETTES = [
    BROWN50,
    GRAY50,
    BLUE_GRAY50,
]

ALL_PALETTES = [BW, *COLOR_PALETTES, *TONE_PALETTES]

AVATAR_COLORS = list(itertools.chain(*COLOR_PALETTES))
_AC_PRIME = 8191  # Prime number, 5th Mersenne prime


def get_avatar_bg_color(n: int) -> str:
    """
    Get persistent shuffled colors for avatars
    :param n: Positive number, usually user id
    :return:
    """
    # Wrap possibly too long number
    n = n % _AC_PRIME
    i = n * _AC_PRIME % len(AVATAR_COLORS)
    return AVATAR_COLORS[i]


def split_rgb(color: str) -> Tuple[int, int, int]:
    """
    Split color #RRGGBB to a tuple of (R, G, B)
    :param color:
    :return:
    """
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:], 16)


def get_fg_color(color: str) -> str:
    """
    Return contrast foreground color
    :param color:
    :return:
    """

    def distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]):
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

    bg_rgb = split_rgb(color)
    best_fg = FG[0]
    best_distance = distance(split_rgb(best_fg), bg_rgb)
    for fg in FG[1:]:
        dist = distance(split_rgb(fg), bg_rgb)
        if dist <= best_distance:
            continue
        best_fg = fg
        best_distance = dist
    return best_fg
