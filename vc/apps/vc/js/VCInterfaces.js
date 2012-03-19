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
    autoScroll: "auto",
    maximizable: true,

    initComponent: function() {
        var me = this,
            tpl = new Ext.XTemplate(
                '<table border="1">',
                    // Untagged
                    '<tr><td colspan="2" align="center"><b>Untagged interfaces</b></td></tr>',
                    '<tpl for="untagged">',
                        '<tr>',
                            '<td>{managed_object_name}</td>',
                            '<td><tpl for="interfaces">{name}, </tpl></td>',
                        '</tr>',
                    '</tpl>',
                    // Tagged
                    '<tr><td colspan="2" align="center"><b>Tagged interfaces</b></td></tr>',
                    '<tpl for="tagged">',
                        '<tr>',
                            '<td>{managed_object_name}</td>',
                            '<td><tpl for="interfaces">{name}, </tpl></td>',
                        '</tr>',
                    '</tpl>',
                    // L3
                    '<tr><td colspan="2" align="center"><b>L3</b></td></tr>',
                    '<tpl for="l3">',
                        '<tr>',
                            '<td>{managed_object_name}</td>',
                            '<td><tpl for="interfaces">{name} (',
                                '{ipv4_addresses}',
                                '{ipv6_addresses}',
                            ')</tpl></td>',
                        '</tr>',
                    '</tpl>',
                '</table>'
            );
        Ext.apply(me, {
            title: Ext.String.format("Interfaces in VC {0} ({1})",
                                     me.vc.name, me.vc.l1),
            items: [
                {
                    xtype: "panel",
                    padding: 4,
                    html: tpl.apply(me.interfaces),
                    layout: "fit"
                }
            ]
        });
        me.callParent();
    }
});
