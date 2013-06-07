//---------------------------------------------------------------------
// Change Interface Project
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.ChangeInterfaceProjectForm");

Ext.define("NOC.inv.interface.ChangeInterfaceProjectForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.project.project.LookupField"
    ],
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    // width: 300,
    // height: 200,
    autoScroll: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            autoLoad: false,
            fields: ["id", "label"],
            data: []
        });

        Ext.apply(me, {
            title: "Change " + me.record.get("name") + " project",
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "project.project.LookupField",
                            name: "project",
                            fieldLabel: "Project",
                            allowBlank: true
                        }
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Change",
                            iconCls: "icon_page_edit",
                            formBind: true,
                            scope: me,
                            handler: me.onChangeProject
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.field = me.items.first().getForm().getFields().items[0];
        me.field.setValue(me.record.get("project"));
    },
    //
    onChangeProject: function() {
        var me = this,
            project = me.field.getValue(),
            project_label = me.field.getDisplayValue(),
            data = {
                project: project
            };

        Ext.Ajax.request({
            url: "/inv/interface/l1/" + me.record.get("id") + "/change_project/",
            method: "POST",
            jsonData: data,
            scope: me,
            success: function() {
                me.record.set("project", project);
                me.record.set("project__label", project_label);
                me.close();
            },
            failure: function() {
                NOC.error("Failed to change project");
            }
        });
    }
});
