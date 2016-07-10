//---------------------------------------------------------------------
// NOC.sa.authprofile.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.LookupField");

Ext.define("NOC.sa.authprofile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.authprofile.LookupField",
    requires: ["NOC.sa.authprofile.Lookup"]
});
