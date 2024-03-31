# ---------------------------------------------------------------------
# CSV-file downloader
# First line is a field names
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import csv
import gzip
from io import StringIO

# NOC modules
from noc.core.http.sync_client import HttpClient
from noc.core.comp import smart_text
from .base import BaseDownloader


class CsvUrlDownloader(BaseDownloader):
    """
    Download reference book from CSV file
    First line of CSV file is field names
    """

    name = "url_csv"

    @classmethod
    def download(cls, ref_book):
        out = []
        # Fetch data into StringIO wrapper
        url = ref_book.download_url
        url = url.replace("http://update.nocproject.org/db/", "https://cdn.nocproject.org/refbook/")
        with HttpClient(
            timeout=60,
            allow_proxy=True,
            validate_cert=False,
        ) as client:
            code, headers, body = client.get(url)
            if code != 200:
                raise IOError("Invalid HTTP response: %s" % code)

            data = StringIO(body)
            # Wrap GzipFile for gzipped content
            if ref_book.download_url.endswith(".gz"):
                data = gzip.GzipFile(fileobj=data)
            # Iterate through CSV
            reader = csv.reader(data)
            header = {}
            for row in reader:
                if not row:
                    continue
                if not header:
                    # Read field names from first line
                    for i, h in enumerate(row):
                        header[i] = smart_text(h, errors="ignore")
                    continue
                r = {}
                for i, v in enumerate(row):
                    r[header[i]] = smart_text(v, errors="ignore")
                out.append(r)
            return out
