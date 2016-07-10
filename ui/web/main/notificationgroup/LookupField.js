//---------------------------------------------------------------------
// NOC.main.notificationgroup.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroup.LookupField");

Ext.define("NOC.main.notificationgroup.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.notificationgroup.LookupField",
    requires: ["NOC.main.notificationgroup.Lookup"]
});
