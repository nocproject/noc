//---------------------------------------------------------------------
// NOC.gis.division.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.division.LookupField");

Ext.define("NOC.gis.division.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.division.LookupField",
    requires: ["NOC.gis.division.Lookup"]
});
