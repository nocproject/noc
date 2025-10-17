//---------------------------------------------------------------------
// ip.ipam Rebase panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.RebasePanel");

Ext.define("NOC.ip.ipam.view.forms.prefix.RebasePanel", {
  extend: "NOC.core.FormPanel",
  alias: "widget.ip.ipam.form.rebase",
  requires: [
    "NOC.ip.vrf.LookupField",
  ],
  prefixUrl: "/ip/prefix/",

  initComponent: function(){
    var me = this;

    Ext.apply(me, {
      fields: [
        {
          name: "to_vrf",
          xtype: "ip.vrf.LookupField",
          fieldLabel: __("To VRF"),
          allowBlank: false,
        },
        {
          name: "to_prefix",
          xtype: "textfield",
          fieldLabel: __("To Prefix"),
          allowBlank: false,
          uiStyle: "medium",
        },
      ],
    });
    me.callParent()
  },

  preview: function(record){
    var me = this;
    me.currentPrefixId = record.id;
    me.setValues(record);
    me.setTitle(__("Rebase prefix ") + record.get("to_prefix"))
  },

  onClose: function(){
    var me = this;
    me.fireEvent("ipIPAMRebaseCloseForm");
  },

  save: function(data){
    var me = this;
    me.mask(__("Rebasing ..."));
    Ext.Ajax.request({
      url: me.prefixUrl + me.currentPrefixId + "/rebase/",
      method: "POST",
      scope: me,
      jsonData: {
        to_vrf: data.to_vrf,
        to_prefix: data.to_prefix,
      },
      success: function(){
        me.unmask();
        NOC.msg.complete(__("Rebased"));
        me.fireEvent("ipIPAMRebaseCloseForm");
      },
      failure: function(response){
        var message = "Error during rebase";
        if(response.responseText){
          try{
            message = Ext.decode(response.responseText).message
          } catch(err){
            console.error(err);
            console.log(response.responseText)
          }
        }
        me.unmask();
        NOC.error(message)
      },
    });
  },
});
