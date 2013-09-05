//---------------------------------------------------------------------
// NOC.sa.objectnotification.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectnotification.LookupField");

Ext.define("NOC.sa.objectnotification.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.objectnotification.LookupField",
    requires: ["NOC.sa.objectnotification.Lookup"]
});
