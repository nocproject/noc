//---------------------------------------------------------------------
// inv.reportmetricdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportmetricdetail.Application");

Ext.define("NOC.inv.reportmetricdetail.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField"
    ],

    initComponent: function() {
        var me = this;

        me.interfaceData = [
            ["id", __("ID"), false],
            ["object_name", __("Object Name"), true],
            ["object_address", __("IP"), true],
            ["iface_name", __("Interface Name"), true],
            ["load_in", __("Load In"), true],
            ["load_out", __("Load Out"), true],
            ["errors_in", __("Errors In"), true],
            ["errors_out", __("Errors Out"), true]
        ];
        me.objectData = [
            ["id", __("ID"), false],
            ["object_name", __("Object Name"), true],
            ["object_address", __("IP"), true],
            ["cpu_usage", __("CPU Usage"), true],
            ["memory_usage", __("Memory Usage"), true]
        ];
        me.otherData = [
            ["id", __("ID"), false],
            ["object_name", __("Other Data"), true]
        ];
        me.columnsStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label", {
                name: "is_active",
                type: "boolean"
            }],
            data: me.interfaceData
        });

        me.columnsGrid = Ext.create("Ext.grid.Panel", {
            store: me.columnsStore,
            autoScroll: true,
            columns: [
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Field"),
                    dataIndex: "label",
                    flex: 1
                }
            ],
            selModel: "cellmodel",
            plugins: [
                {
                    ptype: "cellediting",
                    clicksToEdit: 1
                }
            ],
            viewConfig: {
                plugins: {
                    ptype: 'gridviewdragdrop',
                    dragText: 'Drag and drop to reorganize'
                }
            }
        });

        me.formatButton = Ext.create("Ext.button.Segmented", {
            width: 150,
            items: [
                {
                    text: __("CSV"),
                    width: 70
                },
                {
                    text: __("Excel"),
                    pressed: true,
                    width: 70
                }
            ]
        });

        me.adm_domain = null;
        me.segment = null;
        me.selector = null;

        me.formPanel = Ext.create("Ext.form.Panel", {
            autoScroll: true,
            defaults: {
                padding: "0 10 10 10",
                labelWidth: 120
            },
            items: [
                {
                    name: "metric_source",
                    xtype: "radiogroup",
                    columns: 3,
                    vertical: false,
                    fieldLabel: __("Metric source"),
                    allowBlank: false,
                    margin: 0,
                    width: 300,
                    defaults: {
                        padding: "0 5"
                    },
                    items: [
                        {boxLabel: 'Interfaces', name: 'rb', inputValue: 'interface', checked: true},
                        {boxLabel: 'Objects', name: 'rb', inputValue: 'object'},
                        {boxLabel: 'Other', name: 'rb', inputValue: 'other'}
                    ],
                    listeners: {
                        scope: me,
                        change: me.onChangeSource
                    }
                },
                {
                    name: "from_date",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("From"),
                    allowBlank: false,
                    format: "d.m.Y",
                    margin: 0,
                    width: 210
                },
                {
                    name: "to_date",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("To"),
                    allowBlank: false,
                    format: "d.m.Y",
                    margin: 0,
                    width: 210
                },
                {
                    name: "segment",
                    xtype: "inv.networksegment.TreeCombo",
                    fieldLabel: __("Segment"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.segment = record.get("id")
                        }
                    }
                },
                {
                    name: "administrative_domain",
                    xtype: "sa.administrativedomain.TreeCombo",
                    fieldLabel: __("By Adm. domain"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.adm_domain = record.get("id")
                        }
                    }
                },
                {
                    name: "Selector",
                    xtype: "sa.managedobjectselector.LookupField",
                    fieldLabel: __("By Selector"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.selector = record.get("id")
                        }
                    }
                },
                me.formatButton,
                me.columnsGrid
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Download"),
                            glyph: NOC.glyph.download,
                            scope: me,
                            handler: me.onDownload,
                            formBind: true
                        }
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [me.formPanel]
        });
        me.callParent();
    },

    onDownload: function() {
        var me = this,
            v = me.formPanel.getValues(),
            format = "csv",
            url,
            columns = [];

        if(me.formatButton.items.items[1].pressed) {
            format = "xlsx"
        }

        url = [
            "/inv/reportmetricdetail/download/?o_format=" + format
            + "&from_date=" + v.from_date + "&to_date=" + v.to_date
        ];

        if(me.adm_domain) {
            url.push("&administrative_domain=" + me.adm_domain);
        }

        if(me.segment) {
            url.push("&segment=" + me.segment);
        }

        if(me.selector) {
            url.push("&selector=" + me.selector);
        }

        me.columnsStore.each(function(record) {
            if(record.get("is_active")) {
                columns.push(record.get("id"));
            }
        });

        url.push("&columns=" + columns.join(","));

        window.open(url.join(""));
    },
    //
    onChangeSource: function(self, newVal) {
        var me = this, data = me.otherData;
        switch(newVal.rb) {
            case "interface":
                data = me.interfaceData;
                break;
            case "object":
                data = me.objectData;
                break;
        }
        me.columnsStore.loadData(data);
    }
});
