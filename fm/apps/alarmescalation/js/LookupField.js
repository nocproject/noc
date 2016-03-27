//---------------------------------------------------------------------
// NOC.fm.alarmescalation.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmescalation.LookupField");

Ext.define("NOC.fm.alarmescalation.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.alarmescalation.LookupField",
    requires: ["NOC.fm.alarmescalation.Lookup"]
});
