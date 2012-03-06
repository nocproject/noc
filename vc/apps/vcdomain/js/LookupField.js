//---------------------------------------------------------------------
// NOC.vc.vcdomain.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcdomain.LookupField");

Ext.define("NOC.vc.vcdomain.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.vc.vcdomain.LookupField",
    requires: ["NOC.vc.vcdomain.Lookup"]
});
