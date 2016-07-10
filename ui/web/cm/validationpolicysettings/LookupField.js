//---------------------------------------------------------------------
// NOC.cm.validationpolicysettings.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicysettings.LookupField");

Ext.define("NOC.cm.validationpolicysettings.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.cm.validationpolicysettings.LookupField",
    requires: ["NOC.cm.validationpolicysettings.Lookup"]
});
