# ----------------------------------------------------------------------
# Victoria Metrics Proto request
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from remote_pb2 import remote_pb2

_WRITEREQUEST = remote_pb2.DESCRIPTOR.message_types_by_name["WriteRequest"]

WriteRequest = _reflection.GeneratedProtocolMessageType(
    "WriteRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _WRITEREQUEST,
        "__module__": "remote_pb2",
        # @@protoc_insertion_point(class_scope:prometheus.WriteRequest)
    },
)
remote_pb2._sym_db.RegisterMessage(WriteRequest)
