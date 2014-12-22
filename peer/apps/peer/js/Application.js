//---------------------------------------------------------------------
// peer.peer application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peer.Application");

Ext.define("NOC.peer.peer.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.peer.Model",
        "NOC.peer.peeringpoint.LookupField",
        "NOC.peer.peergroup.LookupField",
        "NOC.project.project.LookupField",
        "NOC.peer.as.LookupField"
    ],
    model: "NOC.peer.peer.Model",
    search: true,
    columns: [
        {
            text: "Peering Point",
            flex: 1,
            dataIndex: "peering_point",
            renderer: NOC.render.Lookup("peering_point")
        },
        {
            text: "Peer Group",
            flex: 1,
            dataIndex: "peer_group",
            renderer: NOC.render.Lookup("peer_group")
        },
        {
            text: "Project",
            dataIndex: "project",
            renderer: NOC.render.Lookup("project")
        },
        {
            text: "Local AS",
            flex: 1,
            dataIndex: "local_asn",
            renderer: NOC.render.Lookup("local_asn")
        },
        {
            text: "Remote AS",
            flex: 1,
            dataIndex: "remote_asn"
        },
        {
            text: "Status",
            width: 70,
            dataIndex: "status",
            renderer: function(a) {
                return {P: "Planned", A: "Active",
                        S: "Shutdown"}[a];
            }
        },
        {
            text: "Import Filter",
            flex: 1,
            dataIndex: "import_filter"
        },
        {
            text: "Export Filter",
            flex: 1,
            dataIndex: "export_filter"
        },
        {
            text: "Local Address",
            flex: 1,
            dataIndex: "local_ip"
        },
        {
            text: "Remote Address",
            flex: 1,
            dataIndex: "remote_ip"
        },
        {
            text: "TT",
            flex: 1,
            dataIndex: "tt"
        },
        {
            text: "Description",
            flex: 1,
            dataIndex: "description"
        }, 
        {
            text: "Import Communities",
            flex: 1,
            dataIndex: "communities"
        }, 
        {
            text: "Tags",
            flex: 1,
            dataIndex: "tags",
            renderer: "NOC.render.Tags"
        }
    ],
    fields: [
        {
            xtype: "fieldset",
            title: "Peering",
            collapsible: false,
            defaults: {
                labelWidth: 100,
                layout: {
                    type: "hbox",
                    defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
                }
            },
            items: [
                {
                    name: "peering_point",
                    xtype: "peer.peeringpoint.LookupField",
                    fieldLabel: "Peering Point",
                    width: 400,
                    allowBlank: false
                },
                {
                    name: "peer_group",
                    xtype: "peer.peergroup.LookupField",
                    fieldLabel: "Peer Group",
                    width: 400,
                    allowBlank: false
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: "Project",
                    width: 400,
                    allowBlank: true
                },
                {
                    name: "local_asn",
                    xtype: "peer.as.LookupField",
                    fieldLabel: "Local AS",
                    width: 400,
                    allowBlank: false
                },
                {
                    name: "remote_asn",
                    xtype: "numberfield",
                    fieldLabel: "Remote AS",
                    hideTrigger: true,
                    keyNavEnabled: false,
                    mouseWheelEnabled: false,
                    allowBlank: false,
                    vtype: "ASN"
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: "Status",
                    allowBlank: false,
                    store: [
                        ["P", "Planned"],
                        ["A", "Active"],
                        ["S", "Shutdown"]
                    ]
                }
                
            ]
        },
        {
            xtype: "fieldset",
            title: "Link Addresses",
            collapsible: false,
            defaults: {
                labelWidth: 100,
                layout: {
                    type: "hbox",
                    defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
                }
            },
            items: [
                {
                    name: "local_ip",
                    xtype: "textfield",
                    allowBlank: false,
                    fieldLabel: "Local IP"
                },
                {
                    name: "local_backup_ip",
                    xtype: "textfield",
                    fieldLabel: "Local Backup IP",
                    allowBlank: true
                },
                {
                    name: "remote_ip",
                    xtype: "textfield",
                    allowBlank: false,
                    fieldLabel: "Remote IP"
                },
                {
                    name: "remote_backup_ip",
                    xtype: "textfield",
                    fieldLabel: "Remote Backup IP",
                    allowBlank: true
                }
            ]
        },
        {
            xtype: "fieldset",
            title: "Description",
            collapsible: false,
            defaults: {
                labelWidth: 100,
                layout: {
                    type: "hbox",
                    defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
                }
            },
            items: [
                {
                    name: "description",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "rpsl_remark",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: "RPSL Remark",
                    allowBlank: true
                }
            ]
        },
        {
            xtype: "fieldset",
            title: "Filters and Limits",
            collapsible: false,
            defaults: {
                labelWidth: 100,
                layout: {
                    type: "hbox",
                    defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
                }
            },
            items: [
                {
                    name: "import_filter",
                    xtype: "textfield",
                    width: 400,
                    allowBlank: false,                    
                    fieldLabel: "Import Filter"
                },
                {
                    name: "export_filter",
                    xtype: "textfield",
                    width: 400,
                    allowBlank: false,
                    fieldLabel: "Export Filter"
                },
                {
                    name: "import_filter_name",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: "Import Filter Name",
                    allowBlank: true
                },
                {
                    name: "export_filter_name",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: "Export Filter Name",
                    allowBlank: true
                },
                {
                    name: "max_prefixes",
                    xtype: "numberfield",
                    allowBlank: false,
                    fieldLabel: "Max. Prefixes"
                },
                {
                    name: "communities",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: "Import Communities",
                    allowBlank: true
                }
            ]
        },
        {
            xtype: "fieldset",
            title: "Preferences",
            collapsible: false,
            defaults: {
                labelWidth: 100,
                layout: {
                    type: "hbox",
                    defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
                }
            },
            items: [
                {
                    name: "local_pref",
                    xtype: "numberfield",
                    fieldLabel: "Local Pref",
                    allowBlank: true
                },
                {
                    name: "import_med",   
                    xtype: "numberfield",
                    fieldLabel: "Import MED",
                    allowBlank: true   
                },
                {
                    name: "export_med",   
                    xtype: "numberfield",
                    fieldLabel: "Export MED",
                    allowBlank: true   
                }
            ]
        },
        {
            xtype: "fieldset",
            title: "Tags",
            collapsible: false,
            defaults: {
                labelWidth: 100,
                layout: {
                    type: "hbox",
                    defaultMargins: {top: 0, right: 5, bottom: 0, left: 0}
                }
            },
            items: [
                {
                    name: "tt",
                    xtype: "numberfield",
                    fieldLabel: "TT",
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: "Tags",
                    width: 400,
                    allowBlank: true
                }
            ]
        }

    ],
    filters: [
    ],
    actions: [
        {
            title: "Mark as planned",
            action: "planned",
        },
        {
            title: "Mark as active",
            action: "active",
        },
        {
            title: "Mark as shutdown",
            action: "shutdown",
        }
    ],
    showOpError: function(action, op, status) {
        var me = this;
        // Detect Syntax Errors
        if(status.traceback) {
            NOC.error(status.traceback);
            return;
        }
        me.callParent([action, op, status]);
    }
});
