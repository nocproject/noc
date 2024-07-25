// fm.reportalarmdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.reportalarmdetail.Application");

Ext.define("NOC.fm.reportalarmdetail.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ReportControl",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.sa.administrativedomain.TreeCombo",
        'NOC.inv.resourcegroup.TreeCombo',
        "NOC.core.tagfield.Tagfield"
    ],

    initComponent: function() {
        var me = this;
        if(me.noc && me.noc.cmd && me.noc.cmd.ids) {
            me.items.controls = [
                {
                    name: "ids",
                    xtype: "displayfield",
                    fieldLabel: __("Alarms"),
                    value: me.noc.cmd.ids.join(" ")
                }
            ];
        } else {
            me.items.controls = [
                // {
                //     name: "source",
                //     xtype: "segmentedbutton",
                //     allowBlank: false,
                //     width: 300,
                //     items: [
                //         {text: __("Active Alarms"), value: 'active', pressed: true},
                //         {text: __("Archived Alarms"), value: 'archived'},
                //         {text: __("Both"), value: 'both'}
                //     ]
                // },
                {
                    name: "source",
                    xtype: "radiogroup",
                    columns: 4,
                    vertical: false,
                    fieldLabel: __("Alarms source"),
                    allowBlank: false,
                    width: 600,
                    items: [
                        {boxLabel: __("Active Alarms"), inputValue: 'active', checked: true},
                        {boxLabel: __("Archived Alarms"), inputValue: 'archived'},
                        {boxLabel: __("Both"), inputValue: 'both'},
                        {boxLabel: __("Long Alarm Archive (more 3 months)"), inputValue: 'long_archive'}]
                },
                {
                    name: "from_date",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("From"),
                    allowBlank: false,
                    format: "d.m.Y",
                    submitFormat: "d.m.Y"
                },
                {
                    name: "to_date",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("To"),
                    allowBlank: false,
                    format: "d.m.Y",
                    submitFormat: "d.m.Y"
                },
                {
                    name: "segment",
                    xtype: "inv.networksegment.TreeCombo",
                    fieldLabel: __("Segment"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500
                },
                {
                    name: "administrative_domain",
                    xtype: "sa.administrativedomain.TreeCombo",
                    fieldLabel: __("By Adm. domain"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true
                },
                {
                    name: "resource_group",
                    xtype: "inv.resourcegroup.TreeCombo",
                    fieldLabel: __("By Resource Group (Selector)"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true
                },
                {
                    name: "ex_resource_group",
                    xtype: "inv.resourcegroup.TreeCombo",
                    fieldLabel: __("Exclude MO by Resource Group (Selector)"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true
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
                {
                    name: "enable_autowidth",
                    xtype: "checkboxfield",
                    boxLabel: __("Enable Excel column autowidth"),
                    allowBlank: false
                },
                {
                    name: "subscribers",
                    xtype: "core.tagfield",
                    url: "/crm/subscriberprofile/lookup/",
                    fieldLabel: __("Subscribers that Sum"),
                    allowBlank: true,
                    uiStyle: undefined,
                    width: "45%"
                }
            ];
        }
        me.callParent();
    },
    items: {
        xtype: "report.control",
        url: "/fm/reportalarmdetail",
        storeData: [
            ["alarm_id", __("ID"), true],
            ["root_id", __("Root ID"), true],
            ["from_ts", __("From"), true],
            ["to_ts", __("To"), true],
            ["duration_sec", __("Duration"), true],
            ["object_name", __("Object Name"), true],
            ["object_address", __("IP"), true],
            ["object_hostname", __("Hostname"), true],
            ["object_profile", __("Profile"), true],
            ["object_object_profile", __("Object Profile"), true],
            ["object_admdomain", __("Administrative Domain"), true],
            ["object_platform", __("Platform"), true],
            ["object_version", __("Version"), true],
            ["object_project", __("Project"), true],
            ["alarm_class", __("Alarm Class"), true],
            ["alarm_subject", __("Alarm Subject"), false],
            ["maintenance", __("Maintenance"), true],
            ["objects", __("Affected Objects"), true],
            ["subscribers", __("Affected Subscriber"), true],
            ["tt", __("TT"), true],
            ["escalation_ts", __("Escalation Time"), true],
            ["location", __("Location"), true],
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
    }
});
