//---------------------------------------------------------------------
// Link Interfaces window
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LinkForm");

Ext.define("NOC.sa.managedobject.LinkForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.core.ComboBox",
    ],
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    // width: 300,
    // height: 200,
    scrollable: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            autoLoad: false,
            fields: ["id", "label"],
            data: []
        });

        me.unlinkButton = Ext.create("Ext.button.Button", {
            text: __("Disconnect"),
            glyph: NOC.glyph.times,
            disabled: !me.isLinked,
            scope: me,
            handler: me.onUnlink
        });

        me.fixButton = Ext.create("Ext.button.Button", {
            text: __("Fix"),
            glyph: NOC.glyph.check_circle,
            disabled: !me.isLinked,
            scope: me,
            handler: me.onFix
        });

        Ext.apply(me, {
            items: [
                {
                    xtype: "form",
                    padding: 4,
                    items: [
                        {
                            xtype: "core.combo",
                            restUrl: "/sa/managedobject/lookup/",
                            uiStyle: "medium-combo",
                            name: "managed_object",
                            emptyText: __("Select managed object ..."),
                            fieldLabel: __("Object"),
                            width: 360,
                            allowBlank: false,
                            listeners: {
                                scope: me,
                                select: me.onObjectSelect
                            }
                        },
                        {
                            xtype: "combobox",
                            name: "interface",
                            fieldLabel: __("Interface"),
                            width: 360,
                            allowBlank: false,
                            displayField: "label",
                            valueField: "id",
                            queryMode: "local",
                            store: me.store
                        }
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: __("Connect"),
                            glyph: NOC.glyph.link,
                            formBind: true,
                            scope: me,
                            handler: me.onLink
                        },
                        me.unlinkButton,
                        me.fixButton
                    ]
                }
            ]
        });
        me.callParent();
        me.form = me.items.first().getForm();
    },
    //
    onObjectSelect: function(field, value) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/interface/unlinked/" + value.get("id") + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var me = this,
                    data = Ext.decode(response.responseText);
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error(__("Failed to get interfaces list"));
            }
        });
    },
    //
    onLink: function() {
        var me = this,
            data = {
                type: "ptp",
                interfaces: [me.ifaceId, me.form.getValues().interface]
            };
        Ext.Ajax.request({
            url: "/inv/interface/link/",
            method: "POST",
            jsonData: data,
            scope: me,
            success: function() {
                var me = this;
                me.app.onRefresh();
                me.close();
            },
            failure: function() {
                NOC.error(__("Failed to connect interfaces"));
            }
        });
    },
    //
    onUnlink: function() {
        var me = this;
        Ext.Msg.show({
            title: __("Unlink interface"),
            msg: Ext.String.format(__("Do you wish to unlink interface {0}?"), me.ifName),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if(button == "yes") {
                    Ext.Ajax.request({
                        url: "/inv/interface/unlink/" + me.ifaceId + "/",
                        method: "POST",
                        scope: me,
                        success: function(response) {
                            var me = this,
                                data = Ext.decode(response.responseText);
                            if(data.status) {
                                me.close();
                                me.app.onRefresh();
                            } else {
                                NOC.error(data.message);
                            }
                        },
                        failure: function() {
                            NOC.error(__("Unlink failure"));
                        }
                    });
                }
            }
        });
    },
    //
    onFix: function() {
        var me = this;
        me.mask("Fixing ...");
        Ext.Ajax.request({
            url: "/sa/managedobject/link/fix/" + me.linkId + "/",
            method: "POST",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.unmask();
                if(data.status) {
                    NOC.info(data.message);
                    self.close();
                    me.app.onRefresh();
                } else {
                    NOC.error(data.message);
                }
            },
            failure: function() {
                NOC.error(__("Failed to fix"));
                me.unmask();
            }
        });
    },
    //
    getDefaultFocus: function() {
        var me = this;
        return me.form.findField("managed_object");
    }
});
