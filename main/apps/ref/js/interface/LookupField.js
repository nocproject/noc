//---------------------------------------------------------------------
// NOC.main.pyrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.LookupField");

Ext.define("NOC.main.ref.interface.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.interface.LookupField",
    requires: ["NOC.main.ref.interface.Lookup"]
});
