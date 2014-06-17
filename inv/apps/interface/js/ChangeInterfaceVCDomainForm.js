//---------------------------------------------------------------------
// Change Interface VCDomain
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.ChangeInterfaceVCDomainForm");

Ext.define("NOC.inv.interface.ChangeInterfaceVCDomainForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.vc.vcdomain.LookupField"
    ],
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
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
            title: "Change " + me.record.get("name") + " VC Domain",
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "vc.vcdomain.LookupField",
                            name: "state",
                            fieldLabel: "VCDomain",
                            allowBlank: true
                        }
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Change",
                            glyph: NOC.glyph.check,
                            formBind: false,
                            scope: me,
                            handler: me.onChangeVCDomain
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.field = me.items.first().getForm().getFields().items[0];
        me.field.setValue(me.record.get("vc_domain"));
    },
    //
    onChangeVCDomain: function() {
        var me = this,
            vc_domain = me.field.getValue(),
            vc_domain_label = me.field.getDisplayValue(),
            data = {
                vc_domain: vc_domain
            };

        Ext.Ajax.request({
            url: "/inv/interface/l1/" + me.record.get("id") + "/change_vc_domain/",
            method: "POST",
            jsonData: data,
            scope: me,
            success: function() {
                me.record.set("vc_domain", vc_domain);
                me.record.set("vc_domain__label", vc_domain_label);
                me.close();
            },
            failure: function() {
                NOC.error("Failed to change VC Domain");
            }
        });
    }
});
