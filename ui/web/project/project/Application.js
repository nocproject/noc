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
        "NOC.project.project.Model",
        "NOC.project.project.templates.AllocatedResources"
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
                    text: "Resources",
                    glyph: NOC.glyph.list,
                    tooltip: "Show Allocated resources",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onProjectResources
                }
            ],
            columns: [
                {
                    text: "Code",
                    dataIndex: "code",
                    width: 150
                },
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: "Code",
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
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
