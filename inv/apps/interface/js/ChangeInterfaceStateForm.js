//---------------------------------------------------------------------
// Change Interface State
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.ChangeInterfaceStateForm");

Ext.define("NOC.inv.interface.ChangeInterfaceStateForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.main.resourcestate.LookupField"
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
            title: "Change " + me.record.get("name") + " state",
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "main.resourcestate.LookupField",
                            name: "state",
                            fieldLabel: "State",
                            allowBlank: false
                        }
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Change",
                            iconCls: "icon_page_edit",
                            formBind: true,
                            scope: me,
                            handler: me.onChangeState
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.field = me.items.first().getForm().getFields().items[0];
        me.field.setValue(me.record.get("state"));
    },
    //
    onChangeState: function() {
        var me = this,
            state = me.field.getValue(),
            state_label = me.field.getDisplayValue(),
            data = {
                state: state
            };

        Ext.Ajax.request({
            url: "/inv/interface/l1/" + me.record.get("id") + "/change_state/",
            method: "POST",
            jsonData: data,
            scope: me,
            success: function() {
                me.record.set("state", state);
                me.record.set("state__label", state_label);
                me.close();
            },
            failure: function() {
                NOC.error("Failed to change state");
            }
        });
    }
});
