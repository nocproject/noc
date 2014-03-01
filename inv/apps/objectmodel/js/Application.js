//---------------------------------------------------------------------
// inv.objectmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.Application");

Ext.define("NOC.inv.objectmodel.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "Ext.ux.form.GridField",
        "Ext.ux.form.ModelDataField",
        "NOC.inv.objectmodel.Model",
        "NOC.inv.vendor.LookupField",
        "NOC.inv.connectiontype.LookupField",
        "NOC.inv.connectionrule.LookupField",
        "NOC.inv.objectmodel.templates.Test",
        "NOC.inv.objectmodel.templates.JSON"
    ],
    model: "NOC.inv.objectmodel.Model",
    search: true,
    filters: [
        {
            title: "By Is Builtin",
            name: "is_builtin",
            ftype: "boolean"
        },
        {
            title: "By Vendor",
            name: "vendor",
            ftype: "lookup",
            lookup: "inv.vendor"
        }
    ],

    actions: [
        {
            title: "Get JSON",
            action: "json",
            glyph: NOC.glyph.file,
            resultTemplate: "JSON"
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/inv/objectmodel/{{id}}/json/",
            previewName: "Object Model: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        // Test panel
        me.testPanel = Ext.create("NOC.core.TemplatePreview", {
            app: me,
            previewName: "Compatible connections for {{name}}",
            template: me.templates.Test
        });
        me.ITEM_TEST = me.registerItem(me.testPanel);
        //
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
                },
                {
                    text: "Vendor",
                    dataIndex: "vendor",
                    renderer: NOC.render.Lookup("vendor"),
                    width: 150
                },
                {
                    text: "Connection Rule",
                    dataIndex: "connection_rule",
                    renderer: NOC.render.Lookup("connection_rule"),
                    width: 100
                },
                {
                    text: "CR. Context",
                    dataIndex: "cr_context",
                    width: 70
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
                    name: "vendor",
                    xtype: "inv.vendor.LookupField",
                    fieldLabel: "Vendor",
                    allowBlank: false
                },
                {
                    name: "connection_rule",
                    xtype: "inv.connectionrule.LookupField",
                    fieldLabel: "Connection Rule",
                    allowBlank: true
                },
                {
                    name: "cr_context",
                    xtype: "textfield",
                    fieldLabel: "Connection Context",
                    allowBlank: true
                },
                {
                    name: "plugins",
                    xtype: "textfield",
                    fieldLabel: "Plugins",
                    allowBlank: true
                },
                {
                    name: "data",
                    xtype: "modeldatafield",
                    fieldLabel: "Model Data",
                    labelAlign: "top"
                },
                {
                    name: "connections",
                    xtype: "gridfield",
                    fieldLabel: "Connections",
                    labelAlign: "top",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name",
                            editor: "textfield",
                            width: 100
                        },
                        {
                            text: "Connection Type",
                            dataIndex: "type",
                            editor: "inv.connectiontype.LookupField",
                            width: 200,
                            renderer: NOC.render.Lookup("type")
                        },
                        {
                            text: "Group",
                            dataIndex: "group",
                            editor: "textfield",
                            width: 50
                        },
                        {
                            text: "Direction",
                            dataIndex: "direction",
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["i", "Inner"],
                                    ["o", "Outer"],
                                    ["s", "Connection"]
                                ]
                            },
                            width: 50
                        },
                        {
                            text: "Gender",
                            dataIndex: "gender",
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["m", "Male"],
                                    ["f", "Female"],
                                    ["s", "Genderless"]
                                ]
                            },
                            width: 50
                        },
                        {
                            text: "Cross",
                            dataIndex: "cross",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Protocols",
                            dataIndex: "protocols",
                            width: 150,
                            editor: "textfield",
                            renderer: "htmlEncode"
                        },
                        {
                            text: "Internal name",
                            dataIndex: "internal_name",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            editor: "textfield",
                            flex: 1
                        }
                    ],
                    listeners: {
                        scope: me,
                        clone: me.onCloneConnection
                    }
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
                },
                {
                    text: "Test",
                    glyph: NOC.glyph.question,
                    tooltip: "Test compatible types",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onTest
                }
            ]
        });
        me.callParent();
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    },
    //
    onTest: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/objectmodel/" + me.currentRecord.get("id") + "/compatible/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.showItem(me.ITEM_TEST).preview(me.currentRecord, data);
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },
    //
    cleanData: function(v) {
        var me = this,
            i, c, x;
        for(i in v.connections) {
            c = v.connections[i];
            if(!Ext.isArray(c.protocols)) {
                x = c.protocols.trim();
                if(x==="") {
                    c.protocols = [];
                } else {
                    c.protocols = c.protocols.split(",").map(function(v) {
                        return v.trim();
                    });
                }
            }
        }
    },
    //
    onCloneConnection: function(record) {
        var me = this,
            v = record.get("name"),
            m = v.match(/(.*?)(\d+)/);
        if(m===null) {
            return;
        }
        var n = +m[2] + 1;
        record.set("name", m[1] + n);
    }
});
