# ----------------------------------------------------------------------
# Compressor tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import io

# NOC modules
from noc.core.compressor.loader import loader
from noc.core.compressor.base import BaseCompressor
from noc.core.fileutils import temporary_file

SAMPLE = ["Lorem ", "ipsum\n", "dolor ", "sit ", "amet"]
RESULT = "Lorem ipsum\ndolor sit amet"


def test_base_open():
    with temporary_file() as path, pytest.raises(NotImplementedError):
        BaseCompressor(path).open()


def test_base_close():
    with temporary_file() as path, pytest.raises(NotImplementedError):
        BaseCompressor(path).close()


@pytest.mark.parametrize("fmt", loader.iter_classes())
def test_file_instance(fmt):
    comp_cls = loader.get_class(fmt)
    with temporary_file() as path, comp_cls(path, mode="w") as f:
        assert isinstance(f, io.TextIOWrapper)


@pytest.mark.parametrize("fmt", loader.iter_classes())
def test_ext(fmt):
    comp_cls = loader.get_class(fmt)
    assert comp_cls.ext is not None
    if comp_cls.ext:
        assert comp_cls.ext.startswith(".")


@pytest.mark.parametrize("fmt", loader.iter_classes())
def test_compressor(fmt):
    comp_cls = loader.get_class(fmt)
    with temporary_file() as path:
        # Write samples
        with comp_cls(path, mode="w") as f:
            for sample in SAMPLE:
                f.write(sample)
        # Read result at once
        with comp_cls(path, mode="r") as f:
            data = f.read()
        assert isinstance(data, str)
        assert data == RESULT
        # Read result by lines
        with comp_cls(path, mode="r") as f:
            lines = list(f)
        assert len(lines) == 2
        assert "".join(lines) == RESULT
