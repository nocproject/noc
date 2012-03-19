//---------------------------------------------------------------------
// Add First Free VC window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
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
    callback: null,
    closable: true,

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
            text: "Reset",
            itemId: "reset",
            iconCls: "icon_cancel",
            handler: function() {
                this.up("form").getForm().reset();
            }
        },

        {
            text: "Add First Free",
            itemId: "add",
            iconCls: "icon_add",
            /*formBind: true,
            disabled: true,*/
            handler: function() {
                var me = this.up("window");
                if(me.callback) {
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
                            me.callback(r.vc_domain, vc);
                        },
                        failure: function() {
                            // @todo: Report Error
                            me.close();
                        }
                    });
                }
            }
        }
    ]
});
