//---------------------------------------------------------------------
// NOC.fm.alarmtrigger.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmtrigger.LookupField");

Ext.define("NOC.fm.alarmtrigger.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.alarmtrigger.LookupField",
    requires: ["NOC.fm.alarmtrigger.Lookup"]
});
