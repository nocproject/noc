//---------------------------------------------------------------------
// main.report application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.main.report.Application');

Ext.define('NOC.main.report.Application', {
    extend: 'NOC.core.ModelApplication',
    requires: [
        'NOC.core.JSONPreview',
        "NOC.core.ListFormField",
        "NOC.core.label.LabelField",
        'Ext.ux.form.JSONField',
        'Ext.ux.form.StringsField',
        'Ext.ux.form.GridField',
        "NOC.main.ref.modelid.LookupField",
        "NOC.main.ref.datasource.LookupField",
        "NOC.main.ref.reportsource.LookupField",
        "NOC.aaa.group.LookupField",
        "NOC.aaa.user.LookupField"
    ],
    model: 'NOC.main.report.Model',
    search: true,
    rowClassField: 'row_class',

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create('NOC.core.JSONPreview', {
            app: me,
            restUrl: new Ext.XTemplate('/main/report/{id}/json/'),
            previewName: new Ext.XTemplate('Report: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __('Name'),
                    dataIndex: 'name',
                    width: 250
                },
                {
                    text: __('Builtin'),
                    dataIndex: 'is_builtin',
                    renderer: NOC.render.Bool,
                    width: 30
                },
                {
                    text: __('Code'),
                    dataIndex: 'code',
                    width: 100
                },
                {
                    text: __('Description'),
                    dataIndex: 'description',
                    flex: 1
                }
            ],
            fields: [
                {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [
                        {
                            name: 'name',
                            xtype: 'textfield',
                            fieldLabel: __('Name'),
                            allowBlank: false,
                            uiStyle: 'large'
                        },
                        {
                            name: 'uuid',
                            xtype: 'displayfield',
                            style: 'padding-left: 10px',
                            fieldLabel: __('UUID')
                        }

                    ]
                },
                {
                    xtype: 'tabpanel',
                    layout: 'fit',
                    autoScroll: true,
                    anchor: '-0, -50',
                    defaults: {
                        autoScroll: true,
                        layout: 'anchor'
                    },
                    items: [ // tabs
                        {
                            title: __('Common'),
                            items: [
                                {
                                    name: 'description',
                                    xtype: 'textarea',
                                    fieldLabel: __('Description'),
                                    uiStyle: 'large'
                                },
                                {
                                    name: 'code',
                                    xtype: 'textfield',
                                    fieldLabel: __('Code'),
                                    allowBlank: true,
                                    uiStyle: 'large'
                                },
                                {
                                    name: 'category',
                                    xtype: 'textfield',
                                    fieldLabel: __('Category'),
                                    allowBlank: true,
                                    uiStyle: 'large'
                                },
                                {
                                    name: "format",
                                    xtype: "radiogroup",
                                    // columns: 3,
                                    vertical: true,
                                    fieldLabel: __("Report Format"),
                                    allowBlank: false,
                                    width: 600,
                                    items: [
                                        {boxLabel: __("By Datasource"), inputValue: 'B'},
                                        {boxLabel: __("By Source"), inputValue: 'S'},
                                        {boxLabel: __("By Template"), inputValue: 'T', checked: true}]
                                },
                                {
                                    name: "report_source",
                                    xtype: "main.ref.reportsource.LookupField",
                                    fieldLabel: __("Report Source"),
                                    allowBlank: true
                                },
                                {
                                    name: "hide",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Hide Report from UI"),
                                    allowBlank: false
                                }
                            ]
                        }, // Text
                        {
                            title: __('Bands'),
                            items: [
                                {
                                    xtype: "fieldset",
                                    title: __("Root Band"),
                                    items: [
                                        {
                                            name: "root_orientation",
                                            xtype: "combobox",
                                            fieldLabel: __("Orientation"),
                                            allowBlank: true,
                                            defaultValue: "H",
                                            store: [
                                                ["H", __("Horizontal")],
                                                ["V", __("Vertical")],
                                                ["C", __("Cross")],
                                                ["U", __("Undefined")]
                                            ]
                                        },
                                        {
                                            name: "root_queries",
                                            xtype: "gridfield",
                                            fieldLabel: __("Column Formats"),
                                            columns: [
                                                {
                                                    dataIndex: "datasource",
                                                    text: __("Datasource"),
                                                    renderer: NOC.render.Lookup('datasource'),
                                                    editor: 'main.ref.datasource.LookupField',
                                                    width: 200
                                                },
                                                {
                                                    dataIndex: "ds_query",
                                                    text: __("Query"),
                                                    editor: "textfield",
                                                    width: 300
                                                },
                                                {
                                                    text: __('Json Data'),
                                                    dataIndex: 'json',
                                                    editor: 'jsonfield',
                                                    flex: 1,
                                                    renderer: NOC.render.JSON
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    name: "bands",
                                    xtype: "listform",
                                    rows: 10,
                                    fieldLabel: __("Bands"),
                                    labelAlign: "top",
                                    items: [
                                        {
                                            name: "name",
                                            xtype: "textfield",
                                            fieldLabel: __("Code"),
                                            allowBlank: false
                                        },
                                        {
                                            name: "parent",
                                            xtype: "textfield",
                                            fieldLabel: __("Parent"),
                                            allowBlank: true
                                        },
                                        {
                                            name: "orientation",
                                            xtype: "combobox",
                                            fieldLabel: __("Orientation"),
                                            allowBlank: true,
                                            defaultValue: "H",
                                            store: [
                                                ["H", __("Horizontal")],
                                                ["V", __("Vertical")],
                                                ["C", __("Cross")],
                                                ["U", __("Undefined")]
                                            ]
                                        },
                                        {
                                            name: "queries",
                                            xtype: "gridfield",
                                            fieldLabel: __("Column Formats"),
                                            columns: [
                                                {
                                                    dataIndex: "datasource",
                                                    text: __("Datasource"),
                                                    editor: 'main.ref.datasource.LookupField',
                                                    renderer: NOC.render.Lookup('datasource'),
                                                    width: 200
                                                },
                                                {
                                                    dataIndex: "ds_query",
                                                    text: __("Query"),
                                                    editor: "textfield",
                                                    width: 300
                                                },
                                                {
                                                    text: __('Json Data'),
                                                    dataIndex: 'json',
                                                    editor: 'jsonfield',
                                                    flex: 1,
                                                    renderer: NOC.render.JSON
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }, // Text
                        {
                            title: __('Templates'),
                            items: [
                                {
                                    name: "templates",
                                    xtype: "listform",
                                    rows: 4,
                                    labelAlign: "top",
                                    items: [
                                        {
                                            name: "code",
                                            xtype: "textfield",
                                            fieldLabel: __("Code"),
                                            allowBlank: false
                                        },
                                        {
                                            name: "output_type",
                                            xtype: "combobox",
                                            fieldLabel: __("Output Type"),
                                            allowBlank: true,
                                            store: [
                                                ["csv", __("CSV")],
                                                ["pdf", __("PDF")],
                                                ["ssv", __("SSV")],
                                                ["html", __("HTML")]
                                            ]
                                        },
                                        {
                                            name: "output_name_pattern",
                                            xtype: "textfield",
                                            fieldLabel: __("Filename pattern")
                                        }
                                    ]
                                }
                            ]
                        }, // Components
                        {
                            title: __('Permissions'),
                            items: [
                                {
                                    name: 'permissions',
                                    xtype: 'gridfield',
                                    columns: [
                                        {
                                            text: __('User'),
                                            dataIndex: 'user',
                                            width: 250,
                                            renderer: NOC.render.Lookup('user'),
                                            editor: 'aaa.user.LookupField'
                                        },
                                        {
                                            text: __('Group'),
                                            dataIndex: 'group',
                                            width: 250,
                                            renderer: NOC.render.Lookup('group'),
                                            editor: 'aaa.group.LookupField'
                                        },
                                        {
                                            text: __("Edit"),
                                            dataIndex: "edit",
                                            width: 50,
                                            renderer: NOC.render.Bool,
                                            editor: "checkbox",
                                            defaultValue: false
                                        },
                                        {
                                            text: __("Launch"),
                                            dataIndex: "launch",
                                            width: 50,
                                            renderer: NOC.render.Bool,
                                            editor: "checkbox",
                                            defaultValue: true
                                        }
                                    ]
                                }
                            ]
                        }, // Permissions
                        {
                            title: __('Parameters'),
                            items: [
                                {
                                    name: 'parameters',
                                    xtype: 'gridfield',
                                    columns: [
                                        {
                                            text: __('Name'),
                                            dataIndex: 'name',
                                            width: 100,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Label'),
                                            dataIndex: 'label',
                                            width: 100,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __("Type"),
                                            dataIndex: "type",
                                            width: 100,
                                            editor: {
                                                xtype: "combobox",
                                                store: [
                                                    ["integer", __("Integer")],
                                                    ["string", __("String")],
                                                    ["date", __("Date")],
                                                    ["model", __("Model Lookup")]
                                                ]
                                            },
                                            renderer: NOC.render.Choices({
                                                "integer": __("Integer"),
                                                "string": __("String"),
                                                "date": __("Date"),
                                                "bool": __("Date"),
                                                "model": __("Model Lookup")
                                            })
                                        },
                                        {
                                            text: __("Is Required"),
                                            dataIndex: "required",
                                            width: 50,
                                            renderer: NOC.render.Bool,
                                            editor: "checkbox"
                                        },
                                        {
                                            text: __('ModelID'),
                                            dataIndex: 'model_id',
                                            renderer: NOC.render.Lookup('model_id'),
                                            editor: 'main.ref.modelid.LookupField',
                                            width: 200
                                        },
                                        {
                                            text: __('Default'),
                                            dataIndex: 'default',
                                            width: 150,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Description'),
                                            dataIndex: 'description',
                                            flex: 1,
                                            editor: 'textfield'
                                        }
                                    ]
                                }
                            ]
                        }, // Band Format
                        {
                            title: __('Band Format'),
                            items: [
                                {
                                    name: "bands_format",
                                    xtype: "listform",
                                    rows: 10,
                                    labelAlign: "top",
                                    items: [
                                        {
                                            name: "name",
                                            xtype: "textfield",
                                            fieldLabel: __("Band Name"),
                                            allowBlank: false
                                        },
                                        {
                                            name: "title_template",
                                            xtype: "textfield",
                                            fieldLabel: __("Title Template"),
                                            allowBlank: true
                                        },
                                        {
                                            name: "column_format",
                                            xtype: "gridfield",
                                            fieldLabel: __("Format Columns"),
                                            columns: [
                                                {
                                                    dataIndex: "name",
                                                    text: __("Name"),
                                                    editor: "textfield",
                                                    width: 150
                                                },
                                                {
                                                    dataIndex: "title",
                                                    text: __("Title"),
                                                    editor: "textfield",
                                                    width: 100
                                                },
                                                {
                                                    text: __("Align"),
                                                    dataIndex: "align",
                                                    width: 100,
                                                    editor: {
                                                        xtype: "combobox",
                                                        store: [
                                                            ["1", __("Left")],
                                                            ["2", __("Right")],
                                                            ["3", __("Center")],
                                                            ["4", __("Mask")]
                                                        ]
                                                    },
                                                    renderer: NOC.render.Choices({
                                                        "1": __("Left"),
                                                        "2": __("Right"),
                                                        "3": __("Center"),
                                                        "4": __("Mask")
                                                    })
                                                },
                                                {
                                                    text: __("Type"),
                                                    dataIndex: "format_type",
                                                    width: 100,
                                                    editor: {
                                                        xtype: "combobox",
                                                        store: [
                                                            ["integer", __("Integer")],
                                                            ["string", __("String")],
                                                            ["float", __("Float")]
                                                        ]
                                                    },
                                                    renderer: NOC.render.Choices({
                                                        "integer": __("Integer"),
                                                        "string": __("String"),
                                                        "float": __("Float")
                                                    })
                                                },
                                                {
                                                    text: __("Total"),
                                                    dataIndex: "total",
                                                    width: 100,
                                                    editor: {
                                                        xtype: "combobox",
                                                        store: [
                                                            ["sum", __("Sum")],
                                                            ["count", __("Count")]
                                                        ]
                                                    },
                                                    renderer: NOC.render.Choices({
                                                        "sum": __("Sum"),
                                                        "count": __("Count")
                                                    })
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        } // Components

                    ]
                }
            ],
            formToolbar: [
                {
                    text: __('JSON'),
                    glyph: NOC.glyph.file,
                    tooltip: __('View as JSON'),
                    hasAccess: NOC.hasPermission('read'),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    filters: [
        {
            title: __('By Builtin'),
            name: 'is_builtin',
            ftype: 'boolean'
        }
    ],
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
