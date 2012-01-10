//---------------------------------------------------------------------
// NOC.gis.srs.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.srs.LookupField");

Ext.define("NOC.gis.srs.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.srs.LookupField",
    requires: ["NOC.gis.srs.Lookup"]
});
