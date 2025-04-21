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
        // "NOC.core.CMText",
        "NOC.peer.peeringpoint.LookupField",
        "Ext.ux.form.UCField"
    ],
    layout: {
        type: "vbox",
        align: "stretch"
    },
    border: 0,
    autoScroll: true,

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
                        if (field.xtype !== "textfield")
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
                    fieldLabel: __("Name"),
                    name: "name",
                    emptytext: __("Prefix list name ..."),
                    allowBlank: true,
                    regex: /^[0-9a-zA-Z_\-]*$/,
                    invalidtext: __("Prefix list name must contains only 0-9,a-z,A-Z,-,_")
                },
                {
                    xtype: "peer.peeringpoint.LookupField",
                    fieldLabel: __("Peering Point"),
                    name: "peering_point",
                    allowBlank: false
                },
                {
                    fieldLabel: __("AS-SET"),
                    name: "as_set",
                    emptytext: __("AS or AS-set"),
                    allowBlank: false,
                    regex: /^AS(\d+|-\w+)(-\w+)*(:\S+)?(\s+AS(\d+|-\w+)(:\S+)?)*$/,
                    invalidtext: __("Enter list valid ASnumber (ex., AS1234) or as sets (ex. AS-MEGASET, AS-MEGA-SET)"),
                    plugins: ["ucfield"]
                }
            ],
            buttonAlign: "left",
            buttons: [
                {
                    text: __("Build"),
                    itemId: "build",
                    glyph: NOC.glyph.play,
                    formBind: true,
                    disabled: true,
                    scope: me,
                    handler: me.onBuild
                },
                {
                    text: __("Reset"),
                    itemId: "reset",
                    glyph: NOC.glyph.refresh,
                    disabled: false,
                    scope: me,
                    handler: me.onReset
                }
            ]

        });

        me.resultField = Ext.create("NOC.core.CMText", {
            readOnly: true,
            flex: 1
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
        me.mask("Building");
        Ext.Ajax.request({
            url: "/peer/prefixlistbuilder/",
            method: "GET",
            params: form.getValues(),
            scope: me,
            success: function (response) {
                var data = Ext.decode(response.responseText);
                me.unmask();
                if(data.success) {
                    NOC.info(data.message);
                    me.resultField.setValue(data.prefix_list);
                } else {
                    NOC.error(data.message);
                    me.resultField.setValue("")
                }
            },
            failure: function () {
                me.unmask();
                NOC.error("Failed to build prefix list");
            }
        });
    },
    onReset: function () {
        var me = this;
        me.form.getForm().reset();
    }
});
