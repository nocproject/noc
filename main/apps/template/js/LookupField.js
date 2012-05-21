//---------------------------------------------------------------------
// NOC.main.template.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.template.LookupField");

Ext.define("NOC.main.template.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.template.LookupField",
    requires: ["NOC.main.template.Lookup"]
});
