//---------------------------------------------------------------------
// NOC.inv.connectionrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectionrule.LookupField");

Ext.define("NOC.inv.connectionrule.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.connectionrule.LookupField",
    requires: ["NOC.inv.connectionrule.Lookup"]
});
