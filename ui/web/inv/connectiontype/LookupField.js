//---------------------------------------------------------------------
// NOC.inv.connectiontype.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectiontype.LookupField");

Ext.define("NOC.inv.connectiontype.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.connectiontype.LookupField",
    requires: ["NOC.inv.connectiontype.Lookup"]
});
