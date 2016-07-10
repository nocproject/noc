//---------------------------------------------------------------------
// NOC.gis.area.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.area.LookupField");

Ext.define("NOC.gis.area.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.area.LookupField",
    requires: ["NOC.gis.area.Lookup"]
});
