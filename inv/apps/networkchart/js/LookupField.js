//---------------------------------------------------------------------
// NOC.inv.networkchart.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networkchart.LookupField");

Ext.define("NOC.inv.networkchart.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.networkchart.LookupField",
    requires: ["NOC.inv.networkchart.Lookup"],
    uiStyle: "medium"
});
