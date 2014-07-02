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
    queryMode: "remote",
    queryParam: "__query",
    createNewOnEnter: true,
    createNewOnBlur: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            store: Ext.create("Ext.data.Store", {
                fields: ["id", "label"],
                proxy: {
                    type: "ajax",
                    url: "/main/tag/lookup/",
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    extraParams: {
                        "__format": "ext"
                    },
                    reader: {
                        type: "json",
                        root: "data",
                        totalProperty: "total",
                        successProperty: "success"
                    }
                }
            })
        });
        me.callParent();
    }
});