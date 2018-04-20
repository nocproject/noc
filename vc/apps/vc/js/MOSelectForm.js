//---------------------------------------------------------------------
// Managed Object Selection form
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.MOSelectForm");

Ext.define("NOC.vc.vc.MOSelectForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.vc.vcdomain.LookupField",
        "NOC.vc.vcfilter.LookupField",
        "NOC.sa.managedobject.LookupField"
    ],
    title: "Select Object To Import",
    autoShow: true,
    closable: true,
    modal: true,
    app: null,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "vc.vcdomain.LookupField",
                            name: "vc_domain",
                            fieldLabel: "VC Domain",
                            allowBlank: false,
                            itemId: "vc_domain",
                            listeners: {
                                select: {
                                    scope: me,
                                    fn: me.onSelectVCDomain
                                }
                            }
                        },
                        {
                            xtype: "sa.managedobject.LookupField",
                            name: "managed_object",
                            fieldLabel: "Managed Object",
                            allowBlank: false,
                            disabled: true,
                            itemId: "managed_object"
                        },
                        {
                            xtype: "vc.vcfilter.LookupField",
                            name: "vc_filter",
                            fieldLabel: "VC Filter",
                            allowBlank: false,
                            itemId: "vc_filter"
                        }
                    ]
                }
            ],
            buttons: [
                {
                    text: "Import",
                    itemId: "import",
                    glyph: NOC.glyph.sign_in,
                    scope: me,
                    handler: me.onImport
                }
            ]
        });
        me.callParent();
    },
    onSelectVCDomain: function() {
        var me = this,
            mo = me.down("form").getComponent("managed_object");
        mo.setDisabled(false);
    },
    onImport: function() {
        var me = this,
            r = me.down("form").getForm().getValues();
        me.close();
        me.app.runImportFromSwitch(r.vc_domain, r.managed_object, r.vc_filter);
    }
});
