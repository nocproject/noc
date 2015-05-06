//---------------------------------------------------------------------
// Managed Object Selection form
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.MOSelectForm");

Ext.define("NOC.ip.vrf.MOSelectForm", {
    extend: "Ext.Window",
    requires: [
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
                    margin: 4,
                    items: [
                        {
                            xtype: "sa.managedobject.LookupField",
                            name: "managed_object",
                            fieldLabel: "Managed Object",
                            allowBlank: false,
                            itemId: "managed_object"
                        }
                    ]
                }
            ],
            buttons: [
                {
                    text: "Import",
                    itemId: "import",
                    glyph: NOC.hlyph.level_down,
                    /* formBind: true,
                    disabled: true, */
                    scope: me,
                    handler: me.onImport
                }
            ]
        });
        me.callParent();
    },
    onImport: function() {
        var me = this,
            r = me.down("form").getForm().getValues();
        me.close();
        me.app.runImportFromRouter(r.managed_object);
    }
});
