//---------------------------------------------------------------------
// NOC.sa.managedobjectprofile.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectprofile.LookupField");

Ext.define("NOC.sa.managedobjectprofile.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.managedobjectprofile.LookupField",
    requires: ["NOC.sa.managedobjectprofile.Lookup"],
    uiStyle: "medium"
});
