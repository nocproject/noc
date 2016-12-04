//---------------------------------------------------------------------
// vc.vcbindfilter application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcbindfilter.Application");

Ext.define("NOC.vc.vcbindfilter.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vcbindfilter.Model",
        "NOC.vc.vcdomain.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.vc.vcfilter.LookupField"
    ],
    model: "NOC.vc.vcbindfilter.Model",
    columns: [
        {
            text: __("VC Domain"),
            renderer: NOC.render.Lookup("vc_domain"),
            dataIndex: "vc_domain"
        },
        {
            text: __("VRF"),
            dataIndex: "vrf",
            renderer: NOC.render.Lookup("vrf")
        },
        {
            text: __("AFI"),
            dataIndex: "afi",
            renderer: function(v) {
                return "IPv" + v;
            }
        },
        {
            text: __("Prefix"),
            dataIndex: "prefix"
        },
        {
            text: __("VC Filter"),
            dataIndex: "vc_filter",
            renderer: NOC.render.Lookup("vc_filter")
        },
        {
            text: __("VC Filter Expression"),
            dataIndex: "vc_filter_expression",
            flex: 1
        }
    ],
    fields: [
        {
            name: "vc_domain",
            xtype: "vc.vcdomain.LookupField",
            fieldLabel: __("VC Domain"),
            allowBlank: false
        },
        {
            name: "vrf",
            xtype: "ip.vrf.LookupField",
            fieldLabel: __("VRF"),
            allowBlank: false
        },
        {
            name: "afi",
            xtype: "combobox",
            fieldLabel: __("Address Family"),
            allowBlank: false,
            store: [["4", "IPv4"], ["6", "IPv6"]]
        },
        {
            name: "prefix",
            xtype: "textfield",
            fieldLabel: __("Prefix"),
            allowBlank: false
        },
        {
            name: "vc_filter",
            xtype: "vc.vcfilter.LookupField",
            fieldLabel: __("VC Filter"),
            allowBlank: false
        }
    ],
    filters: [
        {
            name: "afi",
            title: __("By Address Family"),
            ftype: "afi"
        }
    ]
});
