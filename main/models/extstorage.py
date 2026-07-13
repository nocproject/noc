# ----------------------------------------------------------------------
# ExtStorage model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator
from pathlib import Path

# Third-party modules
import cachetools
from gufo.blob.sync import BlobBase, open_blob, BlobError
from mongoengine.document import Document
from mongoengine.fields import StringField
from bson import ObjectId

# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        ("sa.ManagedObjectProfile", "config_mirror_storage"),
        ("sa.ManagedObjectProfile", "beef_storage"),
        ("sa.ManagedObjectProfile", "config_download_storage"),
    ]
)
class ExtStorage(Document):
    meta = {"collection": "extstorages", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    url = StringField()
    description = StringField()
    type = StringField(
        choices=[
            ("config_mirror", "Config Mirror"),
            ("config_upload", "Config Upload"),
            ("beef", "Beef"),
            ("beef_test", "Beef Test"),
            ("beef_test_config", "Beef Test Config"),
        ]
    )

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    StorageErrors = (BlobError, KeyError)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: str | ObjectId) -> Optional["ExtStorage"]:
        return ExtStorage.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["ExtStorage"]:
        return ExtStorage.objects.filter(name=name).first()

    @classmethod
    def from_url(cls, url: str) -> BlobBase:
        """
        Open blob from url.

        Args:
            url: Blob URL

        Returns:
            Blob object

        Raises:
            StorageErrors: on any error
        """
        return open_blob(url)

    def get_storage(self) -> BlobBase:
        """
        Get Blob object.

        To be used in context managers like:

        ```python
        with my_storage.storage as blob:
            ...
        ```

        Returns:
            BlobBase subclass instance
        """
        return open_blob(self.url)

    def read_bytes(self, path: str) -> bytes:
        """
        Read bytes from path.

        Args:
            path: File path.

        Returns:
            Received bytes.

        Raises:
            StorageErrors: on error.
        """
        with self.get_storage() as blob:
            return blob[path]

    def write_bytes(self, path: str | Path, data: bytes) -> None:
        """
        Write data to storage.

        Args:
            path: File path.
            data: data to store.

        Raises:
            StorageErorrs on any error.
        """
        with self.get_storage() as blob:
            blob[str(path)] = data

    @classmethod
    def read_bytes_from_ref(cls, ref: str) -> bytes:
        """
        Read bytes from reference.

        Reference has a form of `<name>:<path>`. Where:

        - `name` - ExtStorage name.
        - `path` - Resource path inside the storage.

        Args:
            ref: Reference.

        Returns:
            Received bytes.

        Raises:
            StorageErorrs: On any error.
        """
        if ":" not in ref:
            msg = f"Invalid ref format: {ref}"
            raise BlobError(msg)
        storage_name, path = ref.split(":", 1)
        storage = cls.get_by_name(storage_name)
        if not storage:
            msg = f"Invalid storage: {storage_name}"
            raise BlobError(msg)
        return storage.read_bytes(path)

    @property
    def is_config_mirror(self):
        return self.type == "config_mirror"

    @property
    def is_beef(self):
        return self.type == "beef"

    @property
    def is_beef_test(self):
        return self.type == "beef_test"

    @property
    def is_beef_test_config(self):
        return self.type == "beef_test_config"
