//---------------------------------------------------------------------
// NOC.wf.solution.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.solution.LookupField");

Ext.define("NOC.wf.solution.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.wf.solution.LookupField",
    requires: ["NOC.wf.solution.Lookup"]
});
