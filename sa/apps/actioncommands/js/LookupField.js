//---------------------------------------------------------------------
// NOC.sa.actioncommands.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.actioncommands.LookupField");

Ext.define("NOC.sa.actioncommands.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.actioncommands.LookupField",
    requires: ["NOC.sa.actioncommands.Lookup"]
});
