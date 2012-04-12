//---------------------------------------------------------------------
// Desktop application controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Controller");

Ext.define("NOC.main.desktop.Controller", {
    extend: "Ext.app.Controller",
    views: ["NOC.main.desktop.Viewport"],
    init: function() {
        console.log("Controller started");
        this.login_window = null;
        this.check_logged();
        this.launched_tabs = {};
        this.control({
            // Navigation tree events
            "#navtree": {
                itemclick: this.on_nav_launch
            },
            // Header events
            "#header_menu_toggle": {
                click: this.on_panels_toggle
            },
            "#header_menu_userprofile": {
                click: this.on_user_profile
            },
            "#header_menu_change_password": {
                click: this.show_change_credentials  
            },
            "#header_menu_logout": {
                click: this.do_logout
            },
            "#search": {
                search: this.on_search
            }
        });
    },
    // Check session is authenticated
    check_logged: function() {
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/is_logged/",
            scope: this,
            success: function(response) {
                var status = Ext.decode(response.responseText);
                if (status)
                    this.on_login();
                else
                    this.show_login();
            },
            failure: function(response) {
                this.show_login();
            }
        }); 
    },
    // Called when session is authenticated or user logged in
    on_login: function() {
        // Apply user settings
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/user_settings/",
            scope: this,
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
                this.launched_tabs = {};
                // Load menu
                this.update_menu();
                // Change theme
                this.change_theme(settings["theme"]);
            }
        });
        // Launch welcome application
        this.launch_tab("NOC.main.welcome.Application", "Welcome", {});
    },
    // Show login window
    show_login: function() {
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/login_fields/",
            scope: this,
            success: function(response) {
                var fields = Ext.decode(response.responseText);
                this.login_window = Ext.create("NOC.main.desktop.Login", {
                    controller: this,
                    login_fields: fields
                });
            }
        });
    },
    // Start login sequence
    do_login: function(values) {
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
                    this.login_window.close();
                    this.login_window = null;
                    this.on_login();
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
    do_logout: function() {
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/logout/",
            scope: this,
            success: function(response) {
                Ext.getCmp("header").getComponent("user_display_name").hide();
                Ext.getCmp("workplace").removeAll(true);
                this.update_menu();
                this.show_login();
            },
            failure: function(response) {
                Ext.Msg.alert("Failed", "Logout failed");
            }
        });
    },
    // Change current theme
    change_theme: function(theme) {
        if(theme == "default")
            theme = "ext-all.css";
        else
            theme = "ext-all-" + theme + ".css";
        Ext.util.CSS.swapStyleSheet("theme",
            "/static/resources/css/" + theme);
    },
    // Update menu
    update_menu: function() {
        console.log("Update menu");
        var store = Ext.getStore("NOC.main.desktop.NavTreeStore");
        if (!store.isLoading()) {
            store.load()
        }
    },
    // Application selected in nav tree
    on_nav_launch: function(view, record, item, index, event, opts) {
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
                this.launch_tab(data["class"], data["title"], data["params"],
                                opts.params.node, reuse);
            }
        });
    },
    // Launch application in tab
    launch_tab: function(panel_class, title, params, node, reuse) {
        if(reuse && node && this.launched_tabs[node]) {
            // Open tab
            Ext.getCmp("workplace").setActiveTab(this.launched_tabs[node]);
            return;
        }
        var tab = Ext.getCmp("workplace").launch_tab(panel_class, title, params);
        if(node) {
            this.launched_tabs[node] = tab;
            tab.menu_node = node;
            tab.desktop_controller = this;
        }
    },
    // Toggle panels
    on_panels_toggle: function() {
        Ext.getCmp("header").collapse(Ext.Component.DIRECTION_TOP);
        Ext.getCmp("nav").collapse(Ext.Component.DIRECTION_LEFT);
        Ext.getCmp("status").collapse(Ext.Component.DIRECTION_BOTTOM);
    },
    // Search text entered
    on_search: function(value) {
        this.launch_tab("NOC.main.desktop.IFramePanel",
                        "Search",
                        {url: "/main/search/?" + Ext.urlEncode({query: value})});
    },
    // Show change credentials form
    show_change_credentials: function() {
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/change_credentials_fields/",
            scope: this,
            success: function(response) {
                var fields = Ext.decode(response.responseText);
                this.change_credentials_window = Ext.create("NOC.main.desktop.ChangeCredentials", {
                    controller: this,
                    change_credentials_fields: fields
                });
            }
        });
    },
    // Change credentials
    do_change_credentials: function(values) {
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/change_credentials/",
            params: values,
            scope: this,
            success: function(response) {
                this.change_credentials_window.close();
                this.change_credentials_window = null;
            },
            failure: function(response) {
                var status = Ext.decode(response.responseText);
                Ext.Msg.alert("Failed", status["error"]);
            }
        });        
    },
    //
    on_close_tab: function(menu_id) {
        if(this.launched_tabs[menu_id])
            delete this.launched_tabs[menu_id];
    },
    // Show user profile panel
    on_user_profile: function() {
        this.launch_tab("NOC.main.desktop.IFramePanel",
                        "User Profile",
                        {url: "/main/userprofile/profile/"});
    }
});
