#!/usr/bin/python2.4
# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import service
from google.protobuf import service_reflection
from google.protobuf import descriptor_pb2
_ERRORCODE = descriptor.EnumDescriptor(
  name='ErrorCode',
  full_name='sae.ErrorCode',
  filename='ErrorCode',
  values=[
    descriptor.EnumValueDescriptor(
      name='ERR_OK', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ERR_INVALID_METHOD', index=1, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ERR_INVALID_TRANSACTION', index=2, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ERR_TRANSACTION_EXISTS', index=3, number=3,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ERR_UNKNOWN_ACTIVATOR', index=4, number=4,
      options=None,
      type=None),
  ],
  options=None,
)


_ACCESSSCHEME = descriptor.EnumDescriptor(
  name='AccessScheme',
  full_name='sae.AccessScheme',
  filename='AccessScheme',
  values=[
    descriptor.EnumValueDescriptor(
      name='TELNET', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SSH', index=1, number=1,
      options=None,
      type=None),
  ],
  options=None,
)


ERR_OK = 0
ERR_INVALID_METHOD = 1
ERR_INVALID_TRANSACTION = 2
ERR_TRANSACTION_EXISTS = 3
ERR_UNKNOWN_ACTIVATOR = 4
TELNET = 0
SSH = 1



_MESSAGE = descriptor.Descriptor(
  name='Message',
  full_name='sae.Message',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='id', full_name='sae.Message.id', index=0,
      number=1, type=13, cpp_type=3, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='request', full_name='sae.Message.request', index=1,
      number=2, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='response', full_name='sae.Message.response', index=2,
      number=3, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='error', full_name='sae.Message.error', index=3,
      number=4, type=11, cpp_type=10, label=1,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_REQUEST = descriptor.Descriptor(
  name='Request',
  full_name='sae.Request',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='method', full_name='sae.Request.method', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='serialized_request', full_name='sae.Request.serialized_request', index=1,
      number=2, type=12, cpp_type=9, label=2,
      default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_RESPONSE = descriptor.Descriptor(
  name='Response',
  full_name='sae.Response',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='serialized_response', full_name='sae.Response.serialized_response', index=0,
      number=1, type=12, cpp_type=9, label=1,
      default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_ERROR = descriptor.Descriptor(
  name='Error',
  full_name='sae.Error',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='code', full_name='sae.Error.code', index=0,
      number=1, type=14, cpp_type=8, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='text', full_name='sae.Error.text', index=1,
      number=2, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_ACCESSPROFILE = descriptor.Descriptor(
  name='AccessProfile',
  full_name='sae.AccessProfile',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='scheme', full_name='sae.AccessProfile.scheme', index=0,
      number=1, type=14, cpp_type=8, label=2,
      default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='address', full_name='sae.AccessProfile.address', index=1,
      number=2, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='port', full_name='sae.AccessProfile.port', index=2,
      number=3, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='user', full_name='sae.AccessProfile.user', index=3,
      number=4, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='password', full_name='sae.AccessProfile.password', index=4,
      number=5, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='super_password', full_name='sae.AccessProfile.super_password', index=5,
      number=6, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='path', full_name='sae.AccessProfile.path', index=6,
      number=7, type=9, cpp_type=9, label=1,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_PINGREQUEST = descriptor.Descriptor(
  name='PingRequest',
  full_name='sae.PingRequest',
  filename='sae.proto',
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_PINGRESPONSE = descriptor.Descriptor(
  name='PingResponse',
  full_name='sae.PingResponse',
  filename='sae.proto',
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_REGISTERREQUEST = descriptor.Descriptor(
  name='RegisterRequest',
  full_name='sae.RegisterRequest',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='name', full_name='sae.RegisterRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_REGISTERRESPONSE = descriptor.Descriptor(
  name='RegisterResponse',
  full_name='sae.RegisterResponse',
  filename='sae.proto',
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_PULLCONFIGREQUEST = descriptor.Descriptor(
  name='PullConfigRequest',
  full_name='sae.PullConfigRequest',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='access_profile', full_name='sae.PullConfigRequest.access_profile', index=0,
      number=1, type=11, cpp_type=10, label=2,
      default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='profile', full_name='sae.PullConfigRequest.profile', index=1,
      number=2, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_PULLCONFIGRESPONSE = descriptor.Descriptor(
  name='PullConfigResponse',
  full_name='sae.PullConfigResponse',
  filename='sae.proto',
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='config', full_name='sae.PullConfigResponse.config', index=0,
      number=2, type=9, cpp_type=9, label=2,
      default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],  # TODO(robinson): Implement.
  enum_types=[
  ],
  options=None)


_MESSAGE.fields_by_name['request'].message_type = _REQUEST
_MESSAGE.fields_by_name['response'].message_type = _RESPONSE
_MESSAGE.fields_by_name['error'].message_type = _ERROR
_ERROR.fields_by_name['code'].enum_type = _ERRORCODE
_ACCESSPROFILE.fields_by_name['scheme'].enum_type = _ACCESSSCHEME
_PULLCONFIGREQUEST.fields_by_name['access_profile'].message_type = _ACCESSPROFILE

class Message(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _MESSAGE

class Request(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _REQUEST

class Response(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _RESPONSE

class Error(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _ERROR

class AccessProfile(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _ACCESSPROFILE

class PingRequest(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PINGREQUEST

class PingResponse(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PINGRESPONSE

class RegisterRequest(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _REGISTERREQUEST

class RegisterResponse(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _REGISTERRESPONSE

class PullConfigRequest(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PULLCONFIGREQUEST

class PullConfigResponse(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PULLCONFIGRESPONSE


_SAESERVICE = descriptor.ServiceDescriptor(
  name='SAEService',
  full_name='sae.SAEService',
  index=0,
  options=None,
  methods=[
  descriptor.MethodDescriptor(
    name='ping',
    full_name='sae.SAEService.ping',
    index=0,
    containing_service=None,
    input_type=_PINGREQUEST,
    output_type=_PINGRESPONSE,
    options=None,
  ),
  descriptor.MethodDescriptor(
    name='register',
    full_name='sae.SAEService.register',
    index=1,
    containing_service=None,
    input_type=_REGISTERREQUEST,
    output_type=_REGISTERRESPONSE,
    options=None,
  ),
])

class SAEService(service.Service):
  __metaclass__ = service_reflection.GeneratedServiceType
  DESCRIPTOR = _SAESERVICE
class SAEService_Stub(SAEService):
  __metaclass__ = service_reflection.GeneratedServiceStubType
  DESCRIPTOR = _SAESERVICE


_ACTIVATORSERVICE = descriptor.ServiceDescriptor(
  name='ActivatorService',
  full_name='sae.ActivatorService',
  index=1,
  options=None,
  methods=[
  descriptor.MethodDescriptor(
    name='ping',
    full_name='sae.ActivatorService.ping',
    index=0,
    containing_service=None,
    input_type=_PINGREQUEST,
    output_type=_PINGRESPONSE,
    options=None,
  ),
  descriptor.MethodDescriptor(
    name='register',
    full_name='sae.ActivatorService.register',
    index=1,
    containing_service=None,
    input_type=_PINGREQUEST,
    output_type=_PINGRESPONSE,
    options=None,
  ),
  descriptor.MethodDescriptor(
    name='pull_config',
    full_name='sae.ActivatorService.pull_config',
    index=2,
    containing_service=None,
    input_type=_PULLCONFIGREQUEST,
    output_type=_PULLCONFIGRESPONSE,
    options=None,
  ),
])

class ActivatorService(service.Service):
  __metaclass__ = service_reflection.GeneratedServiceType
  DESCRIPTOR = _ACTIVATORSERVICE
class ActivatorService_Stub(ActivatorService):
  __metaclass__ = service_reflection.GeneratedServiceStubType
  DESCRIPTOR = _ACTIVATORSERVICE

