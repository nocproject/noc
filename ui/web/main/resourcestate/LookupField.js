//---------------------------------------------------------------------
// NOC.main.resourcestate.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.resourcestate.LookupField");

Ext.define("NOC.main.resourcestate.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.resourcestate.LookupField",
    requires: ["NOC.main.resourcestate.Lookup"]
});
