//---------------------------------------------------------------------
// NOC.inv.pendinglink.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.pendinglink.LookupField");

Ext.define("NOC.inv.pendinglink.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.pendinglink.LookupField",
    requires: ["NOC.inv.pendinglink.Lookup"]
});
