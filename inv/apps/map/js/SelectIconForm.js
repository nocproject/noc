//---------------------------------------------------------------------
// Icon Selection window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
// @todo: Auto-fill VC-domain if selected in filter
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.SelectIconForm");

Ext.define("NOC.inv.map.SelectIconForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.main.ref.stencil.LookupField"
    ],
    title: "Select Shape",
    autoShow: true,
    closable: false,
    modal: true,
    app: null,
    closable: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "form",
                    items: [
                        {
                            xtype: "main.ref.stencil.LookupField",
                            name: "shape",
                            fieldLabel: "Shape",
                            labelWidth: 40,
                            minWidth: 300,
                            allowBlank: false
                        }
                    ]
                }
            ],
            buttons: [
                {
                    text: "Set",
                    itemId: "set",
                    glyph: NOC.glyph.ok,
                    scope: me,
                    /*formBind: true,
                    disabled: true,*/
                    handler: me.onSet
                }
            ]
        });
        me.callParent();
    },
    // Called when "Set" button pressed
    onSet: function() {
        var me = this;
        var r = me.down("form").getForm().getValues();
        me.close();
        me.app.setIcon(r.shape);
    }
});
