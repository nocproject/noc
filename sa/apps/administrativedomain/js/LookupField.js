//---------------------------------------------------------------------
// NOC.sa.administrativedomain.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.administrativedomain.LookupField");

Ext.define("NOC.sa.administrativedomain.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.administrativedomain.LookupField",
    requires: ["NOC.sa.administrativedomain.Lookup"]
});
