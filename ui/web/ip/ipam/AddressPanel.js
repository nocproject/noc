//---------------------------------------------------------------------
// ip.ipam Address panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.AddressPanel");

Ext.define("NOC.ip.ipam.AddressPanel", {
    extend: "NOC.core.FormPanel",
    requires: [
        "NOC.ip.addressprofile.LookupField",
        "NOC.project.project.LookupField",
        "NOC.sa.managedobject.LookupField"
    ],
    currentAddressId: null,
    restUrl: "/ip/address/",
    prefixRestUrl: "/ip/prefix/",
    enableDeleteButton: true,

    initComponent: function () {
        var me = this;

        Ext.apply(me, {
            fields: [
                {
                    name: "vrf",
                    xtype: "ip.vrf.LookupField",
                    fieldLabel: __("VRF"),
                    allowBlank: false,
                    readOnly: true
                },
                {
                    name: "address",
                    xtype: "textfield",
                    fieldLabel: __("Address"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "fqdn",
                    xtype: "textfield",
                    fieldLabel: __("FQDN"),
                    allowBlank: false,
                    uiStyle: "medium",
                    regex: /^[0-9a-z\-]+(\.[0-9a-z\-]+)+$/
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "profile",
                    xtype: "ip.addressprofile.LookupField",
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
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: __("Project"),
                    allowBlank: true
                },
                {
                    name: "managed_object",
                    xtype: "sa.managedobject.LookupField",
                    fieldLabel: __("Managed Object"),
                    allowBlank: true
                }
            ]
        });
        me.callParent()
    },

    preview: function (record, backItem) {
        var me = this;
        if(record.id) {
            me.loadAddress(record.id)
        } else {
            me.newAddress(record.prefixId, record.address)
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
            url: me.restUrl + (me.currentAddressId ? me.currentAddressId + "/" : ""),
            method: me.currentAddressId ? "PUT" : "POST",
            scope: me,
            jsonData: data,
            success: function(response) {
                var d = Ext.decode(response.responseText),
                    // Get prefix from prefix__label
                    pparts = d.prefix__label.split(": "),
                    prefix = pparts[pparts.length - 1];
                me.unmask();
                NOC.msg.complete(__("Saved"));
                me.app.showPrefix(d.vrf, d.afi, prefix)
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
    // Load address to form
    //
    loadAddress: function(id) {
        var me = this;
        me.currentAddressId = id;
        Ext.Ajax.request({
            url: me.restUrl + id + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.deleteButton.setDisabled(false);
                me.setTitle(__("Change address"));
                me.setValues(data)
            },
            failure: function() {
                NOC.error(__("Failed to load data"))
            }
        })
    },
    //
    // New address form
    //
    newAddress: function(prefixId, address) {
        var me = this;
        me.currentAddressId = null;
        Ext.Ajax.request({
            url: me.prefixRestUrl + prefixId + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText),
                    values = {
                        "vrf": data.vrf,
                        "vrf__label": data.vrf__label,
                        "afi": data.afi
                    };
                if(address) {
                    values.address = address
                } else {
                    values.address = me.app.getCommonPrefixPart(data.afi, data.prefix)
                }
                me.deleteButton.setDisabled(true);
                me.setTitle(__("Create new address"));
                me.setValues(values)
            },
            failure: function() {
                NOC.error(__("Failed to load data"))
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
    onDelete: function() {
        var me = this;

        Ext.Msg.show({
            title: __("Delete address?"),
            msg: __("Do you wish to delete address? This operation cannot be undone!"),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if(button === "yes")
                    me.deleteAddress();
            }
        });

    },
    //
    deleteAddress: function() {
        var me = this;
        Ext.Ajax.request({
            url: me.restUrl + me.currentAddressId + "/",
            method: "DELETE",
            scope: me,
            success: function() {
                NOC.info(__("Deleted"));
                me.onClose()
            },
            failure: function(response) {
                NOC.error(__("Failed to delete: ") + response.responseText)
            }
        })
    }
});
