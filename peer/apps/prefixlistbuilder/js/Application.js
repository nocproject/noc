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
    layout: { type: 'vbox', align: 'stretch' },
    border: 0,
    items :  [{
        xtype: "container",
        items: [{
            xtype: 'form',
            border: 0,
            url: "/peer/prefixlistbuilder/",
            padding: 4,
            bodyPadding: 4,
            waitMsgTarget : true,
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
                },
                xtype: "textfield",
                msgTarget : "side",
                size: 30
            },
            items: [
                {
                    fieldLabel: "Name",
                    name: "name",
                    emptyText: "Prefix list name ...",
                    allowBlank: true,
                    regex: /^[0-9a-zA-Z_\-]*$/,
                    invalidText: "Prefix list name must contains only 0-9,a-z,A-Z,'-','_'"
                },
                {
                    xtype: "peer.peeringpoint.LookupField",
                    fieldLabel: "Peering Point",
                    name: "peering_point",
                    allowBlank: false
                },
                {
                    fieldLabel: "AS-SET",
                    name: "as_set",
                    emptyText: "AS or AS-set",
                    allowBlank: false,
                    regex: /^AS(\d+|-\w+)(-\w+)*(:\S+)?(\s+AS(\d+|-\w+)(:\S+)?)*$/,
                    invalidText: "Enter list valid ASnumber (ex., AS1234) or as sets (ex. AS-MEGASET, AS-MEGA-SET)",
                    plugins: [ 'ucfield' ]
                }
            ],
            buttonAlign: "left",
            buttons: [
                {
                    text: "Build",
                    itemId: "build",
                    glyph: NOC.glyph.play,
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
                                form.owner.up("panel").down("textareafield").setValue(action.result.prefix_list);
                            }
                        });
                    }
                },
                {
                    text: "Reset",
                    itemId: "reset",
                    glyph: NOC.glyph.refresh,
                    disabled: false,
                    handler: function() {
                        this.up("form").getForm().reset();
                    }
                }
            ]
        }]
    },
    {
        xtype: "textarea",
        fieldStyle: {"padding-left": "7px"},
        flex: 1
    }
    ]
});
