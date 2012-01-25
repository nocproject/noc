//---------------------------------------------------------------------
// NOC.inv.vendor.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.vendor.LookupField");

Ext.define("NOC.inv.vendor.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.vendor.LookupField",
    requires: ["NOC.inv.vendor.Lookup"]
});
