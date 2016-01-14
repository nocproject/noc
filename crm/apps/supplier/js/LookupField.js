//---------------------------------------------------------------------
// NOC.crm.supplier.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplier.LookupField");

Ext.define("NOC.crm.supplier.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.crm.supplier.LookupField",
    requires: ["NOC.crm.supplier.Lookup"]
});
