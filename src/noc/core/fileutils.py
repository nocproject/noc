# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import tempfile
import tarfile
import gzip
import shutil
from io import BytesIO

# NOC modules
from noc.core.version import version
from noc.core.comp import smart_text


def safe_rewrite(path, text, mode=None):
    """
    Create new file filled with "text" safely
    """
    text = smart_text(text)
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d)
    b = os.path.basename(path)
    h, p = tempfile.mkstemp(suffix=".tmp", prefix=b, dir=d)
    f = os.fdopen(h, "w")
    f.write(text)
    f.flush()
    f.close()
    if os.path.exists(path):
        os.unlink(path)
    os.link(p, path)
    os.unlink(p)
    if mode:
        os.chmod(path, mode)


def write_tempfile(text):
    """
    Create temporary file, write content and return path
    """
    h, p = tempfile.mkstemp()
    f = os.fdopen(h, "w")
    f.write(text)
    f.close()
    return p


class temporary_file:
    """
    Temporary file context manager.
    Writes data to temporary file an returns path.
    Unlinks temporary file on exit
    USAGE:
         with temporary_file("line1\nline2") as p:
             subprocess.Popen(["wc","-l",p])
    """

    def __init__(self, text="") -> None:
        self.text = text

    def __enter__(self):
        self.p = write_tempfile(self.text)
        return self.p

    def __exit__(self, type, value, tb):
        os.unlink(self.p)


def urlopen(url, auto_deflate=False):
    """
    urlopen wrapper
    """
    from urllib.request import urlopen, Request
    from noc.core.http.proxy import setup_urllib_proxies

    setup_urllib_proxies()

    if url.startswith("http://") or url.startswith("https://"):
        r = Request(url, headers={"User-Agent": f"NOC/{version.version.strip()}"})
    else:
        r = url
    if auto_deflate and url.endswith(".gz"):
        u = urlopen(r)
        f = BytesIO(u.read())
        return gzip.GzipFile(fileobj=f)
    return urlopen(r)


def iter_open(path):
    """
    Generator yielding file-like objects from path
    :return:
    """
    if path.endswith("tar.gz") or path.endswith("tgz"):
        tf = tarfile.open(path, "r:gz")
        for name in tf:
            f = tf.extractfile(name)
            yield f
        tf.close()
    elif path.endswith("tar.bz2") or path.endswith("tbz"):
        tf = tarfile.open(path, "r:bz")
        yield from tf
        tf.close()
    elif path.endswith(".gz"):
        f = gzip.open(path, "r")
        yield f
        f.close()
    else:
        f = open(path)
        yield f
        f.close()


def make_persistent(path, tmp_suffix=".tmp"):
    """
    Make file persistent removing `tmp_suffix` suffix

    :param path: File path
    :return: True if file has been moved, false otherwise
    """
    if not path.endswith(tmp_suffix):
        return False
    shutil.move(path, path[: -len(tmp_suffix)])
