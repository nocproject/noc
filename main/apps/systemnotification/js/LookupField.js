//---------------------------------------------------------------------
// NOC.main.systemnotification.LookupFields
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.systemnotification.LookupField");

Ext.define("NOC.main.systemnotification.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.systemnotification.LookupField",
    requires: ["NOC.main.systemnotification.Lookup"]
});
