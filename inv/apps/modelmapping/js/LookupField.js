//---------------------------------------------------------------------
// NOC.inv.modelmapping.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelmapping.LookupField");

Ext.define("NOC.inv.modelmapping.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.modelmapping.LookupField",
    requires: ["NOC.inv.modelmapping.Lookup"]
});
