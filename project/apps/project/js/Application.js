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
        Ext.apply(me, {
            formToolbar: [
                {
                    itemId: "resources",
                    text: "Resources",
                    iconCls: "icon_page_link",
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
    showProjectResources: function(record) {
        var me = this;
        Ext.Ajax.request({
            url: "/project/project/" + record.get("id") + "/resources/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                Ext.create("NOC.project.project.ProjectResources", {
                    app: me,
                    data: data,
                    project: record
                });
            },
            failure: function() {
                NOC.error("Failed to get resources");
            }
        })
    },
    onProjectResources: function() {
        var me = this;
        me.showProjectResources(me.currentRecord);
    },
    //
    onPreview: function(record) {
        var me = this;
        me.showProjectResources(record);
    }
});
