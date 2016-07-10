//---------------------------------------------------------------------
// NOC.cm.validationrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationrule.LookupField");

Ext.define("NOC.cm.validationrule.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.cm.validationrule.LookupField",
    requires: ["NOC.cm.validationrule.Lookup"]
});
