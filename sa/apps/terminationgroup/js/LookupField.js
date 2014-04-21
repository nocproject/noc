//---------------------------------------------------------------------
// NOC.sa.terminationgroup.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.terminationgroup.LookupField");

Ext.define("NOC.sa.terminationgroup.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.terminationgroup.LookupField",
    requires: ["NOC.sa.terminationgroup.Lookup"]
});
