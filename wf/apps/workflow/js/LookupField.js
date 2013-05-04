//---------------------------------------------------------------------
// NOC.wf.workflow.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.LookupField");

Ext.define("NOC.wf.workflow.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.wf.workflow.LookupField",
    requires: ["NOC.wf.workflow.Lookup"]
});
