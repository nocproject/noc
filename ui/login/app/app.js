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
        Ext.Ajax.request({
            // url: "http://localhost:3000/api/login/is_first_login/",
            url: "/api/login/is_first_login/",
            method: "GET",
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    Ext.create("NOC.LoginView");
                } else {
                    Ext.create("NOC.SetAdminView");
                }
            },
            failure: function() {
                Ext.toast({
                    html: '<div style="text-align: center;">Failed to get data</div>',
                    align: 't',
                    paddingY: 0,
                    width: '80%',
                    minHeight: 5,
                    border: false,
                    listeners: {
                        focusenter: function() {
                            this.close();
                        }
                    },
                    bodyStyle: {
                        color: 'white',
                        background: 'red',
                        "font-weight": 'bold'
                    },
                    style: {
                        background: 'red',
                        "border-width": '0px'
                    }
                });
            }
        });
    }
});
