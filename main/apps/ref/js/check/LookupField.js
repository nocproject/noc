//---------------------------------------------------------------------
// NOC.main.check.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.LookupField");

Ext.define("NOC.main.ref.check.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.check.LookupField",
    requires: ["NOC.main.ref.check.Lookup"]
});
