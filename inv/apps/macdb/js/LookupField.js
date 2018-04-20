//---------------------------------------------------------------------
// NOC.inv.macdb.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.LookupField");

Ext.define("NOC.inv.macdb.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.macdb.LookupField",
    requires: ["NOC.inv.macdb.Lookup"]
});
