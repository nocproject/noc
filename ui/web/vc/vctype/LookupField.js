//---------------------------------------------------------------------
// NOC.vc.vctype.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vctype.LookupField");

Ext.define("NOC.vc.vctype.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.vc.vctype.LookupField",
    requires: ["NOC.vc.vctype.Lookup"]
});
