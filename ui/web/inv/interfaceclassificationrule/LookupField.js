//---------------------------------------------------------------------
// NOC.inv.interfaceclassificationrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceclassificationrule.LookupField");

Ext.define("NOC.inv.interfaceclassificationrule.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.interfaceclassificationrule.LookupField",
    requires: ["NOC.inv.interfaceclassificationrule.Lookup"]
});
