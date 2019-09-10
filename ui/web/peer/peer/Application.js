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
        "NOC.core.RepoPreview",
        "NOC.core.TagsField",
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
            text: __("Peering Point"),
            flex: 1,
            dataIndex: "peering_point",
            renderer: NOC.render.Lookup("peering_point")
        },
        {
            text: __("Peer Group"),
            flex: 1,
            dataIndex: "peer_group",
            renderer: NOC.render.Lookup("peer_group")
        },
        {
            text: __("Project"),
            dataIndex: "project",
            renderer: NOC.render.Lookup("project")
        },
        {
            text: __("Local AS"),
            flex: 1,
            dataIndex: "local_asn",
            renderer: NOC.render.Lookup("local_asn")
        },
        {
            text: __("Remote AS"),
            flex: 1,
            dataIndex: "remote_asn"
        },
        {
            text: __("Status"),
            width: 70,
            dataIndex: "status",
            renderer: function(a) {
                return {P: "Planned", A: "Active",
                        S: "Shutdown"}[a];
            }
        },
        {
            text: __("Import Filter"),
            flex: 1,
            dataIndex: "import_filter"
        },
        {
            text: __("Export Filter"),
            flex: 1,
            dataIndex: "export_filter"
        },
        {
            text: __("Local Address"),
            flex: 1,
            dataIndex: "local_ip"
        },
        {
            text: __("Remote Address"),
            flex: 1,
            dataIndex: "remote_ip"
        },
        {
            text: __("TT"),
            flex: 1,
            dataIndex: "tt"
        },
        {
            text: __("Description"),
            flex: 1,
            dataIndex: "description"
        }, 
        {
            text: __("Import Communities"),
            flex: 1,
            dataIndex: "communities"
        }, 
        {
            text: __("Tags"),
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
                    fieldLabel: __("Peering Point"),
                    width: 400,
                    allowBlank: false
                },
                {
                    name: "peer_group",
                    xtype: "peer.peergroup.LookupField",
                    fieldLabel: __("Peer Group"),
                    width: 400,
                    allowBlank: false
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: __("Project"),
                    width: 400,
                    allowBlank: true
                },
                {
                    name: "local_asn",
                    xtype: "peer.as.LookupField",
                    fieldLabel: __("Local AS"),
                    width: 400,
                    allowBlank: false
                },
                {
                    name: "remote_asn",
                    xtype: "numberfield",
                    fieldLabel: __("Remote AS"),
                    hideTrigger: true,
                    keyNavEnabled: false,
                    mouseWheelEnabled: false,
                    allowBlank: false,
                    vtype: "ASN"
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: __("Status"),
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
                    fieldLabel: __("Local IP")
                },
                {
                    name: "local_backup_ip",
                    xtype: "textfield",
                    fieldLabel: __("Local Backup IP"),
                    allowBlank: true
                },
                {
                    name: "remote_ip",
                    xtype: "textfield",
                    allowBlank: false,
                    fieldLabel: __("Remote IP")
                },
                {
                    name: "remote_backup_ip",
                    xtype: "textfield",
                    fieldLabel: __("Remote Backup IP"),
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
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "rpsl_remark",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: __("RPSL Remark"),
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
                    fieldLabel: __("Import Filter"),
                    emptytext: __("ANY")
                },
                {
                    name: "export_filter",
                    xtype: "textfield",
                    width: 400,
                    allowBlank: false,
                    fieldLabel: __("Export Filter"),
                    emptytext: __("ANY")
                },
                {
                    name: "import_filter_name",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: __("Import Filter Name"),
                    allowBlank: true
                },
                {
                    name: "export_filter_name",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: __("Export Filter Name"),
                    allowBlank: true
                },
                {
                    name: "max_prefixes",
                    xtype: "numberfield",
                    allowBlank: false,
                    fieldLabel: __("Max. Prefixes")
                },
                {
                    name: "communities",
                    xtype: "textfield",
                    width: 400,
                    fieldLabel: __("Import Communities"),
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
                    fieldLabel: __("Local Pref"),
                    allowBlank: true
                },
                {
                    name: "import_med",   
                    xtype: "numberfield",
                    fieldLabel: __("Import MED"),
                    allowBlank: true   
                },
                {
                    name: "export_med",   
                    xtype: "numberfield",
                    fieldLabel: __("Export MED"),
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
                    fieldLabel: __("TT"),
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
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
    },
    preview: {
        xtype: "NOC.core.RepoPreview",
        syntax: "rpsl",
        previewName: 'Peer RPSL: {0}',
        restUrl: '/peer/peer/{0}/repo/rpsl/'
    }
});
