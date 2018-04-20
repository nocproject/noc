//---------------------------------------------------------------------
// NOC.vc.vcfilter.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcfilter.LookupField");

Ext.define("NOC.vc.vcfilter.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.vc.vcfilter.LookupField",
    requires: ["NOC.vc.vcfilter.Lookup"]
});
