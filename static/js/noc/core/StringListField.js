//---------------------------------------------------------------------
// NOC.core.TagsField -
// Tags Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.StringListField");

Ext.define("NOC.core.StringListField", {
    extend: "Ext.ux.form.field.BoxSelect",
    alias: ["widget.stringlistfield"],
    forceSelection: false,
    displayField: "label",
    valueField: "label",
    queryMode: "local",
    queryParam: "__query",
    createNewOnEnter: true,
    createNewOnBlur: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            store: Ext.create("Ext.data.Store", {
                fields: ["id", "label"],
                data: []
            })
        });
        me.callParent();
    }
});