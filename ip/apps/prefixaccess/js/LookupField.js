//---------------------------------------------------------------------
// NOC.ip.prefixaccess.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefixaccess.LookupField");

Ext.define("NOC.ip.prefixaccess.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.ip.prefixaccess.LookupField",
    requires: ["NOC.ip.prefixaccess.Lookup"]
});
