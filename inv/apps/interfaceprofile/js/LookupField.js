//---------------------------------------------------------------------
// NOC.inv.interfaceprofile.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.LookupField");

Ext.define("NOC.inv.interfaceprofile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.inv.interfaceprofile.LookupField",
    requires: ["NOC.inv.interfaceprofile.Lookup"]
});
