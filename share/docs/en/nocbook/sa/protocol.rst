SAE Protocol
************
SAE use lightweight RPC protocol to communicate. Protocol has following distinctive features:
  
* `Google's Protocol Buffers <http://code.google.com/p/protobuf/>`_ used for message serialization and as RPC interface skeleton
* gzip message compression used to reduce bandwidth
* optional SSL encryption

Complete RPC message definition stored in sa/protocols/sae.proto
