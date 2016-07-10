//---------------------------------------------------------------------
// NOC.main.customfield.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfield.LookupField");

Ext.define("NOC.main.customfield.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.customfield.LookupField",
    requires: ["NOC.main.customfield.Lookup"]
});
