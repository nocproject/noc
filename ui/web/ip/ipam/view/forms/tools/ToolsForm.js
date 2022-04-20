//---------------------------------------------------------------------
// ip.ipam.tools form
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.tools.ToolsForm");

Ext.define("NOC.ip.ipam.view.forms.tools.ToolsForm", {
    extend: "Ext.form.Panel",
    alias: "widget.ip.ipam.form.tools",
    controller: "ip.ipam.form.tools",
    viewModel: "ip.ipam.form.tools",
    requires: [
        "NOC.core.ComboBox",
        "NOC.ip.ipam.view.forms.tools.ToolsController",
        "NOC.ip.ipam.view.forms.tools.ToolsModel",
    ],

    layout: 'anchor',
    border: true,
    padding: 4,
    bodyPadding: 4,
    defaultType: 'textfield',
    items: [
        {
            xtype: "container",
            bind: {
                html: "VRF:" + "{prefix.vrf__label} {prefix.name} " + __("tools")
            },
            padding: "0 0 4 0",
            style: {
                fontSize: "1.2em",
                fontWeight: "bold"
            }
        },
        {
            fieldLabel: __("NS"),
            name: "ns",
            allowBlank: false,
            bind: {
                value: "{ns}"
            }
        },
        {
            fieldLabel: __("Zone"),
            name: "zone",
            allowBlank: false,
            bind: {
                value: "{zone}"
            }
        },
        {
            fieldLabel: __("Source Address"),
            name: "source",
            allowBlank: true,
            bind: {
                value: "{source}"
            }
        }
    ],

    tbar: [
        {
            text: __("Close"),
            tooltip: __("Close form"),
            glyph: NOC.glyph.arrow_left,
            handler: "onClose"
        },
        "-",
        {
            text: __("Download"),
            tooltip: __("Download list of allocated IP addresses in CSV format"),
            glyph: NOC.glyph.download,
            handler: "onDownload"
        },
        {
            text: __("Start zone transfer"),
            tooltip: __("Upload list of allocated IP addresses from existing DNS servers via AXFR request"),
            glyph: NOC.glyph.upload,
            bind: {
                disabled: "{!isValid}"
            },
            handler: "onStartZoneTransfer"
        },
    ]
});
