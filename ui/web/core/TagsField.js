//---------------------------------------------------------------------
// NOC.core.TagsField -
// Tags Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TagsField");

Ext.define("NOC.core.TagsField", {
    extend: "Ext.form.field.Tag",
    alias: ["widget.tagsfield"],
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
            store: {
                fields: ['label', 'id'],
                data: []
            },
            createNewOnEnter: true,
            createNewOnBlur: true,
            displayField: 'label'
        });
        me.callParent();
    }
});