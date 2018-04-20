//---------------------------------------------------------------------
// NOC.sa.managedobject.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LookupField");

Ext.define("NOC.sa.managedobject.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.managedobject.LookupField",
    requires: ["NOC.sa.managedobject.Lookup"]
});
