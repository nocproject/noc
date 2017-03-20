//---------------------------------------------------------------------
// fm.reportalarmdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.reportalarmdetail.Application");

Ext.define("NOC.fm.reportalarmdetail.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.inv.networksegment.TreeCombo"
    ],

    initComponent: function() {
        var me = this;

        me.columnsStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label", {
                name: "is_active",
                type: "boolean"
            }],
            data: [
                ["id", __("ID"), true],
                ["root_id", __("Root ID"), true],
                ["from_ts", __("From"), true],
                ["to_ts", __("To"), true],
                ["duration_sec", __("Duration"), true],
                ["object_name", __("Object Name"), true],
                ["object_address", __("IP"), true],
                ["object_platform", __("Platform"), true],
                ["alarm_class", __("Alarm Class"), true],
                ["objects", __("Affected Objects"), true],
                ["subscribers", __("Affected Subscriber"), true],
                ["tt", __("TT"), true],
                ["escalation_ts", __("Escalation Time"), true],
                ["container_0", __("Container (Level 1)"), true],
                ["container_1", __("Container (Level 2)"), true],
                ["container_2", __("Container (Level 3)"), true],
                ["container_3", __("Container (Level 4)"), true],
                ["container_4", __("Container (Level 5)"), true],
                ["container_5", __("Container (Level 6)"), true],
                ["container_6", __("Container (Level 7)"), true],
                ["segment_0", __("Segment (Level 1)"), true],
                ["segment_1", __("Segment (Level 2)"), true],
                ["segment_2", __("Segment (Level 3)"), true],
                ["segment_3", __("Segment (Level 4)"), true],
                ["segment_4", __("Segment (Level 5)"), true],
                ["segment_5", __("Segment (Level 6)"), true],
                ["segment_6", __("Segment (Level 7)"), true]
            ]
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
            items: [
                {
                    text: __("CSV"),
                    pressed: true,
                    width: 70
                },
                {
                    text: __("Excel"),
                    width: 70
                }
            ],
            anchor: null
        });

        me.segment = null;

        me.formPanel = Ext.create("Ext.form.Panel", {
            autoScroll: true,
            defaults: {
                labelWidth: 60
            },
            items: [
                {
                    name: "from_date",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("From"),
                    allowBlank: false,
                    format: "d.m.Y",
                    width: 150
                },
                {
                    name: "to_date",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("To"),
                    allowBlank: false,
                    format: "d.m.Y",
                    width: 150
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
                    name: "min_duration",
                    xtype: "numberfield",
                    fieldLabel: __("Min. Duration"),
                    allowBlank: false,
                    value: 300,
                    uiStyle: "small"
                },
                {
                    name: "min_objects",
                    xtype: "numberfield",
                    fieldLabel: __("Min. Objects"),
                    allowBlank: true,
                    value: 0,
                    uiStyle: "small"
                },
                {
                    name: "min_subscribers",
                    xtype: "numberfield",
                    fieldLabel: __("Min. Subscribers"),
                    allowBlank: true,
                    value: 0,
                    uiStyle: "small"
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
            "/fm/reportalarmdetail/download/?from_date="
            + v.from_date + "&to_date=" + v.to_date
            + "&format=" + format + "&min_duration=" + v.min_duration
            + "&min_objects=" + v.min_objects
            + "&min_subscribers=" + v.min_subscribers
        ];

        if(me.segment) {
            url.push("&segment=" + me.segment);
        }

        me.columnsStore.each(function(record) {
            if(record.get("is_active")) {
                columns.push(record.get("id"));
            }
        });

        url.push("&columns=" + columns.join(","));

        window.open(url.join(""));
    }
});
