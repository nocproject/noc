# ----------------------------------------------------------------------
# Reporter testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import polars as pl

# NOC modules
from noc.core.reporter.report import Band, ROOT_BAND, DataSet


def test_get_children():
    root = create_band_data()

    band1 = root.get_child_by_name("Band1")
    band3 = root.get_child_by_name("Band3")

    assert band1 is not None
    assert band3 is not None

    assert band1.get_child_by_name("Band11") is not None
    assert band1.get_child_by_name("Band14") is not None


def test_find_band_recursively():
    root = create_band_data()

    f_root = root.find_band_recursively(ROOT_BAND)
    assert f_root is root

    band1 = root.find_band_recursively("Band1")
    band11 = root.find_band_recursively("Band11")
    assert band1 is not None
    assert band11 is not None

    assert "Band1.Band11" == band11.full_name


def test_get_band_data():
    root = create_band_data()

    band11 = root.find_band_recursively("Band11")
    d_band = root.get_data_band()
    assert band11 is d_band


def create_band_data():
    root = Band(ROOT_BAND)

    for b1 in range(1, 4):
        bd = Band(f"Band{b1}", root)
        root.add_child(bd)
        for b2 in range(1, 5):
            cb = Band(f"Band{b1}{b2}", bd)
            bd.add_child(cb)
            if cb.name == "Band11":
                cb.add_dataset(DataSet(data=pl.DataFrame([{"col1": 1, "col2": 2}]), name=cb.name))
    return root
