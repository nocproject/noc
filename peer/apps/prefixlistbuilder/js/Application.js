//---------------------------------------------------------------------
// peer.prefixlistbuilder application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.prefixlistbuilder.Application");

Ext.define("NOC.peer.prefixlistbuilder.Application", {
    extend: "NOC.core.Application",
    requires: ["NOC.peer.peeringpoint.LookupField", "Ext.ux.form.UCField"],
    layout: {
        type: "vbox",
        align: "center"
    },
    items :  [{
        xtype: 'form',
        title: 'Build prefix lists',
        frame: true,
        url: "/peer/prefixlistbuilder/",
        padding: 4,
        bodyPadding: 4,
        style: {
            marginTop: "10px"
        },
        listeners : {
            added : function(comp, container, pos, eOpts) {
                comp.resultPanel = Ext.create("Ext.panel.Panel", {
                            title: "Prefix list",
                            layout: "fit",
                            flex: 1,
                            width: "95%",
                            padding: 10,
                            border: false,
                            items: [{
                                xtype: "textareafield",
                                flex: 1,
                                resizable: false
                            }]
                        });
                container.add(comp.resultPanel);
                Ext.applyIf(comp.getForm(), { waitMsgTarget : comp.resultPanel.id });
            }
        },
        defaults: {
            enableKeyEvents: true,
            listeners: {
                specialkey: function(field, key) {
                    if (field.xtype != "textfield")
                        return;
                    var get_button = function(scope, name) {
                        return scope.ownerCt.down("toolbar").getComponent(name);
                    }
                    switch(key.getKey()) {
                        case Ext.EventObject.ENTER:
                            var b = get_button(field, "build");
                            key.stopEvent();
                            b.handler.call(b);
                            break;
                        case Ext.EventObject.ESC:
                            var b = get_button(field, "reset");
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
                fieldLabel: "AS-SET",
                name: "as_set",
                emptyText: "AS or AS-set",
                allowBlank: false,
                regex: /^AS(\d+|-\w+)(\s+AS(\d+|-\w+))*$/,
                plugins: [ 'ucfield' ]
            }
        ],
        buttonAlign: "left",
        buttons: [
            {
                text: "Build",
                itemId: "build",
                formBind: true,
                disabled: true,
                handler : function() {
                    var form = this.up("form").getForm();
                    form.submit({
                        method: "GET",
                        submitEmptyText : false,
                        params : { __format: "ext" },
                        waitMsg : "Compute prefix list",
                        success: function(form, action) {
                            var r = form.owner.resultPanel;
                            r.setTitle("Prefix list: " + action.result.name);
                            r.items.items[0].setValue(action.result.prefix_list);
                        }
                    });
                }
            },
            {
                text: "Reset",
                itemId: "reset",
                disabled: false,
                handler: function() {
                    this.up("form").getForm().reset();
                }
            }
        ]
    }]
});
