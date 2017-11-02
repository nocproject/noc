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
    displayField: "label",
    valueField: "label",
    queryParam: "__q",
    queryMode: "remote",
    autoLoadOnValue: true,
    // forceSelection: false,
    // triggerAction: 'query',
    // createNewOnEnter: true,
    // createNewOnBlur: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            store: {
                fields: ["label"],
                // pageSize: 25,
                proxy: {
                    type: "rest",
                    url: '/main/tag/ac_lookup/',
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    extraParams: {
                        "__format": "ext"
                    },
                    reader: {
                        type: "json",
                        rootProperty: "data",
                        totalProperty: "total",
                        successProperty: "success"
                    }
                }
            }
        });
        me.callParent();
    }
});