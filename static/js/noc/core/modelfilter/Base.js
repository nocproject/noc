//---------------------------------------------------------------------
// NOC.core.modelfilter.Base
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Base");

Ext.define("NOC.core.modelfilter.Base", {
    extend: "Ext.form.FieldSet",
    ftype: "base",
    name: null,
    collapsible: false,
    handler: undefined,
    border: false,

    onChange: function() {
        if(Ext.isDefined(this.handler))
            this.handler();
    },

    getFilter: function() {
        return {};
    }
});
