//---------------------------------------------------------------------
// NOC.fm.alarmseverity.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmseverity.LookupField");

Ext.define("NOC.fm.alarmseverity.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.fm.alarmseverity.LookupField",
    requires: ["NOC.fm.alarmseverity.Lookup"],
    uiStyle: "medium"
});
