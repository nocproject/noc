//---------------------------------------------------------------------
// NOC.fm.alarmclass.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclass.LookupField");

Ext.define("NOC.fm.alarmclass.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.alarmclass.LookupField",
    requires: ["NOC.fm.alarmclass.Lookup"]
});
