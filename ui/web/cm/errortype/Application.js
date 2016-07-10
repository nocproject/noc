//---------------------------------------------------------------------
// cm.errortype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.errortype.Application");

Ext.define("NOC.cm.errortype.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.cm.errortype.Model"
    ],
    model: "NOC.cm.errortype.Model",
    search: true,
    initComponent: function() {
        var me = this;

        me.ITEM_JSON = me.registerItem(
            Ext.create("NOC.core.JSONPreview", {
                app: me,
                restUrl: "/cm/errortype/{{id}}/json/",
                previewName: "Error Type: {{name}}"
            })
        );

        Ext.apply(me, {
            columns: [
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
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: "UUID"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "subject_template",
                    xtype: "textarea",
                    fieldLabel: "Subject Template",
                    allowBlank: false
                },
                {
                    name: "body_template",
                    xtype: "textarea",
                    fieldLabel: "Body Template",
                    allowBlank: false
                }
            ],
            formToolbar: [
                {
                    text: "JSON",
                    glyph: NOC.glyph.file,
                    tooltip: "Show JSON",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON).preview(me.currentRecord);
    }
});
