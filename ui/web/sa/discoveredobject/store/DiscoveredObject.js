//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.store.DiscoveredObject");

Ext.define("NOC.sa.discoveredobject.store.DiscoveredObject", {
  extend: "Ext.data.BufferedStore",
  alias: "store.sa.discoveredobject",
  model: "NOC.sa.discoveredobject.model.DiscoveredObject",
  autoLoad: false,
  pageSize: 70,
  leadingBufferZone: 70,
  numFromEdge: Math.ceil(70 / 2),
  trailingBufferZone: 70,
  purgePageCount: 10,
  remoteSort: true,
  sorters: [
    {
      property: 'timestamp',
      direction: 'DESC',
    },
  ],
  proxy: {
    type: "rest",
    url: "/sa/discoveredobject/",
    pageParam: "__page",
    startParam: "__start",
    limitParam: "__limit",
    sortParam: "__sort",
    reader: {
      type: "json",
      rootProperty: "data",
      totalProperty: "total",
      successProperty: "success",
    },
    writer: {
      type: "json",
    },
  },
});