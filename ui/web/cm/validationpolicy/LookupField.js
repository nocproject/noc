//---------------------------------------------------------------------
// NOC.cm.validationpolicy.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicy.LookupField");

Ext.define("NOC.cm.validationpolicy.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.cm.validationpolicy.LookupField",
    requires: ["NOC.cm.validationpolicy.Lookup"]
});
