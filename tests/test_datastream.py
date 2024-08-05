# ----------------------------------------------------------------------
# noc.core.datastream test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
import threading

# Third-party modules
import pytest
import orjson
import bson

# NOC modules
from noc.core.datastream.base import DataStream
from noc.core.perf import metrics
from noc.core.datastream.loader import loader


class ExampleDataStream(DataStream):
    name = "example"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        return {"id": id, "name": "Item #%s" % id}


class NoEvenDatastream(DataStream):
    name = "noeven"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        if id % 2 == 0:
            raise KeyError
        return {"id": id, "name": "Item #%s" % id}

    @classmethod
    def get_meta(cls, data):
        return {"n": data["id"] / 2}


def test_datastream_base():
    with pytest.raises(NotImplementedError):
        DataStream.get_object(1)


@pytest.mark.dependency(name="datastream_collection_name")
def test_datastream_collection_name():
    assert ExampleDataStream.get_collection_name() == "ds_example"


@pytest.mark.dependency(name="datastream_collection", depends=["datastream_collection_name"])
def test_datastream_collection():
    ExampleDataStream.ensure_collection()
    # Test collection exists
    coll = ExampleDataStream.get_collection()
    assert "ds_example" in coll.database.list_collection_names()
    # Test collection indexes
    ii = coll.index_information()
    assert "change_id_1" in ii
    assert ii["change_id_1"].get("unique")


@pytest.mark.dependency(name="datastream_hash")
def test_datastream_hash():
    data = {"id": 1, "name": "test"}
    assert ExampleDataStream.get_hash(data) == "5757d197ae2f024e"


@pytest.fixture(params=list(range(1, 11)))
def ds_index(request):
    return request.param


@pytest.mark.dependency(
    name="datastream_update", depends=["datastream_hash", "datastream_collection"]
)
def test_datastream_update(ds_index):
    coll = ExampleDataStream.get_collection()
    # Generate update
    m_u = metrics["ds_example_updated"].value
    m_c = metrics["ds_example_changed"].value
    ExampleDataStream.update_object(ds_index)
    assert metrics["ds_example_updated"].value == m_u + 1
    assert metrics["ds_example_changed"].value == m_c + 1
    # Check document is exists in collection
    doc = coll.find_one({"_id": ds_index})
    assert doc is not None
    assert "hash" in doc
    assert "data" in doc
    assert "change_id" in doc
    data = orjson.loads(doc["data"])
    assert "id" in data
    assert "name" in data
    assert data["name"] == "Item #%s" % ds_index
    assert "change_id" in data
    assert data["change_id"] == str(doc["change_id"])
    change_id = doc["change_id"]
    # Try to update once mode
    m_u = metrics["ds_example_updated"].value
    m_c = metrics["ds_example_changed"].value
    ExampleDataStream.update_object(ds_index)
    assert metrics["ds_example_updated"].value == m_u + 1
    assert metrics["ds_example_changed"].value == m_c
    # Check document is still exists
    doc = coll.find_one({"_id": ds_index})
    assert doc is not None
    # Check document is not changed
    assert doc["change_id"] == change_id


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_total():
    assert ExampleDataStream.get_total() == 10


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_iter_data_limit():
    seen = set()
    for id, change_id, data in ExampleDataStream.iter_data(limit=3):
        assert id not in seen
        seen.add(id)
    assert seen == {1, 2, 3}


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_iter_data():
    seen = set()
    last_change = None
    for id, change_id, data in ExampleDataStream.iter_data():
        assert id not in seen
        seen.add(id)
        if last_change:
            assert last_change < change_id
        last_change = change_id
    assert seen == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_iter_data_id1():
    seen = set()
    for id, change_id, data in ExampleDataStream.iter_data(filters=["id(3)"]):
        assert id not in seen
        seen.add(id)
    assert seen == {3}


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_iter_data_id2():
    seen = set()
    for id, change_id, data in ExampleDataStream.iter_data(filters=["id(3,7)"]):
        assert id not in seen
        seen.add(id)
    assert seen == {3, 7}


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_iter_data_id_type_check():
    with pytest.raises(ValueError):
        next(ExampleDataStream.iter_data(filters=3))
    with pytest.raises(ValueError):
        next(ExampleDataStream.iter_data(change_id=3))
    with pytest.raises(ValueError):
        next(ExampleDataStream.iter_data(change_id="3"))


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_iter_data_chunked():
    seen = set()
    last_change = None
    # First 3
    for id, change_id, data in ExampleDataStream.iter_data(limit=3):
        last_change = change_id
        assert id not in seen
        seen.add(id)
    assert seen == {1, 2, 3}
    # Next 3
    for id, change_id, data in ExampleDataStream.iter_data(change_id=last_change, limit=3):
        last_change = change_id
        assert id not in seen
        seen.add(id)
    assert seen == {1, 2, 3, 4, 5, 6}
    # Next 3
    for id, change_id, data in ExampleDataStream.iter_data(change_id=last_change, limit=3):
        last_change = change_id
        assert id not in seen
        seen.add(id)
    assert seen == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    # Last one
    for id, change_id, data in ExampleDataStream.iter_data(change_id=last_change, limit=3):
        last_change = change_id
        assert id not in seen
        seen.add(id)
    assert seen == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    # Nothing more
    assert list(ExampleDataStream.iter_data(change_id=last_change, limit=3)) == []


@pytest.mark.dependency(depends=["datastream_update"])
def test_datastream_key_error(ds_index):
    coll = NoEvenDatastream.get_collection()
    NoEvenDatastream.update_object(ds_index)
    doc = coll.find_one({"_id": ds_index})
    assert doc
    assert "data" in doc
    if ds_index % 2 == 0:
        assert "$deleted" in doc["data"]
    else:
        assert "$deleted" not in doc["data"]
        assert "meta" in doc
        assert doc["meta"]["n"][0] == ds_index / 2


def test_datastream_delete_object():
    class DeleteDataStream(ExampleDataStream):
        name = "delete"

    coll = DeleteDataStream.get_collection()
    DeleteDataStream.ensure_collection()
    DeleteDataStream.update_object(1)
    doc = coll.find_one({"_id": 1})
    assert doc
    assert "data" in doc
    assert "$deleted" not in doc["data"]
    # Delete
    DeleteDataStream.delete_object(1)
    doc = coll.find_one({"_id": 1})
    assert doc
    assert "data" in doc
    assert "$deleted" in doc["data"]


def test_datastream_clean_id():
    assert ExampleDataStream.clean_id(1) == 1
    assert ExampleDataStream.clean_id("1") == 1


def test_datastream_clean_id_int():
    class DS(DataStream):
        clean_id = DataStream.clean_id_int

    assert DS.clean_id(1) == 1
    assert DS.clean_id("1") == 1
    with pytest.raises(ValueError):
        DS.clean_id("z")


@pytest.fixture(params=list(loader))
def datastream_name(request):
    return request.param


def test_loader(datastream_name):
    ds = loader[datastream_name]
    assert ds is not None
    assert issubclass(ds, DataStream)
    assert ds.name == datastream_name


def test_loader_invalid_name():
    ds = loader["aaa..bbbb"]
    assert ds is None


def test_loader_error():
    ds = loader["invalid"]
    assert ds is None


def test_loader_contains(datastream_name):
    assert datastream_name in loader


def test_wait():
    class WaitDS(DataStream):
        name = "wait"

        @classmethod
        def get_object(cls, id):
            return {"id": id}

    TIMEOUT = 0.1

    def writer():
        # Wait until main thread is ready
        event.wait()
        time.sleep(TIMEOUT)
        WaitDS.update_object(2)

    # Insert first object
    WaitDS.ensure_collection()
    WaitDS.update_object(1)
    # Start writer thread
    event = threading.Event()
    thread = threading.Thread(target=writer, name="test_wait-writer")
    thread.daemon = True
    thread.start()
    # Ensure WaitDS contains only one item
    assert WaitDS.get_total() == 1
    # Allow writer thread to start
    event.set()
    # Hang until writer thread inserts new object
    t0 = time.time()
    WaitDS.wait()
    dt = time.time() - t0
    # Cleanup writer thread
    thread.join()
    # We should be waiting more, than TIMEOUT
    assert dt > TIMEOUT
    # We must have second object
    assert WaitDS.get_total() == 2


def test_clean_changeid():
    oid = bson.ObjectId()
    # ObjectId left unchanged
    assert DataStream.clean_change_id(oid) == oid
    # string converted to object id
    assert DataStream.clean_change_id(str(oid)) == oid
    # date
    oid = DataStream.clean_change_id("2018-07-04")
    assert oid.generation_time.strftime("%Y-%m-%d") == "2018-07-04"
    # datetime
    oid = DataStream.clean_change_id("2018-07-04T09:25:51")
    assert oid.generation_time.strftime("%Y-%m-%dT%H:%M:%S") == "2018-07-04T09:25:51"
    #
    with pytest.raises(ValueError):
        DataStream.clean_change_id("9999-99-99")


def test_parse_filter():
    assert DataStream._parse_filter("id(1)") == ["id", "1"]
    assert DataStream._parse_filter("id(1,2)") == ["id", "1", "2"]
    assert DataStream._parse_filter("id(1,2,  3   )") == ["id", "1", "2", "3"]
    with pytest.raises(ValueError):
        DataStream._parse_filter(1)
    with pytest.raises(ValueError):
        DataStream._parse_filter("id")
    with pytest.raises(ValueError):
        DataStream._parse_filter("id(")


def test_filter_id():
    assert DataStream.filter_id(10) == {"_id": 10}
    assert DataStream.filter_id(10, 11) == {"_id": {"$in": [10, 11]}}


def test_filter_shard():
    assert DataStream.filter_shard(1, 3) == {"_id": {"$mod": [3, 1]}}
    assert DataStream.filter_shard("1", "3") == {"_id": {"$mod": [3, 1]}}


def test_compile_filters():
    assert DataStream.compile_filters(["id(1)"]) == {"_id": "1"}
    assert DataStream.compile_filters(["id(1,2)"]) == {"_id": {"$in": ["1", "2"]}}
    with pytest.raises(ValueError):
        assert DataStream.compile_filters("id(1)")
    with pytest.raises(ValueError):
        assert DataStream.compile_filters(["id(1)", 1])
    with pytest.raises(ValueError):
        DataStream.compile_filters(["unknown(1)"])
