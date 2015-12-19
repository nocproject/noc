//---------------------------------------------------------------------
// NOC.sa.profilecheckrule.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.profilecheckrule.LookupField");

Ext.define("NOC.sa.profilecheckrule.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.sa.profilecheckrule.LookupField",
    requires: ["NOC.sa.profilecheckrule.Lookup"]
});
