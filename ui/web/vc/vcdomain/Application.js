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
            text: __("Name"),
            dataIndex: "name"
        },

        {
            text: __("Type"),
            dataIndex: "type",
            renderer: NOC.render.Lookup("type")
        },

        {
            text: __("Object Count"),
            dataIndex: "object_count",
            align: "right",
            sortable: false,
            width: 50
        },

        {
            text: __("Provisioning"),
            dataIndex: "enable_provisioning",
            renderer: NOC.render.Bool
        },

        {
            text: __("Bind filter"),
            dataIndex: "enable_vc_bind_filter",
            renderer: NOC.render.Bool
        },

        {
            text: __("Description"),
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true,
            anchor: "100%"
        },
        {
            name: "type",
            xtype: "vc.vctype.LookupField",
            fieldLabel: __("VC Type")
        },
        {
            name: "enable_provisioning",
            xtype: "checkboxfield",
            boxLabel: __("Enable Provisioning")
        },
        {
            name: "enable_vc_bind_filter",
            xtype: "checkboxfield",
            boxLabel: __("Enable VC Bind filter")
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: __("Style"),
            allowBlank: true
        }
    ],
    filters: [
        {
            title: __("By VC Type"),
            name: "type",
            ftype: "lookup",
            lookup: "vc.vctype"
        },
        {
            title: __("By Provisioning"),
            name: "enable_provisioning",
            ftype: "boolean"
        },
        {
            title: __("By Bind Filter"),
            name: "enable_vc_bind_filter",
            ftype: "boolean"
        }
    ]
});
