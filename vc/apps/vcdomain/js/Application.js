//---------------------------------------------------------------------
// vc.vcdomain application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcdomain.Application");

Ext.define("NOC.vc.vcdomain.Application", {
    extend: "NOC.core.ModelApplication",
    model: "NOC.vc.vcdomain.Model",
    requires: [
        "NOC.main.style.LookupField",
        "NOC.vc.vcdomain.Model",
        "NOC.vc.vctype.LookupField"
    ],
    search: true,
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },

        {
            text: "Type",
            dataIndex: "type",
            renderer: NOC.render.Lookup("type")
        },

        {
            text: "Provisioning",
            dataIndex: "enable_provisioning",
            renderer: noc_renderBool
        },

        {
            text: "Bind filter",
            dataIndex: "enable_vc_bind_filter",
            renderer: noc_renderBool
        },

        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true,
            anchor: "100%"
        },
        {
            name: "type",
            xtype: "vc.vctype.LookupField",
            fieldLabel: "VC Type"
        },
        {
            name: "enable_provisioning",
            xtype: "checkboxfield",
            boxLabel: "Enable Provisioning"
        },
        {
            name: "enable_vc_bind_filter",
            xtype: "checkboxfield",
            boxLabel: "Enable VC Bind filter"
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By VC Type",
            name: "type",
            ftype: "lookup",
            lookup: "vc.vctype"
        },
        {
            title: "By Provisioning",
            name: "enable_provisioning",
            ftype: "boolean"
        },
        {
            title: "By Bind Filter",
            name: "enable_vc_bind_filter",
            ftype: "boolean"
        }
    ]
});
