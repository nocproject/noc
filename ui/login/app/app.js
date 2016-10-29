//---------------------------------------------------------------------
// Application Login UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC login application");

Ext.application({
    name: "NOC",
    paths: {
        "NOC": "/ui/login/app"
    },

    launch: function() {
        Ext.create('NOC.LoginView');
    }
});
