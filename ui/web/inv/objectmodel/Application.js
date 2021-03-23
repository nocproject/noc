//---------------------------------------------------------------------
// inv.objectmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.Application");

Ext.define("NOC.inv.objectmodel.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.core.LabelField",
        "NOC.core.TemplatePreview",
        "NOC.inv.objectmodel.Model",
        "NOC.inv.vendor.LookupField",
        "NOC.inv.connectiontype.LookupField",
        "NOC.inv.connectionrule.LookupField",
        "NOC.pm.measurementunits.LookupField",
        "Ext.ux.form.ModelDataField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.objectmodel.Model",
    search: true,
    treeFilter: "category",
    filters: [
        {
            title: __("By Is Builtin"),
            name: "is_builtin",
            ftype: "boolean"
        },
        {
            title: __("By Vendor"),
            name: "vendor",
            ftype: "lookup",
            lookup: "inv.vendor"
        }
    ],

    actions: [
        {
            title: __("Get JSON"),
            action: "json",
            glyph: NOC.glyph.file,
            resultTemplate: new Ext.XTemplate('<pre>{data}</pre>')
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/objectmodel/{id}/json/'),
            previewName: new Ext.XTemplate('Object Model: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        // Test panel
        me.testPanel = Ext.create("NOC.core.TemplatePreview", {
            app: me,
            previewName: new Ext.XTemplate('Compatible connections for {name}'),
            template: new Ext.XTemplate('<div class="noc-tp">\n    <h1>Possible connections for model {name}</h1>\n    <table border="1">\n        <tpl foreach="connections">\n            <tr>\n                <td>\n                    <tpl foreach="names">\n                        <b>{name}</b><br/><i>({description})</i><br/>\n                    </tpl>\n                </td>\n                <td>{direction}</td>\n                <td>\n                    <table>\n                        <tpl foreach="connections">\n                            <tr>\n                                <td>\n                                    <b>{name}</b><br/></i>({description})</i>\n                                </td>\n                                <td><b>{model}</b><br/>({model_description})</td>\n                            </tr>\n                        </tpl>\n                    </table>\n                </td>\n            </tr>\n        </tpl>\n    </table>\n    <h1>Internal crossing for {name}</h1>\n    <!--{grid crossing}-->\n</div>')
        });
        me.ITEM_TEST = me.registerItem(me.testPanel);
        //
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
                },
                {
                    text: __("Vendor"),
                    dataIndex: "vendor",
                    renderer: NOC.render.Lookup("vendor"),
                    width: 150
                },
                {
                    text: __("Connection Rule"),
                    dataIndex: "connection_rule",
                    renderer: NOC.render.Lookup("connection_rule"),
                    width: 100
                },
                {
                    text: __("CR. Context"),
                    dataIndex: "cr_context",
                    width: 70
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    width: 100,
                    renderer: NOC.render.Tags
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description")
                },
                {
                    name: "vendor",
                    xtype: "inv.vendor.LookupField",
                    fieldLabel: __("Vendor"),
                    allowBlank: false
                },
                {
                    name: "connection_rule",
                    xtype: "inv.connectionrule.LookupField",
                    fieldLabel: __("Connection Rule"),
                    allowBlank: true
                },
                {
                    name: "cr_context",
                    xtype: "textfield",
                    fieldLabel: __("Connection Context"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "plugins",
                    xtype: "textfield",
                    fieldLabel: __("Plugins"),
                    allowBlank: true
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "enable_objectmodel": true
                    },
                },
                {
                    name: "data",
                    xtype: "modeldatafield",
                    fieldLabel: __("Model Data"),
                    labelAlign: "top"
                },
                {
                    name: "connections",
                    xtype: "gridfield",
                    fieldLabel: __("Connections"),
                    labelAlign: "top",
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            editor: "textfield",
                            width: 100
                        },
                        {
                            text: __("Connection Type"),
                            dataIndex: "type",
                            editor: "inv.connectiontype.LookupField",
                            width: 200,
                            renderer: NOC.render.Lookup("type")
                        },
                        {
                            text: __("Combo"),
                            dataIndex: "combo",
                            editor: "textfield",
                            width: 50
                        },
                        {
                            text: __("Group"),
                            dataIndex: "group",
                            editor: "textfield",
                            width: 50
                        },
                        {
                            text: __("Direction"),
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
                            text: __("Gender"),
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
                            text: __("Composite"),
                            dataIndex: "composite",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Composite pins"),
                            dataIndex: "composite_pins",
                            width: 50,
                            editor: {
                                xtype: "textfield",
                                regex: /^\d+-\d+$/,
                                regexText: __("Regex error!")
                            }
                        },
                        {
                            text: __("Cross"),
                            dataIndex: "cross",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Protocols"),
                            dataIndex: "protocols",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: __("Internal name"),
                            dataIndex: "internal_name",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            editor: "textfield",
                            flex: 1
                        }
                    ],
                    listeners: {
                        scope: me,
                        clone: me.onCloneConnection
                    }
                },
                {
                    name: "sensors",
                    fieldLabel: __("Sensors"),
                    xtype: "gridfield",
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            width: 200,
                            editor: "textfield"
                        },
                        {
                            text: __("Units"),
                            dataIndex: "units",
                            width: 100,
                            editor: "pm.measurementunits.LookupField",
                            renderer: NOC.render.Lookup("units")
                        },
                        {
                            text: __("Modbus Register"),
                            dataIndex: "modbus_register",
                            width: 100,
                            editor: "numberfield"
                        },
                        {
                            text: __("SNMP OID"),
                            dataIndex: "snmp_oid",
                            flex: 1,
                            editor: "textfield"
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                },
                {
                    text: __("Test"),
                    glyph: NOC.glyph.question,
                    tooltip: __("Test compatible types"),
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
                NOC.error(__("Failed to get data"));
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
                if(!Ext.isEmpty(c.protocols)) {
                    x = c.protocols.trim();
                    if(x === "" || x === undefined || x === null) {
                        c.protocols = [];
                    } else {
                        c.protocols = c.protocols.split(",").map(function(v) {
                            return v.trim();
                        });
                    }
                }
            }
        }
    },
    //
    onCloneConnection: function(record) {
        var me = this,
            v = record.get("name"),
            m = v.match(/(.*?)(\d+)/);
        if(m === null) {
            return;
        }
        var n = +m[2] + 1;
        record.set("name", m[1] + n);
    }
});
