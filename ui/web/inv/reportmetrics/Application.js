//---------------------------------------------------------------------
// inv.reportmetricdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.reportmetrics.Application");

Ext.define("NOC.inv.reportmetrics.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ReportControl",
        "NOC.inv.networksegment.TreeCombo",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.sa.administrativedomain.TreeCombo",
        "NOC.sa.managedobjectselector.LookupField"
    ],
    interfaceData: [
        ["id", __("ID"), false],
        ["object_name", __("Object Name"), true],
        ["object_address", __("IP"), true],
        ["object_platform", __("Object Platform"), true],
        ["object_adm_domain", __("Object Administrative domain"), true],
        ["object_segment", __("Object Segemnt"), false],
        ["object_container", __("Object Geo Address"), false],
        ["iface_name", __("Interface Name"), true],
        ["iface_description", __("Interface Description"), true],
        ["iface_speed", __("Interface Speed"), false],
        ["load_in", __("Load In"), true],
        ["load_in_p", __("Load In (% Bandwith)"), false],
        ["load_out", __("Load Out"), true],
        ["load_out_p", __("Load Out (% Bandwith)"), false],
        ["errors_in", __("Errors In"), true],
        ["errors_out", __("Errors Out"), true],
        ["interface_flap", __("Interface Flap count"), false],
        ["interface_load_url", __("Interface Load URL"), false]
    ],
    objectData: [
        ["id", __("ID"), false],
        ["object_name", __("Object Name"), true],
        ["object_address", __("IP"), true],
        ["object_platform", __("Object Platform"), true],
        ["object_adm_domain", __("Object Administrative domain"), true],
        ["object_segment", __("Object Segemnt"), false],
        ["object_container", __("Object Geo Address"), false],
        ["slot", __("Slot"), false],
        ["cpu_usage", __("CPU Usage"), true],
        ["memory_usage", __("Memory Usage"), true]
    ],
    availabilityData: [
        ["id", __("ID"), false],
        ["object_name", __("Object Name"), true],
        ["object_address", __("IP"), true],
        ["object_platform", __("Object Platform"), true],
        ["object_adm_domain", __("Object Administrative domain"), true],
        ["object_segment", __("Object Segemnt"), false],
        ["object_container", __("Object Geo Address"), false],
        ["ping_rtt", __("Ping RTT"), true],
        ["ping_attempts", __("Ping Attempts"), true]
    ],
    otherData: [
        ["id", __("ID"), false],
        ["object_name", __("Other Data"), true]
    ],
    defaultListenerScope: true,
    items: {
        xtype: "report.control",
        url: "/inv/reportmetrics",
        controls: [
            {
                name: "reporttype",
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
                    {boxLabel: 'Interfaces', name: 'reporttype', inputValue: 'load_interfaces', checked: true},
                    {boxLabel: 'Objects', name: 'reporttype', inputValue: 'load_cpu'},
                    {boxLabel: 'Ping', name: 'reporttype', inputValue: 'ping'},
                    {boxLabel: 'Other', name: 'reporttype', inputValue: 'other'}
                ],
                listeners: {
                    change: 'onChangeSource'
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
                name: "selector",
                xtype: "sa.managedobjectselector.LookupField",
                fieldLabel: __("By Selector"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                width: 500,
                allowBlank: true
            },
            {
                name: "interface_profile",
                xtype: "inv.interfaceprofile.LookupField",
                fieldLabel: __("By Interface Profile"),
                listWidth: 1,
                listAlign: 'left',
                labelAlign: "left",
                width: 500,
                allowBlank: true
            },
            {
                name: "exclude_zero",
                xtype: "checkboxfield",
                boxLabel: __("Filter interface has zero load"),
                allowBlank: false,
                defaultValue: false
            }
        ]
    },

    initComponent: function() {
        this.callParent();
        // ToDo need sync with radio "Metric source" checked value
        this.onChangeSource(null, {reporttype: "load_interfaces"});
    },

    onChangeSource: function(self, newVal) {
        var me = this, data,
            store = me.down("[xtype=grid]").getStore();
        switch(newVal.reporttype) {
            case "load_interfaces":
                data = me.interfaceData;
                break;
            case "load_cpu":
                data = me.objectData;
                break;
            case "ping":
                data = me.availabilityData;
                break;
            default:
                data = me.otherData;
        }
        store.loadData(data);
    }
});
