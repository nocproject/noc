//---------------------------------------------------------------------
// NOC.gis.layer.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.layer.LookupField");

Ext.define("NOC.gis.layer.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.layer.LookupField",
    requires: ["NOC.gis.layer.Lookup"]
});
