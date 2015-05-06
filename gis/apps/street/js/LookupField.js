//---------------------------------------------------------------------
// NOC.gis.street.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.street.LookupField");

Ext.define("NOC.gis.street.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.gis.street.LookupField",
    requires: ["NOC.gis.street.Lookup"]
});
