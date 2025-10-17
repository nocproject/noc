//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.store.VRF");

Ext.define("NOC.ip.ipam.store.VRF", {
  extend: "Ext.data.BufferedStore",
  alias: "store.ip.ipam",
  model: "NOC.ip.ipam.model.VRF",
  autoLoad: true,
  pageSize: 70,
  leadingBufferZone: 70,
  numFromEdge: Math.ceil(70 / 2),
  trailingBufferZone: 70,
  purgePageCount: 10,
  remoteSort: true,
  groupField: "vrf_group",
  groupDir: "DESC",
  sorters: [
    {
      property: "name",
      direction: "ASC",
    },
  ],
  proxy: {
    type: "rest",
    url: "/ip/vrf/",
    pageParam: "__page",
    startParam: "__start",
    limitParam: "__limit",
    sortParam: "__sort",
    groupParam: "__group",
    extraParams: {
      __format: "ext",
    },
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