//---------------------------------------------------------------------
// NOC.gis.building.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.building.LookupField");

Ext.define("NOC.gis.building.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.building.LookupField",
    requires: ["NOC.gis.building.Lookup"]
});
