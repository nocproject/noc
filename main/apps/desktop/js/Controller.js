//---------------------------------------------------------------------
// Desktop application controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Controller");

Ext.define("NOC.main.desktop.Controller", {
    extend: "Ext.app.Controller",
    views: ["NOC.main.desktop.Viewport"],

    init: function() {
        var me = this;
        console.log("Controller started");
        me.login_window = null;
        me.checkLogged();
        me.launched_tabs = {};
        me.control({
            // Navigation tree events
            "#navtree": {
                itemclick: me.onNavLaunch
            },
            // Header events
            "#header_menu_toggle": {
                click: me.onPanelsToggle
            },
            "#header_menu_userprofile": {
                click: me.onUserProfile
            },
            "#header_menu_change_password": {
                click: me.showChangeCredentials  
            },
            "#header_menu_logout": {
                click: me.doLogout
            },
            "#search": {
                search: me.onSearch
            }
        });
    },
    // Check session is authenticated
    checkLogged: function() {
        var me = this;
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/is_logged/",
            scope: me,
            success: function(response) {
                var status = Ext.decode(response.responseText);
                if (status)
                    me.on_login();
                else
                    me.showLogin();
            },
            failure: function(response) {
                me.showLogin();
            }
        }); 
    },
    // Called when session is authenticated or user logged in
    on_login: function() {
        var me = this;
        // Apply user settings
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/user_settings/",
            scope: me,
            success: function(response) {
                var settings = Ext.decode(response.responseText);
                // Set username in the header
                var display_name = "";
                if(settings["first_name"])
                    display_name += settings["first_name"];
                if(settings["last_name"]) {
                    if(display_name)
                        display_name += " ";
                    display_name += settings["last_name"];
                }
                if(!display_name)
                    display_name = settings["username"];
                Ext.getCmp("header").set_user_name(display_name);
                // Activate/deactivate change credentials menu
                Ext.getCmp("header").getComponent("user_display_name").menu
                    .getComponent("header_menu_change_password")
                    .setDisabled(!settings["can_change_credentials"]);
                // Activate user profile menu
                Ext.getCmp("header").getComponent("user_display_name").menu
                    .getComponent("header_menu_userprofile")
                    .setDisabled(false);
                // Display username button
                Ext.getCmp("header").getComponent("user_display_name").show();
                // Reset opened tabs
                me.launched_tabs = {};
                // Load menu
                me.updateMenu();
                // Change theme
                me.changeTheme(settings["theme"]);
            }
        });
        // Launch welcome application
        me.launchTab("NOC.main.welcome.Application", "Welcome", {});
    },
    // Show login window
    showLogin: function() {
        var me = this;
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/login_fields/",
            scope: this,
            success: function(response) {
                var fields = Ext.decode(response.responseText);
                me.login_window = Ext.create("NOC.main.desktop.Login", {
                    controller: this,
                    login_fields: fields
                });
            }
        });
    },
    // Start login sequence
    do_login: function(values) {
        var me = this;
        console.log("Do login");
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/login/",
            params: values,
            scope: this,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(r.status) {
                    // Login successfull
                    me.login_window.close();
                    me.login_window = null;
                    me.on_login();
                } else {
                    // Login failed
                    Ext.Msg.alert("Failed", r.message);
                }
            },
            failure: function(response) {
                Ext.Msg.alert("Failed", "Login failed due to internal error");
            }
        });
    },
    // Start logout sequence
    doLogout: function() {
        var me = this;
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/logout/",
            scope: this,
            success: function(response) {
                Ext.getCmp("header").getComponent("user_display_name").hide();
                Ext.getCmp("workplace").removeAll(true);
                me.updateMenu();
                me.showLogin();
            },
            failure: function(response) {
                Ext.Msg.alert("Failed", "Logout failed");
            }
        });
    },
    // Change current theme
    changeTheme: function(theme) {
        var me = this;
        if(theme == "default")
            theme = "ext-all.css";
        else
            theme = "ext-all-" + theme + ".css";
        Ext.util.CSS.swapStyleSheet("theme",
            "/static/resources/css/" + theme);
    },
    // Update menu
    updateMenu: function() {
        var me = this;
        console.log("Update menu");
        var store = Ext.getStore("NOC.main.desktop.NavTreeStore");
        if (!store.isLoading()) {
            store.load()
        }
    },
    // Application selected in nav tree
    onNavLaunch: function(view, record, item, index, event, opts) {
        var me = this;
        var reuse = !event.shiftKey;

        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/launch_info/",
            params: {
                node: record.data.id
            },
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                me.launchTab(data["class"], data["title"], data["params"],
                                opts.params.node, reuse);
            }
        });
    },
    // Launch application in tab
    launchTab: function(panel_class, title, params, node, reuse) {
        var me = this;
        if(reuse && node && me.launched_tabs[node]) {
            // Open tab
            Ext.getCmp("workplace").setActiveTab(me.launched_tabs[node]);
            return;
        }
        var tab = Ext.getCmp("workplace").launchTab(panel_class, title, params);
        if(node) {
            me.launched_tabs[node] = tab;
            tab.menu_node = node;
            tab.desktop_controller = this;
        }
    },
    // Toggle panels
    onPanelsToggle: function() {
        var me = this;
        Ext.getCmp("header").collapse(Ext.Component.DIRECTION_TOP);
        Ext.getCmp("nav").collapse(Ext.Component.DIRECTION_LEFT);
        Ext.getCmp("status").collapse(Ext.Component.DIRECTION_BOTTOM);
    },
    // Search text entered
    onSearch: function(value) {
        var me = this;
        me.launchTab("NOC.main.desktop.IFramePanel",
                        "Search",
                        {url: "/main/search/?" + Ext.urlEncode({query: value})});
    },
    // Show change credentials form
    showChangeCredentials: function() {
        var me = this;
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/change_credentials_fields/",
            scope: this,
            success: function(response) {
                var fields = Ext.decode(response.responseText);
                me.change_credentials_window = Ext.create("NOC.main.desktop.ChangeCredentials", {
                    controller: this,
                    change_credentials_fields: fields
                });
            }
        });
    },
    // Change credentials
    do_change_credentials: function(values) {
        var me = this;
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/change_credentials/",
            params: values,
            scope: this,
            success: function(response) {
                me.change_credentials_window.close();
                me.change_credentials_window = null;
            },
            failure: function(response) {
                var status = Ext.decode(response.responseText);
                Ext.Msg.alert("Failed", status["error"]);
            }
        });        
    },
    //
    on_close_tab: function(menu_id) {
        var me = this;
        if(me.launched_tabs[menu_id])
            delete me.launched_tabs[menu_id];
    },
    // Show user profile panel
    onUserProfile: function() {
        var me = this;
        me.launchTab("NOC.main.desktop.IFramePanel",
                        "User Profile",
                        {url: "/main/userprofile/profile/"});
    }
});
