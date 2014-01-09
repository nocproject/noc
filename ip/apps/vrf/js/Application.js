//---------------------------------------------------------------------
// ip.vrf application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.Application");

Ext.define("NOC.ip.vrf.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.vrf.Model",
        "NOC.ip.vrfgroup.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.resourcestate.LookupField",
        "NOC.project.project.LookupField",
        "NOC.core.TagsField"
    ],
    model: "NOC.ip.vrf.Model",
    search: true,
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "State",
            dataIndex: "state",
            renderer: NOC.render.Lookup("state")
        },
        {
            text: "Group",
            dataIndex: "vrf_group",
            renderer: NOC.render.Lookup("vrf_group")
        },
        {
            text: "Project",
            dataIndex: "project",
            renderer: NOC.render.Lookup("project")
        },
        {
            text: "RD",
            dataIndex: "rd",
            width: 100
        },
        {
            text: "IPv4",
            dataIndex: "afi_ipv4",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "IPv6",
            dataIndex: "afi_ipv6",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        },
        {
            text: "Tags",
            dataIndex: "tags",
            renderer: NOC.render.Tags
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "VRF",
            allowBlank: false
        },
        {
            name: "state",
            xtype: "main.resourcestate.LookupField",
            fieldLabel: "State",
            allowBlank: false
        },
        {
            name: "vrf_group",
            xtype: "ip.vrfgroup.LookupField",
            fieldLabel: "VRF Group",
            allowBlank: false
        },
        {
            name: "project",
            xtype: "project.project.LookupField",
            fieldLabel: "Project",
            allowBlank: true
        },
        {
            name: "rd",
            xtype: "textfield",
            fieldLabel: "RD",
            allowBlank: false
        },
        {
            name: "afi_ipv4",
            xtype: "checkboxfield",
            boxLabel: "IPv4",
            allowBlank: false
        },
        {
            name: "afi_ipv6",
            xtype: "checkboxfield",
            boxLabel: "IPv6",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "tt",
            xtype: "textfield",
            regexText: /^\d*$/,
            fieldLabel: "TT",
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: true
        },
        {
            name: "allocated_till",
            xtype: "datefield",
            fieldLabel: "Allocated till",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By State",
            name: "state",
            ftype: "lookup",
            lookup: "main.resourcestate"
        },
        {
            title: "By VRF Group",
            name: "vrf_group",
            ftype: "lookup",
            lookup: "ip.vrfgroup"
        },
        {
            title: "By Project",
            name: "project",
            ftype: "lookup",
            lookup: "project.project"
        },
        {
            title: "By IPv4",
            name: "afi_ipv4",
            ftype: "boolean"
        },
        {
            title: "By IPv6",
            name: "afi_ipv6",
            ftype: "boolean"
        }
    ],

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            gridToolbar: [
                {
                    "itemId": "import",
                    text: "Import",
                    glyph: NOC.glyph.level_down,
                    tooltip: "Import VRFs",
                    checkAccess: NOC.hasPermission("import"),
                    menu: {
                        xtype: "menu",
                        plain: true,
                        items: [
                            {
                                text: "From Router",
                                itemId: "from_router",
                                glyph: NOC.glyph.level_down
                            }
                        ],
                        listeners: {
                            click: {
                                scope: me,
                                fn: me.onImportFromRouter
                            }
                        }
                    }
                }
            ]
        });
        me.callParent();
    },
    //
    onImportFromRouter: function() {
        Ext.create("NOC.ip.vrf.MOSelectForm", {app: this});
    },
    //
    runImportFromRouter: function(managed_object) {
        var me = this;

        NOC.mrt({
            url: "/ip/vrf/mrt/get_vrfs/",
            selector: managed_object,
            loadMask: me,
            scope: me,
            success: me.processImportFromRouter,
            failure: function() {
                NOC.error("Failed to import VRFs");
            }
        });
    },
    //
    processImportFromRouter: function(result) {
        var me = this,
            r = result[0];
        if(!Ext.isDefined(r)) {
            NOC.error("Failed to import VRFs:<br/>No result returned");
            return;
        }
        if(r.status) {
            var w = Ext.create("NOC.ip.vrf.VRFImportForm", {app: me});
            w.loadVRFsFromRouter(r.result);
        } else {
            NOC.error("Failed to import VRFs from {0}:<br/>{1}",
                      r.object_name, r.result.text);
        }
    },
    //
    onImportSuccess: function() {
        this.reloadStore();
    }
});
