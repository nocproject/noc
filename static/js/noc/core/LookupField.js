//---------------------------------------------------------------------
// NOC.core.LookupField -
// Lookup form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.LookupField");

Ext.define("NOC.core.LookupField", {
    extend: "Ext.form.ComboBox",
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    forceSelection: true,
    minChars: 2,
    typeAhead: true,
    editable: true,
    initComponent: function() {
        var sclass = this.__proto__.$className.replace("LookupField", "Lookup");
        Ext.applyIf(this, {
            store: Ext.create(sclass)
        });
        this.callParent();
        console.log(this);
    }
});