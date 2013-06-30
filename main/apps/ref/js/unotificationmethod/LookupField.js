//---------------------------------------------------------------------
// NOC.main.unotificationmethod.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.unotificationmethod.LookupField");

Ext.define("NOC.main.ref.unotificationmethod.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.unotificationmethod.LookupField",
    requires: ["NOC.main.ref.unotificationmethod.Lookup"]
});
