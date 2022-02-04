# ---------------------------------------------------------------------
# RefBook Downloaders
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class BaseDownloader(object):
    """
    Downloader is a class performing download and parsing of refbook
    and returning a list of hashes (for RefBook.bulk_upload)
    """

    # Profile name
    name = None

    #
    # Abstract metrod returning a list of records
    # Each record is a hash with field name -> value mapping
    #
    @classmethod
    def download(cls, ref_book):
        return []
