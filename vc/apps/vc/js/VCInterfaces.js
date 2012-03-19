//---------------------------------------------------------------------
// VC Interfaces
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.VCInterfaces");

Ext.define("NOC.vc.vc.VCInterfaces", {
    extend: "Ext.Window",

    app: null,
    vc: null,
    interfaces: [],
    width: 600,
    height: 400,
    modal: true,
    autoShow: true,
    closable: true,

    initComponent: function() {
        var me = this,
            tpl = new Ext.XTemplate(
                // Unagged
                '<b><u>Untagged interfaces</u></b><br/>',
                '<tpl for="untagged">',
                    '<b>{managed_object_name}:</b> ',
                    '<tpl for="interfaces">{name}, </tpl>',
                    '<br/>',
                '</tpl>',
                // Tagged
                '<b><u>Tagged interfaces</u></b><br/>',
                '<tpl for="tagged">',
                    '<b>{managed_object_name}:</b> ',
                    '<tpl for="interfaces">{name}, </tpl>',
                    '<br/>',
                '</tpl>',
                // L3
                '<b><u>L3</u></b><br/>',
                '<tpl for="l3">',
                    '<b>{managed_object_name}:</b> ',
                    '<tpl for="interfaces">{name} (',
                    '{ipv4_addresses}',
                    '{ipv6_addresses}',
                    ')</tpl>',
                    '<br/>',
                '</tpl>'
            );
        Ext.apply(me, {
            title: Ext.String.format("Interfaces in VC {0} ({1})",
                                     me.vc.name, me.vc.l1),
            items: [
                {
                    xtype: "panel",
                    html: tpl.apply(me.interfaces),
                    layout: "fit"
                }
            ]
        });
        me.callParent();
    }
});
