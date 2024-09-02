//---------------------------------------------------------------------
// ip.ipam Address panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.AddressPanel");

Ext.define("NOC.ip.ipam.view.forms.prefix.AddressPanel", {
    extend: "NOC.core.FormPanel",
    alias: "widget.ip.ipam.address.form",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.core.StateField",
        "NOC.ip.addressprofile.LookupField",
        "NOC.project.project.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.aaa.user.LookupField",
        "NOC.aaa.group.LookupField"
    ],
    currentAddressId: null,
    restUrl: "/ip/address/",
    prefixRestUrl: "/ip/prefix/",
    enableDeleteButton: true,

    viewModel: {
        data: {
            isNew: false
        }
    },

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            fields: [
                {
                    name: "prefix",
                    xtype: "displayfield",
                    hidden: true
                },
                {
                    name: "vrf",
                    xtype: "ip.vrf.LookupField",
                    fieldLabel: __("VRF"),
                    allowBlank: false,
                    uiStyle: "large",
                    readOnly: true
                },
                {
                    name: "address",
                    xtype: "textfield",
                    fieldLabel: __("Address"),
                    allowBlank: false,
                    uiStyle: "large",
                    bind: {
                        readOnly: "{!isNew}"
                    }
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "fqdn",
                    xtype: "textfield",
                    fieldLabel: __("FQDN"),
                    allowBlank: true,
                    uiStyle: "large",
                    regex: /^[0-9a-z\-]+(\.[0-9a-z\-]+)+$/
                },
                {
                    name: "mac",
                    xtype: "textfield",
                    fieldLabel: __("MAC"),
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
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "allow_models": ["ip.Address"]
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
                },
                {
                    name: "subinterface",
                    xtype: "textfield",
                    fieldLabel: __("Interface"),
                    allowBlank: true
                },
                {
                    name: "source",
                    xtype: "displayfield",
                    fieldLabel: __("Source"),
                    allowBlank: true
                },
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
            ]
        });
        me.callParent()
    },
    //
    preview: function(record, backItem) {
        var me = this;
        if(record.id) {
            me.loadAddress(record.id)
        } else {
            me.newAddress(record.prefixId, record.address)
        }
    },
    //
    onClose: function() {
        this.close();
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
    close: function() {
        var me = this,
            prefixId = me.getFormData().prefix;
        if(me.getViewModel().get("isNew")) {
            prefixId = me.up("[itemId=ip-ipam]").getViewModel().get("prefix.id");
        }
        me.fireEvent("ipIPAMAddressCloseForm", {id: prefixId});
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
                me.getViewModel().set("isNew", false);
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
                if(address === 'create_new') {
                    values.address = data.prefix.substr(0, data.prefix.lastIndexOf("."));
                }
                else if(address) {
                    values.address = address
                } else {
                    values.address = me.app.getCommonPrefixPart(data.afi, data.prefix)
                }
                me.getViewModel().set("isNew", true);
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
