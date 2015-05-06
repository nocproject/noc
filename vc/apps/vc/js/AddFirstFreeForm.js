//---------------------------------------------------------------------
// Add First Free VC window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
// @todo: Auto-fill VC-domain if selected in filter
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.AddFirstFreeForm");

Ext.define("NOC.vc.vc.AddFirstFreeForm", {
    extend: "Ext.Window",
    requires: [
        "NOC.vc.vcdomain.LookupField",
        "NOC.vc.vcfilter.LookupField"
    ],
    title: "Add First Free VC",
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
                            xtype: "vc.vcdomain.LookupField",
                            name: "vc_domain",
                            fieldLabel: "VC Domain",
                            allowBlank: false
                        },
                        {
                            xtype: "vc.vcfilter.LookupField",
                            name: "vc_filter",
                            fieldLabel: "VC Filter",
                            allowBlank: false
                        }
                    ]
                }
            ],
            buttons: [
                {
                    text: "Add First Free",
                    itemId: "add",
                    glyph: NOC.glyph.plus,
                    scope: me,
                    /*formBind: true,
                    disabled: true,*/
                    handler: me.onAddFirstFree
                }
            ]
        });
        me.callParent();
    },
    // Called when "Add button pressed"
    onAddFirstFree: function() {
        var me = this;
        var r = me.down("form").getForm().getValues();
        Ext.Ajax.request({
            method: "GET",
            url: "/vc/vc/find_free/",
            params: {
                vc_domain: r.vc_domain,
                vc_filter: r.vc_filter
            },
            scope: me,
            success: function(response) {
                var vc = Ext.decode(response.responseText);
                if(!vc) {
                    // No Free VC
                    Ext.Msg.alert("Error", "No free VC found");
                    me.close();
                    return;
                }
                me.close();
                me.app.newRecord({vc_domain: r.vc_domain, l1: vc});
            },
            failure: function() {
                NOC.error("Failed to get first free VC");
                me.close();
            }
        });
    }
});
