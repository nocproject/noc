//---------------------------------------------------------------------
// NOC.main.pendingnotifications.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pendingnotifications.LookupField");

Ext.define("NOC.main.pendingnotifications.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.pendingnotifications.LookupField",
    requires: ["NOC.main.pendingnotifications.Lookup"]
});
