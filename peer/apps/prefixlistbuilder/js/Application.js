//---------------------------------------------------------------------
// peer.prefixlistbuilder application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.prefixlistbuilder.Application");

Ext.define("NOC.peer.prefixlistbuilder.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.peer.peeringpoint.LookupField",
        "Ext.ux.form.UCField"
    ],
    layout: {type: "vbox", align: "stretch"},
    border: 0,

    initComponent: function () {
        var me = this;

        me.form = Ext.create("Ext.form.Panel", {
            padding: 4,
            bodyPadding: 4,
            waitMsgTarget: true,
            defaults: {
                enableKeyEvents: true,
                listeners: {
                    specialkey: function (field, key) {
                        if (field.xtype != "textfield")
                            return;
                        switch (key.getKey()) {
                            case Ext.EventObject.ENTER:
                                me.onBuild();
                                break;
                            case Ext.EventObject.ESC:
                                me.onReset();
                                break;
                        }
                    }
                },
                xtype: "textfield",
                msgTarget: "side",
                size: 30
            },
            items: [
                {
                    fieldLabel: "Name",
                    name: "name",
                    emptyText: "Prefix list name ...",
                    allowBlank: true,
                    regex: /^[0-9a-zA-Z_\-]*$/,
                    invalidText: "Prefix list name must contains only 0-9,a-z,A-Z,-,_"
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
                    plugins: ["ucfield"]
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
                    scope: me,
                    handler: me.onBuild
                },
                {
                    text: "Reset",
                    itemId: "reset",
                    glyph: NOC.glyph.refresh,
                    disabled: false,
                    scope: me,
                    handler: me.onReset
                }
            ]

        });

        me.resultField = Ext.create("NOC.core.CMText", {
            readOnly: true
        });

        Ext.apply(me, {
            items: [
                me.form,
                me.resultField
            ]
        });
        me.callParent();
    },
    //
    onBuild: function () {
        var me = this,
            form = me.form.getForm();
        if (!form.isValid()) {
            return;
        }
        Ext.Ajax.request({
            url: "/peer/prefixlistbuilder/",
            method: "GET",
            params: form.getValues(),
            scope: me,
            mask: true,
            success: function (response) {
                var data = Ext.decode(response.responseText);
                me.resultField.setValue(data.prefix_list);
            },
            failure: function () {
                NOC.error("Failed to build prefix list");
            }
        });
    },
    onReset: function () {
        var me = this;
        me.form.getForm().reset();
    }
});
