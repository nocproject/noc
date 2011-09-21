//---------------------------------------------------------------------
// peer.prefixlistbuilder application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.prefixlistbuilder.Application");

Ext.define("NOC.peer.prefixlistbuilder.Application", {
    extend: "NOC.core.Application",
    requires: ["NOC.peer.peeringpoint.LookupField"],
    initComponent: function() {
        Ext.applyIf(this, {
            items: [
                Ext.create("Ext.form.Panel", {
                    border: true,
                    padding: 4,
                    bodyPadding: 4,
                    items: [
                        {
                            xtype: "textfield",
                            fieldLabel: "Name",
                            name: "name",
                            emptyText: "Prefix list name ..."
                        },
                        {
                            xtype: "peer.peeringpoint.LookupField",
                            fieldLabel: "Peering Point",
                            name: "peering_point"
                        },
                        {
                            xtype: "textfield",
                            fieldLabel: "as-set",
                            name: "as_set",
                            emptyText: "AS or AS-set"
                        }
                    ],
                    buttons: [
                        {
                            text: "Build",
                            formBind: true,
                            disabled: false,
                            handler: function() {
                                // Query for prefix list
                                var form = this.up("panel").getForm();
                                if(!form.isValid())
                                    return;
                                var v = form.getValues();
                                Ext.Ajax.request({
                                    method: "GET",
                                    url: "/peer/prefixlistbuilder/",
                                    scope: this,
                                    params: v,
                                    success: function(response) {
                                        var d = Ext.decode(response.responseText);
                                        var r = this.up("panel").up("panel").items.items[1];
                                        r.setTitle("Prefix list: " + d["name"]);
                                        r.show();
                                        r.items.items[0].setValue(d["prefix_list"]);
                                    }
                                });
                            }
                        },
        
                        {
                            text: "Reset",
                            disabled: false,
                            handler: function() {
                                this.up("panel").getForm().reset();
                            }
                        }
                    ]
                }),
                {
                    xtype: "fieldset",
                    id: "prefixlist",
                    collapsible: true,
                    hidden: true,
                    padding: 4,
                    bodyPadding: 4,
                    items: [
                        {
                            xtype: "textareafield",
                            resizable: true
                        }
                    ]
                }
            ]
        });
        this.callParent();
    }
});
