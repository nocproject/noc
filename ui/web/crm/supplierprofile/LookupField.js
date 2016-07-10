//---------------------------------------------------------------------
// NOC.crm.supplierprofile.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplierprofile.LookupField");

Ext.define("NOC.crm.supplierprofile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.crm.supplierprofile.LookupField",
    requires: ["NOC.crm.supplierprofile.Lookup"]
});
