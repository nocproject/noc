//---------------------------------------------------------------------
// VC Interfaces
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.ProjectResources");

Ext.define("NOC.project.project.ProjectResources", {
  extend: "Ext.panel.Panel",
  app: null,
  vc: null,
  interfaces: [],
  layout: "fit",
  autoScroll: true,

  initComponent: function(){
    var me = this;

    me.closeButton = Ext.create("Ext.button.Button", {
      text: __("Close"),
      glyph: NOC.glyph.arrow_left,
      scope: me,
      handler: me.onClose,
    });

    Ext.apply(me, {
      items: [
        {
          xtype: "panel",
          padding: 4,
          layout: "fit",
          tpl: '<table border="1" width="100%">\n    <tpl if="vc.length">\n        <tr>\n            <th colspan="2"><b>VC</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="vc">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="dnszone.length">\n        <tr>\n            <th colspan="2"><b>DNS Zones</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="dnszone">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="as.length">\n        <tr>\n            <th colspan="2"><b>AS</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="as">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="asset.length">\n        <tr>\n            <th colspan="2"><b>as-set</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="asset">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="vrf.length">\n        <tr>\n            <th colspan="2"><b>VRF</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="vrf">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="prefix.length">\n        <tr>\n            <th colspan="2"><b>Prefix</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="prefix">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="address.length">\n        <tr>\n            <th colspan="2"><b>Address</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="address">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n\n    <tpl if="peer.length">\n        <tr>\n            <th colspan="2"><b>Peers</b></th>\n        </tr>\n    </tpl>\n    <tpl foreach="peer">\n        <tr>\n            <td>{label}</td>\n            <td style="width: 100px">{state__label}</td>\n        </tr>\n    </tpl>\n    <tpl if="interface.length">\n        <tr>\n            <th colspan="2"><b>Interfaces</b></th>\n        </tr>\n        <tpl foreach="interface">\n            <tr>\n                <td>{label}</td>\n                <td style="width: 100px">{state__label}</td>\n            </tr>\n        </tpl>\n    </tpl>\n    <tpl if="subinterface.length">\n        <tr>\n            <th colspan="2"><b>SubInterfaces</b></th>\n        </tr>\n        <tpl foreach="subinterface">\n            <tr>\n                <td>{label}</td>\n                <td style="width: 100px">-</td>\n            </tr>\n        </tpl>\n    </tpl>\n</table>',
        },
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.closeButton,
            me.refreshButton,
          ],
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(record){
    var me = this;
    Ext.Ajax.request({
      url: "/project/project/" + record.get("id") + "/resources/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.items.items[0].update(data);
      },
      failure: function(){
        NOC.error("Failed to get resources");
      },
    });
  },
  //
  onClose: function(){
    var me = this;
    me.app.showForm();
  },
});
