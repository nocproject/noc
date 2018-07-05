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
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField"
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
                ["object_hostname", __("Hostname"), true],
                ["object_profile", __("Profile"), true],
                ["object_admdomain", __("Administrative Domain"), true],
                ["object_platform", __("Platform"), true],
                ["object_version", __("Version"), true],
                ["alarm_class", __("Alarm Class"), true],
                ["alarm_subject", __("Alarm Subject"), false],
                ["maintenance", __("Maintenance"), true],
                ["objects", __("Affected Objects"), true],
                ["subscribers", __("Affected Subscriber"), true],
                ["tt", __("TT"), true],
                ["escalation_ts", __("Escalation Time"), true],
                ["location", __("Location"), true],
                ["container_address", __("Container Address"), false],
                ["container_0", __("Container (Level 1)"), false],
                ["container_1", __("Container (Level 2)"), false],
                ["container_2", __("Container (Level 3)"), false],
                ["container_3", __("Container (Level 4)"), false],
                ["container_4", __("Container (Level 5)"), false],
                ["container_5", __("Container (Level 6)"), false],
                ["container_6", __("Container (Level 7)"), false],
                ["segment_0", __("Segment (Level 1)"), false],
                ["segment_1", __("Segment (Level 2)"), false],
                ["segment_2", __("Segment (Level 3)"), false],
                ["segment_3", __("Segment (Level 4)"), false],
                ["segment_4", __("Segment (Level 5)"), false],
                ["segment_5", __("Segment (Level 6)"), false],
                ["segment_6", __("Segment (Level 7)"), false]
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
                    width: 70
                },
                {
                    text: __("Excel"),
                    pressed: true,
                    width: 70
                }
            ],
            anchor: null
        });

        me.segment = null;
        me.adm_domain = null;
        me.selector = null;
        me.ex_selector = null;

        me.formPanel = Ext.create("Ext.form.Panel", {
            autoScroll: true,
            defaults: {
                labelWidth: 60
            },
            items: [
                {
                    name: "alarms_source",
                    xtype: "radiogroup",
                    columns: 3,
                    vertical: false,
                    fieldLabel: __("Alarms source"),
                    allowBlank: false,
                    width: 300,
                    items: [
                        {boxLabel: 'Active Alarms', name: 'rb', inputValue: 'active', checked: true},
                        {boxLabel: 'Archived Alarms', name: 'rb', inputValue: 'archive'},
                        {boxLabel: 'Both', name: 'rb', inputValue: 'both'}]
                },
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
                    name: "administrative_domain",
                    xtype: "sa.administrativedomain.TreeCombo",
                    fieldLabel: __("By Adm. domain"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    labelWidth: 100,
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
                    labelWidth: 100,
                    width: 500,
                    allowBlank: true,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.selector = record.get("id")
                        }
                    }
                },
                {
                    name: "Exclude selector",
                    xtype: "sa.managedobjectselector.LookupField",
                    fieldLabel: __("Exclude MO by Selector"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    labelWidth: 100,
                    width: 500,
                    allowBlank: true,
                    listeners: {
                        scope: me,
                        select: function(combo, record) {
                            me.ex_selector = record.get("id")
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
                    name: "max_duration",
                    xtype: "numberfield",
                    fieldLabel: __("Max. Duration"),
                    allowBlank: false,
                    value: 0,
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
            + "&source=" + v.rb
        ];

        if(me.segment) {
            url.push("&segment=" + me.segment);
        }

        if(me.adm_domain) {
            url.push("&administrative_domain=" + me.adm_domain);
        }
        if(me.selector) {
            url.push("&selector=" + me.selector);
        }
        if(me.ex_selector) {
            url.push("&ex_selector=" + me.ex_selector);
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
