//---------------------------------------------------------------------
// NOC.vc.vcbindfilter.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcbindfilter.LookupField");

Ext.define("NOC.vc.vcbindfilter.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.vc.vcbindfilter.LookupField",
    requires: ["NOC.vc.vcbindfilter.Lookup"]
});
