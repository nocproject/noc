//---------------------------------------------------------------------
// NOC.sa.commandsnippet.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.commandsnippet.LookupField");

Ext.define("NOC.sa.commandsnippet.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.commandsnippet.LookupField",
    requires: ["NOC.sa.commandsnippet.Lookup"]
});
