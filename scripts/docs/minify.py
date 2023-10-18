# ---------------------------------------------------------------------
# Minify docs
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path
import os
import stat
from multiprocessing.pool import ThreadPool

# Third-party modules
import minify_html

DOCS = Path("build", "docs")
MB = float(1 << 20)
INDEX_HTML = DOCS / "index.html"
INDEX_HTML_RU = DOCS / "ru" / "index.html"


def total_size() -> int:
    """
    Calculate total size used by docs
    """
    size = 0
    for root, _, files in os.walk(DOCS):
        for fn in files:
            size += os.stat(os.path.join(root, fn))[stat.ST_SIZE]
    return size


def remove_duplicated_h1(data: str) -> str:
    """
    Clean up index.html
    """
    return data.replace("<h1>Home</h1>", "")


def preprocess(path: Path, data: str) -> str:
    """
    Preprocess raw HTML and return the result.

    Args:
        path: File path
        data: File contents
    """
    if path in (INDEX_HTML, INDEX_HTML_RU):
        data = remove_duplicated_h1(data)
    return data


def minify(path: Path) -> None:
    """
    Minify single file
    """
    # Read
    with open(path) as fp:
        r = preprocess(path, fp.read())
        r = minify_html.minify(r)
    # Write
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as fp:
        fp.write(r)
    # Substitute
    os.replace(tmp, path)


def compress() -> None:
    """
    Compress docs HTML
    """
    with ThreadPool() as pool:
        pool.map(minify, DOCS.rglob("*.html"))


def clean_summary():
    """
    Remove __SUMMARY__ files
    """
    for path in DOCS.rglob("__SUMMARY__"):
        os.unlink(path)


def main() -> None:
    """
    Main function.
    """
    print("# Compressing docs")
    size_before = total_size()
    print(f"Docs size: {float(size_before)/MB:.2f}Mb")
    compress()
    clean_summary()
    size_after = total_size()
    ratio = float(size_before) / float(size_after)
    print(f"Compressed result: {float(size_after)/MB:.2f}Mb (Ratio: {ratio:.2f})")


if __name__ == "__main__":
    main()
