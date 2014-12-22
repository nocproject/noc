//---------------------------------------------------------------------
// Link Interfaces window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.LinkForm");

Ext.define("NOC.inv.interface.LinkForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.sa.managedobject.LookupField"
    ],
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    // width: 300,
    // height: 200,
    autoScroll: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            autoLoad: false,
            fields: ["id", "label"],
            data: []
        });

        Ext.apply(me, {
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "sa.managedobject.LookupField",
                            name: "managed_object",
                            emptyText: "Select managed object ...",
                            fieldLabel: "Object",
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
                            fieldLabel: "Interface",
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
                            text: "Connect",
                            glyph: NOC.glyph.link,
                            formBind: true,
                            scope: me,
                            handler: me.onLink
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.form = me.items.first().getForm();
    },
    //
    onObjectSelect: function(field, value) {
        var me = this,
            v = value[0];
        Ext.Ajax.request({
            url: "/inv/interface/unlinked/" + v.get("id") + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var me = this,
                    data = Ext.decode(response.responseText);
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error("Failed to get interfaces list");
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
                me.app.loadInterfaces();
                me.close();
            },
            failure: function() {
                NOC.error("Failed to connect interfaces");
            }
        });
    }
});
