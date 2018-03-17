//---------------------------------------------------------------------
// ip.ipam Prefix panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.PrefixPanel");

Ext.define("NOC.ip.ipam.PrefixPanel", {
    extend: "NOC.core.FormPanel",
    requires: [
        "NOC.ip.prefixprofile.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.peer.as.LookupField",
        "NOC.vc.vc.LookupField",
        "NOC.project.project.LookupField"
    ],
    currentPrefixId: null,
    restUrl: "/ip/prefix/",

    initComponent: function () {
        var me = this;

        me.rebaseButton = Ext.create("Ext.button.Button", {
            text: __("Rebase"),
            glyph: NOC.glyph.truck,
            tooltip: __("Rebase prefix to a new location"),
            scope: me,
            handler: me.onRebase,
            hasAccess: NOC.hasPermission("rebase")
        });

        Ext.apply(me, {
            fields: [
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
                    store: []
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
                    name: "vc",
                    xtype: "vc.vc.LookupField",
                    fieldLabel: __("VC"),
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
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
                    allowBlank: true
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
                }
            ],
            formToolbar: [
                me.rebaseButton
            ]
        });
        me.callParent()
    },

    preview: function (record, backItem) {
        var me = this;
        if(record.id) {
            me.loadPrefix(record.id)
        } else {
            me.newPrefix(record.parentId, record.prefix)
        }
    },

    onClose: function() {
        var me = this;
        me.app.showCurrentPrefix()
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
            success: function(response) {
                var d = Ext.decode(response.responseText);
                me.unmask();
                NOC.msg.complete(__("Saved"));
                me.app.showPrefix(d.vrf, d.afi, d.prefix)
            },
            failure: function(response) {
                var message = "Error saving record";
                if(response.responseText) {
                    try {
                        message = Ext.decode(response.responseText).message
                    }
                    catch(err) {
                        console.log(response.responseText)
                    }
                }
                me.unmask();
                NOC.error(message)
            }
        });
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
                me.rebaseButton.setDisabled(false);
                me.getField("prefix").setReadOnly(true);
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
                    values.prefix = me.app.getCommonPrefixPart(data.afi, data.prefix)
                }
                me.rebaseButton.setDisabled(true);
                prefixField.setReadOnly(false);
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
                prefixField.setStore(data.map(function(v) {return v.prefix}))
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
    onRebase: function() {
        var me = this,
            values = me.getFormData(),
            vrfField = me.getField("vrf");
        me.app.previewItem(
            me.app.ITEM_REBASE_FORM,
            {
                id: me.currentPrefixId,
                to_vrf: values.vrf,
                to_vrf__label: vrfField.getRawValue(),
                to_prefix: values.prefix
            }
        )
    }
});
