//---------------------------------------------------------------------
// peer.maintainer application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.as.Application");

Ext.define("NOC.peer.as.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.RepoPreview",
        "NOC.peer.as.Model",
        "NOC.peer.asprofile.LookupField",
        "NOC.peer.person.M2MField",
        "NOC.peer.maintainer.M2MField",
        "NOC.peer.rir.LookupField",
        "NOC.peer.organisation.LookupField",
        "NOC.project.project.LookupField"
    ],
    model: "NOC.peer.as.Model",
    rowClassField: "row_class",
    search: true,
    columns: [
        {
            text: __("AS"),
            dataIndex: "asn",
            width: 50
        },
        {
            text: __("Profile"),
            dataIndex: "profile",
            width: 100,
            renderer: NOC.render.Lookup("profile")
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 1
        },
        {
            text: __("RIR"),
            dataIndex: "rir",
            renderer: NOC.render.Lookup("rir"),
            width: 100
        }
    ],
    fields: [
        {
            name: "asn",
            xtype: "textfield",
            fieldLabel: __("AS"),
            allowBlank: false,
            uiStyle: "medium",
            vtype: "ASN"
        },
        {
            name: "profile",
            xtype: "peer.asprofile.LookupField",
            fieldLabel: __("Profile"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: __("Description"),
            allowBlank: false
        },
        {
            name: "rir",
            xtype: "peer.rir.LookupField",
            fieldLabel: __("RIR"),
            allowBlank: true
        },
        {
            name: "project",
            xtype: "project.project.LookupField",
            fieldLabel: __("Project"),
            allowBlank: true
        },
        {
            name: "organisation",
            xtype: "peer.organisation.LookupField",
            fieldLabel: __("Organisation"),
            allowBlank: true
        },
        {
            name: "administrative_contacts",
            xtype: "peer.person.M2MField",
            fieldLabel: __("Admin-c"),
            buttons: ['add', 'remove'],
            allowBlank: true
        },
        {
            name: "tech_contacts",
            xtype: "peer.person.M2MField",
            fieldLabel: __("Tech-c"),
            buttons: ['add', 'remove'],
            allowBlank: true
        },
        {
            name: "maintainers",
            xtype: "peer.maintainer.M2MField",
            fieldLabel: __("Maintainers"),
            buttons: ['add', 'remove'],
            allowBlank: true
        },
        {
            name: "route_maintainers",
            xtype: "peer.maintainer.M2MField",
            fieldLabel: __("Route Maintainers"),
            buttons: ['add', 'remove'],
            allowBlank: true
        },
        {
            name: "header_remarks",
            xtype: "textarea",
            fieldLabel: __("Header Remarks"),
            allowBlank: true,
            width: 600,
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "footer_remarks",
            xtype: "textarea",
            fieldLabel: __("Footer Remarks"),
            allowBlank: true,
            width: 600,
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        }
    ],
    preview: {
        xtype: "NOC.core.RepoPreview",
        syntax: "rpsl",
        previewName: 'AS RPSL: {0}',
        restUrl: '/peer/as/{0}/repo/rpsl/'
    }
});
