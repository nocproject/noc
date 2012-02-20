//---------------------------------------------------------------------
// NOC.main.pyrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.LookupField");

Ext.define("NOC.main.pyrule.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.pyrule.LookupField",
    requires: ["NOC.main.pyrule.Lookup"]
});
