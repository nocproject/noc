//---------------------------------------------------------------------
// NOC.inv.networksegment.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.LookupField");

Ext.define("NOC.inv.networksegment.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.networksegment.LookupField",
    requires: ["NOC.inv.networksegment.Lookup"]
});
