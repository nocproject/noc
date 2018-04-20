//---------------------------------------------------------------------
// NOC.inv.capability.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.capability.LookupField");

Ext.define("NOC.inv.capability.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.capability.LookupField",
    requires: ["NOC.inv.capability.Lookup"]
});
