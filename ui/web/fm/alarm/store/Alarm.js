//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.store.Alarm");

Ext.define("NOC.fm.alarm.store.Alarm", {
  extend: "Ext.data.BufferedStore",
  alias: "store.fm.alarm",
  model: "NOC.fm.alarm.model.Alarm",
  autoLoad: false,
  pageSize: 70,
  leadingBufferZone: 70,
  numFromEdge: Math.ceil(70 / 2),
  trailingBufferZone: 70,
  purgePageCount: 10,
  remoteSort: true,
  sorters: [
    {
      property: "timestamp",
      direction: "DESC",
    },
  ],
  proxy: {
    type: "rest",
    url: "/fm/alarm/",
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