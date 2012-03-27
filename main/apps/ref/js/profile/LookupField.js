//---------------------------------------------------------------------
// NOC.main.pyrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.LookupField");

Ext.define("NOC.main.ref.profile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.profile.LookupField",
    requires: ["NOC.main.ref.profile.Lookup"]
});
