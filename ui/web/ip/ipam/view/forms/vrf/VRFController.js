//---------------------------------------------------------------------
// ip.ipam.vrf form
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.vrf.VRFController");

Ext.define("NOC.ip.ipam.view.forms.vrf.VRFController", {
  extend: "Ext.app.ViewController",
  alias: "controller.ip.ipam.form.vrf",
  //
  onClose: function(){
    this.fireViewEvent("ipIPAMVRFCloseForm");
  },
  onSave: function(){
    var source = this.getView().up("[itemId=ip-ipam]").getViewModel().data.vrf,
      data = this.serialize(source);
    delete source["state"];
    delete source["state__label"];
    delete source["profile__label"];
    delete source["vrf_group__label"];
    delete source["project__label"];
    Ext.Ajax.request({
      url: "/ip/vrf/" + source.id + "/",
      method: "PUT",
      jsonData: Ext.merge(source, data),
      success: function(response){
        if(response.status === 200){
          NOC.msg.complete(__("Saved"));
        }
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
    });
    this.onClose();
  },
  serialize: function(){
    var data = {},
      allocatedTill = "allocated_till";
    // getLabel = function(name) {
    //     data[name + "__label"] = me.getView().down("[name=" + name + "]").getSelection().get("label");
    // };
    // combo
    // Ext.each([
    //     "profile",
    //     "vrf_group",
    //     "project"
    // ], getLabel, this);
    data[allocatedTill] = this.getView().down("[name=" + allocatedTill + "]").getSubmitValue();
    return data;
  },
});