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
            text: "VC Domain",
            dataIndex: "vc_domain__label"
        },
        {
            text: "VRF",
            dataIndex: "vrf__label"
        },
        {
            text: "AFI",
            dataIndex: "afi",
            renderer: function(v) {
                return "IPv" + v;
            }
        },
        {
            text: "Prefix",
            dataIndex: "prefix"
        },
        {
            text: "VC Filter",
            dataIndex: "vc_filter__label"
        },
        {
            text: "VC Filter Expression",
            dataIndex: "vc_filter_expression",
            flex: 1
        }
    ],
    fields: [
        {
            name: "vc_domain",
            xtype: "vc.vcdomain.LookupField",
            fieldLabel: "VC Domain",
            allowBlank: false
        },
        {
            name: "vrf",
            xtype: "ip.vrf.LookupField",
            fieldLabel: "VRF",
            allowBlank: false
        },
        {
            name: "afi",
            xtype: "combobox",
            fieldLabel: "Address Family",
            allowBlank: false,
            store: [["4", "IPv4"], ["6", "IPv6"]]
        },
        {
            name: "prefix",
            xtype: "textfield",
            fieldLabel: "Prefix",
            allowBlank: false
        },
        {
            name: "vc_filter",
            xtype: "vc.vcfilter.LookupField",
            fieldLabel: "VC Filter",
            allowBlank: false
        }
    ],
    filters: [
        {
            name: "afi",
            title: "By Address Family",
            ftype: "afi"
        }
    ]
});
