//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.store.Profile");

Ext.define("NOC.fm.alarm.store.Profile", {
  extend: "Ext.data.Store",
  alias: "store.fm.profile",
  autoLoad: true,
  pageSize: 500,
  proxy: {
    type: "rest",
    url: "/fm/alarm/profile_lookup/",
    pageParam: "__page",
    startParam: "__start",
    limitParam: "__limit",
    sortParam: "__sort",
  },
});