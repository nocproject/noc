//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.About");

Ext.define("NOC.main.desktop.About", {
    extend: "Ext.Window",
    title: "About NOC",
    layout: "fit",
    autoShow: true,
    resizable: false,
    closable: true,
    modal: true,
    version: null,
    installation: null,
    width: 400,
    height: 132,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "container",
                    layout: "hbox",
                    items: [
                        Ext.create("Ext.Img", {
                            src: "/static/img/logo_black.svg",
                            width: 100,
                            height: 100,
                            padding: 8
                        }),
                        {
                            xtype: "container",
                            layout: "vbox",
                            padding: "8 8 8 0",
                            items: [
                                {
                                    xtype: "container",
                                    html: "NOC " + me.version,
                                    style: "font-size: 16pt; font-weight: bold"
                                },
                                {
                                    xtype: "container",
                                    html: me.installation,
                                    style: "font-size: 12pt; font-style: italic"
                                },
                                {
                                    xtype: "container",
                                    html: "Copyright &copy; 2007-2013, The NOC Project"
                                },
                                {
                                    xtype: "container",
                                    html: "<a href='http://nocproject.org/' target='_'>nocproject.org</a>"
                                }
                            ]
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
