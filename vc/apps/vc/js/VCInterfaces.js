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
            style = {
                t_style: "border: 1px solid gray; font-size: 10pt; width: 100%; cellpadding: 4px",
                h_style: "padding: 4px; border: 1px solid gray; text-align: center; font-weight: bold; background-color: #e0e0e0;",
                o_style: "font-weight: bold; padding: 4px; border: 1px solid gray",
                i_style: "padding: 4px; border: 1px solid gray"
            },
            tpl = new Ext.XTemplate(
                '<table style="{t_style}">',
                    // Untagged
                    '<tr><td colspan="2" style="{h_style}">Untagged interfaces</td></tr>',
                    '<tpl for="untagged">',
                        '<tr>',
                            '<td style="{parent.o_style}">{managed_object_name}</td>',
                            '<td style="{parent.i_style}"><tpl for="interfaces">{name}{[ xindex === xcount ? "" : ", "]}</tpl></td>',
                        '</tr>',
                    '</tpl>',
                    // Tagged
                    '<tr><td colspan="2" style="{h_style}">Tagged interfaces</td></tr>',
                    '<tpl for="tagged">',
                        '<tr>',
                            '<td style="{parent.o_style}">{managed_object_name}</td>',
                            '<td style="{parent.i_style}"><tpl for="interfaces">{name}{[ xindex === xcount ? "" : ", "]}</tpl></td>',
                        '</tr>',
                    '</tpl>',
                    // L3
                    '<tr><td colspan="2" style="{h_style}">L3</td></tr>',
                    '<tpl for="l3">',
                        '<tr>',
                            '<td style="{parent.o_style}">{managed_object_name}</td>',
                            '<td style="{parent.i_style}"><tpl for="interfaces">{name} (',
                                '{ipv4_addresses}; ',
                                '{ipv6_addresses}',
                            '){[ xindex === xcount ? "" : ", "]}</tpl></td>',
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
                    html: tpl.apply(Ext.Object.merge(style, me.interfaces)),
                    layout: "fit"
                }
            ]
        });
        me.callParent();
        console.log(tpl.apply(Ext.Object.merge(style, me.interfaces)));
    }
});
