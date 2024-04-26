//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.About");

Ext.define("NOC.main.desktop.About", {
  extend: "Ext.Window",
  title: __("About System"),
  layout: "fit",
  autoShow: true,
  resizable: false,
  closable: true,
  modal: true,
  width: 380,
  height: 190,
  app: null,
  aboutCfg: null,

  initComponent: function () {
    var me = this;
    Ext.apply(me, {
      items: [
        {
          xtype: "container",
          margin: 40,
          html: new Ext.XTemplate(
            '<div style="display: flex; flex-direction: row; padding: 20">\n' +
              '<img src="{logo_url}" style="width: 100px; height: 100px">\n' +
              '<div style="padding-left: 10">\n' +
              '<div style="font-size: 16pt; font-weight: bold">{brand} {version}</div>\n' +
              '<div style="font-size: 12pt; font-style: italic">{installation}</div>\n' +
              ' <tpl if="system_id">\n' +
              '  <div style="font-size: 12pt">System ID: {system_id}</div>\n' +
              " <tpl elseif='brand === \"NOC\"'>\n" +
              '  <div style="font-size: 12pt">Unregistred system</div>\n' +
              "</tpl>\n" +
              '<div style="">Copyright &copy; {copyright}</div>\n' +
              "<a href='http://getnoc.com/' target='_'>getnoc.com</a>\n" +
              "</div>" +
              "</div>",
          ).apply(me.aboutCfg),
        },
      ],
    });
    me.callParent();
  },
});
