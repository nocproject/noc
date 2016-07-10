//---------------------------------------------------------------------
// NOC.sa.groupaccess.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.groupaccess.LookupField");

Ext.define("NOC.sa.groupaccess.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.groupaccess.LookupField",
    requires: ["NOC.sa.groupaccess.Lookup"]
});
