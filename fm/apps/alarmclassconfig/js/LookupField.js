//---------------------------------------------------------------------
// NOC.fm.alarmclassconfig.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclassconfig.LookupField");

Ext.define("NOC.fm.alarmclassconfig.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.alarmclassconfig.LookupField",
    requires: ["NOC.fm.alarmclassconfig.Lookup"]
});
