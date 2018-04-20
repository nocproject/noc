//---------------------------------------------------------------------
// NOC.gis.overlay.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.overlay.LookupField");

Ext.define("NOC.gis.overlay.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.overlay.LookupField",
    requires: ["NOC.gis.overlay.Lookup"]
});
