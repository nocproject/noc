//---------------------------------------------------------------------
// ip.ipam Prefix panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.PrefixPanel");

Ext.define("NOC.ip.ipam.view.forms.prefix.PrefixPanel", {
    extend: "NOC.core.FormPanel",
    alias: "widget.ip.ipam.form.prefix",
    requires: [
        "NOC.ip.prefixprofile.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.peer.as.LookupField",
        "NOC.vc.vlan.LookupField",
        "NOC.project.project.LookupField",
        "NOC.aaa.user.LookupField",
        "NOC.aaa.group.LookupField"
    ],
    currentPrefixId: null,
    restUrl: "/ip/prefix/",
    viewModel: {
        data: {
            isNew: false
        }
    },

    initComponent: function() {
        var me = this;

        me.app = me.up("[itemId=ip-ipam]");
        me.rebaseButton = Ext.create("Ext.button.Button", {
            text: __("Rebase"),
            glyph: NOC.glyph.truck,
            tooltip: __("Rebase prefix to a new location"),
            scope: me,
            handler: me.onRebase,
            hasAccess: NOC.hasPermission("rebase"),
            bind: {
                disabled: "{isNew}"
            }
        });

        Ext.apply(me, {
            fields: [
                {
                    name: "id",
                    xtype: "displayfield",
                    hidden: true
                },
                {
                    name: "vrf",
                    xtype: "ip.vrf.LookupField",
                    fieldLabel: __("VRF"),
                    allowBlank: true,
                    readOnly: true
                },
                {
                    name: "prefix",
                    xtype: "combobox",
                    fieldLabel: __("Prefix"),
                    allowBlank: false,
                    uiStyle: "medium",
                    store: [],
                    bind: {
                        readOnly: "{!isNew}"
                    }
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "profile",
                    xtype: "ip.prefixprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "afi",
                    xtype: "displayfield",
                    fieldLabel: __("Address Family"),
                    allowBlank: true
                },
                {
                    name: "asn",
                    xtype: "peer.as.LookupField",
                    fieldLabel: __("AS"),
                    allowBlank: true
                },
                {
                    name: "vlan",
                    xtype: "vc.vlan.LookupField",
                    fieldLabel: __("VLAN"),
                    allowBlank: true,
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "allow_models": ["ip.Prefix"]
                    }
                },
                {
                    name: "tt",
                    xtype: "numberfield",
                    fieldLabel: __("TT"),
                    allowBlank: true
                },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: true,
                    bind: {
                        disabled: "{isNew}"
                    }
                },
                {
                    name: "allocated_till",
                    xtype: "datefield",
                    startDay: 1,
                    fieldLabel: __("Allocated till"),
                    allowBlank: true
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: __("Project"),
                    allowBlank: true
                },
                {
                    name: "prefix_discovery_policy",
                    xtype: "combobox",
                    fieldLabel: __("Prefix Discovery Policy"),
                    allowBlank: false,
                    store: [
                        ["P", __("Profile")],
                        ["E", __("Enable")],
                        ["D", __("Disable")]
                    ],
                    labelWidth: 180,
                    uiStyle: "medium"
                },
                {
                    name: "address_discovery_policy",
                    xtype: "combobox",
                    fieldLabel: __("Address Discovery Policy"),
                    allowBlank: false,
                    store: [
                        ["P", __("Profile")],
                        ["E", __("Enable")],
                        ["D", __("Disable")]
                    ],
                    labelWidth: 180,
                    uiStyle: "medium"
                },
                {
                    name: "pools",
                    xtype: "gridfield",
                    fieldLabel: __("Address Pools"),
                    columns: [
                        {
                            text: __("Pool"),
                            dataIndex: "pool",
                            width: 200,
                            editor: {
                                xtype: "inv.resourcepool.LookupField"
                            },
                            renderer: NOC.render.Lookup("pool")
                        },
                        {
                            dataIndex: "description",
                            text: __("Description"),
                            editor: "textfield",
                            width: 150
                        }
                    ]
                }
                // {
                //     name: "direct_permissions",
                //     xtype: "gridfield",
                //     fieldLabel: __("Permissions"),
                //     columns: [
                //         {
                //             text: __("User"),
                //             dataIndex: "user",
                //             editor: "main.user.LookupField",
                //             renderer: NOC.render.Lookup("user"),
                //             width: 100
                //         },
                //         {
                //             text: __("Group"),
                //             dataIndex: "group",
                //             editor: "main.group.LookupField",
                //             renderer: NOC.render.Lookup("group"),
                //             width: 150
                //         },
                //         {
                //             text: __("Permission"),
                //             dataIndex: "permission",
                //             editor: {
                //                 xtype: "combobox",
                //                 store: [
                //                     ["can_view", "can_view"],
                //                     ["can_change", "can_change"],
                //                     ["can_create", "can_create"]
                //                 ]
                //             },
                //             width: 150
                //         }
                //     ]
                // }
            ],
            formToolbar: [
                me.rebaseButton
            ]
        });
        me.callParent()
    },
    onClose: function() {
        this.close();
    },
    //
    onRebase: function() {
        var me = this,
            values = me.getFormData(),
            vrfField = me.getField("vrf"),
            app = me.up("[itemId=ip-ipam]");
        app.getViewModel().set("activeItem", "ipam-prefix-rebase");
        app.down("[itemId=ipam-prefix-rebase]").preview({
            id: me.currentPrefixId,
            to_vrf: values.vrf,
            to_vrf__label: vrfField.getRawValue(),
            to_prefix: values.prefix
        });
    },
    //
    close: function() {
        var me = this,
            prefixId = me.getFormData().id;
        if(me.getViewModel().get("isNew")) {
            prefixId = me.up("[itemId=ip-ipam]").getViewModel().get("prefix.id");
        }
        me.fireEvent("ipIPAMPrefixFormClose", {id: prefixId});
    },
    //
    save: function(data) {
        var me = this;
        me.mask(__("Saving ..."));
        Ext.Ajax.request({
            url: me.restUrl + (me.currentPrefixId ? me.currentPrefixId + "/" : ""),
            method: me.currentPrefixId ? "PUT" : "POST",
            scope: me,
            jsonData: data,
            success: function() {
                me.unmask();
                NOC.msg.complete(__("Saved"));
                me.close();
            },
            failure: function(response) {
                var message = "Error saving record";
                if(response.responseText) {
                    try {
                        message = Ext.decode(response.responseText).message
                    } catch(err) {
                        console.log(response.responseText)
                    }
                }
                me.unmask();
                NOC.error(message)
            }
        });
    },
    //
    preview: function(record, backItem) {
        var me = this;
        if(record.id) {
            me.loadPrefix(record.id)
        } else {
            me.newPrefix(record.parentId, record.prefix)
        }
    },
    //
    // Load prefix to form
    //
    loadPrefix: function(id) {
        var me = this;
        me.currentPrefixId = id;
        Ext.Ajax.request({
            url: me.restUrl + id + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.getViewModel().set("isNew", false);
                me.setTitle(__("Change prefix ") + data.prefix);
                me.setValues(data)
            },
            failure: function() {
                NOC.error(__("Failed to load data"))
            }
        })
    },
    //
    // New prefix form
    //
    newPrefix: function(parentId, prefix) {
        var me = this,
            prefixField = me.getField("prefix");
        me.currentPrefixId = null;
        // Load data
        Ext.Ajax.request({
            url: me.restUrl + parentId + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText),
                    values = {
                        "vrf": data.vrf,
                        "vrf__label": data.vrf__label,
                        "afi": data.afi
                    };
                if(prefix) {
                    values.prefix = prefix
                } else {
                    values.prefix = me.getCommonPrefixPart(data.afi, data.prefix)
                }
                me.getViewModel().set("isNew", true);
                me.setValues(values);
                me.setTitle(__("Create new prefix"))
            },
            failure: function() {
                NOC.error(__("Failed to load data"))
            }
        });
        // Set suggestions
        Ext.Ajax.request({
            url: me.restUrl + parentId + "/suggest_free/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                prefixField.setStore(data.map(function(v) {
                    return v.prefix
                }))
            }
        })
    },
    //
    setValues: function(data) {
        var me = this;
        me.callParent([data]);
        me.setAFI(data.afi)
    },
    //
    setAFI: function(afi) {
        console.log("setAFI", afi)
    },
    //
    getCommonPrefixPart: function(afi, prefix) {
        var parts = prefix.split("/"),
            net = parts[0],
            mask = parseInt(parts[1]);

        if(afi === "4") {
            // IPv4
            // Align to 8-bit border
            var v = net.split(".").slice(0, Math.floor(mask / 8)).join(".");
            if(v !== "") {
                v = v + "."
            }
            return v
        } else {
            // if p.mask < 16:
            //     return ""
            // # Align to 16-bit border
            // p.mask = (p.mask // 16) * 16
            // p = self.rx_ipv6_prefix_rest.sub("", p.normalized.prefix)
        }
    }
});
