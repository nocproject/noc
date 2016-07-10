//---------------------------------------------------------------------
// NOC.sa.useraccess.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.useraccess.LookupField");

Ext.define("NOC.sa.useraccess.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.useraccess.LookupField",
    requires: ["NOC.sa.useraccess.Lookup"]
});
