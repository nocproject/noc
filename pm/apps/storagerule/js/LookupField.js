//---------------------------------------------------------------------
// NOC.pm.storagerule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storagerule.LookupField");

Ext.define("NOC.pm.storagerule.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.pm.storagerule.LookupField",
    requires: ["NOC.pm.storagerule.Lookup"]
});
