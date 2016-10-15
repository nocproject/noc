//---------------------------------------------------------------------
// project.project application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.Application");

Ext.define("NOC.project.project.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.project.project.Model"
    ],
    model: "NOC.project.project.Model",
    search: true,
    initComponent: function() {
        var me = this;
        me.ITEM_RESOURCES = me.registerItem("NOC.project.project.ProjectResources");
        Ext.apply(me, {
            formToolbar: [
                {
                    itemId: "resources",
                    text: __("Resources"),
                    glyph: NOC.glyph.list,
                    tooltip: __("Show Allocated resources"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onProjectResources
                }
            ],
            columns: [
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 150
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    onProjectResources: function() {
        var me = this;
        me.previewItem(me.ITEM_RESOURCES, me.currentRecord);
    },
    //
    onPreview: function(record) {
        var me = this;
        me.previewItem(me.ITEM_RESOURCES, record);
    }
});
