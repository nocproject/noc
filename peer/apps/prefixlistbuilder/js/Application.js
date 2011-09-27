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
    layout: "anchor",
    initComponent: function() {
        Ext.applyIf(this, {
            items: [
                Ext.create("Ext.form.Panel", {
                    border: true,
                    padding: 4,
                    bodyPadding: 4,
                    defaults: {
                        enableKeyEvents: true,
                        listeners: {
                            specialkey: function(field, key) {
                                if (field.xtype != "textfield")
                                    return;
                                var get_button = function(scope, name) {
                                    return scope.up("panel").dockedItems.items[0].getComponent(name);
                                }
                                switch(key.getKey()) {
                                    case Ext.EventObject.ENTER:
                                        var b = get_button(this, "build");
                                        key.stopEvent();
                                        b.handler.call(b);
                                        break;
                                    case Ext.EventObject.ESC:
                                        var b = get_button(this, "reset");
                                        key.stopEvent();
                                        b.handler.call(b);
                                }
                            }
                        }
                    },
                    items: [
                        {
                            xtype: "textfield",
                            fieldLabel: "Name",
                            name: "name",
                            emptyText: "Prefix list name ...",
                            allowBlank: true,
                            regex: /^[0-9a-zA-Z_\-]*$/
                        },
                        {
                            xtype: "peer.peeringpoint.LookupField",
                            fieldLabel: "Peering Point",
                            name: "peering_point",
                            allowBlank: false
                        },
                        {
                            xtype: "textfield",
                            fieldLabel: "as-set",
                            name: "as_set",
                            emptyText: "AS or AS-set",
                            allowBlank: false,
                            regex: /^AS[0-9a-zA-z\-_:]+$/
                        }
                    ],
                    buttonAlign: "left",
                    buttons: [
                        {
                            text: "Build",
                            itemId: "build",
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
                            itemId: "reset",
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
                    layout: "fit",
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
