//---------------------------------------------------------------------
// NOC.inv.unknownmodel.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.unknownmodel.LookupField");

Ext.define("NOC.inv.unknownmodel.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.unknownmodel.LookupField",
    requires: ["NOC.inv.unknownmodel.Lookup"]
});
