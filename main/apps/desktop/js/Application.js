//---------------------------------------------------------------------
// main.desktop application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Application");
Ext.define("NOC.main.desktop.Application", {
    extend: "Ext.Viewport",
    layout: "border",
    requires: [
        "Ext.ux.form.SearchField",
        "NOC.core.TagsField"
    ],

    initComponent: function() {
        var me = this;
        me.restartReason = null;
        // Setup helpers
        NOC.run = Ext.bind(me.launchTab, me);
        NOC.launch = Ext.bind(me.launchApp, me);
        //
        me.launchedTabs = {};
        me.idleTimeout = 0;
        me.idleTimerId = -1;
        // Create panels
        me.headerPanel = Ext.create("NOC.main.desktop.HeaderPanel", {app: me});
        me.navPanel = Ext.create("NOC.main.desktop.NavPanel", {app: me});
        me.workplacePanel = Ext.create("NOC.main.desktop.WorkplacePanel", {app: me});
        //
        Ext.apply(me, {
            items: [
                me.headerPanel,
                me.navPanel,
                me.workplacePanel
            ]
        });
        me.callParent();
        // Set unload handler
        Ext.EventManager.addListener(window, "beforeunload",
            me.onUnload, me, {normalized: false});
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        console.log("NOC application ready");
        me.checkLogged();
        me.launchAppsFromHistory();
    },
    // Launch applications from URL
    launchAppsFromHistory: function() {
        var h = Ext.History.getHash();

        if(h) {
            // Open application tab
            var p = h.split("/"),
                app = p[0],
                args = p.slice(1);
            if(args.length > 0) {
                NOC.launch(app, "history", {args: args});
            } else {
                NOC.launch(app);
            }
        }
    },
    // Show About screen
    onAbout: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/main/desktop/about/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                Ext.create("NOC.main.desktop.About", {
                    version: data.version,
                    installation: data.installation
                });
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },
    // Launch application in tab
    launchTab: function(panel_class, title, params, node, reuse) {
        var me = this;
        if(reuse && node && me.launchedTabs[node]) {
            // Open tab
            me.workplacePanel.setActiveTab(me.launchedTabs[node]);
        } else {
            // Launch new tab
            var tab = me.workplacePanel.launchTab(panel_class, title, params, node);
            if (node) {
                me.launchedTabs[node] = tab;
            }
        }
    },
    launchApp: function(app, cmd, data) {
        var me = this;
        // iframe shortcut
        if(app === "iframe") {
            me.launchTab(
                "NOC.main.desktop.IFramePanel",
                data.title,
                {url: data.url}
            );
            return;
        }
        //
        var url = "/" + app.replace(".", "/") + "/launch_info/";
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                var li = Ext.decode(response.responseText),
                    params = {};
                if(cmd) {
                    params.cmd = Ext.merge({}, data);
                    params.cmd.cmd = cmd;
                }
                Ext.merge(params, li.params);
                me.launchTab(
                    li.class,
                    li.title,
                    params
                );
            },
            failure: function() {
                NOC.error("Failed to launch application " + app);
            }
        });
    },
    // Called when application tab closed
    onCloseApp: function(menuId) {
        var me = this;
        if(me.launchedTabs[menuId]) {
            delete me.launchedTabs[menuId];
        }
    },
    // Search text entered
    onSearch: function(value) {
        var me = this;
        NOC.launch("main.search", "search", {query: value});
    },
    // Toggle all panels except workplace
    onPanelsToggle: function() {
        var me = this;
        if(me.headerPanel.isHidden()) {
            me.headerPanel.show();
            me.navPanel.show();
            me.workplacePanel.setCollapsed();
        } else {
            me.headerPanel.hide();
            me.navPanel.hide();
            me.workplacePanel.setExpanded();
        }
    },
    // Show user profile panel
    onUserProfile: function() {
        var me = this;
        NOC.run(
            "NOC.main.userprofile.Application",
            "User Profile",
            {}
        );
    },
    // Show change credentials form
    onChangeCredentials: function() {
        var me = this;
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/change_credentials_fields/",
            scope: me,
            success: function(response) {
                var fields = Ext.decode(response.responseText);
                Ext.create("NOC.main.desktop.ChangeCredentials", {
                    app: me,
                    fields: fields
                });
            },
            failure: function() {
                NOC.error("Failed to get credentials fields");
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
                if (status) {
                    me.onLogin();
                } else {
                    me.showLogin();
                }
            },
            failure: function(response) {
                me.showLogin();
            }
        });
    },
    // Show Login window
    showLogin: function() {
        var me = this;
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/login_fields/",
            scope: this,
            success: function(response) {
                var fields = Ext.decode(response.responseText);
                me.loginWindow = Ext.create("NOC.main.desktop.Login", {
                    app: me,
                    fields: fields
                });
            }
        });
    },
    //
    login: function(values) {
        var me = this;
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/login/",
            params: values,
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(r.status) {
                    // Login successfull
                    if(me.loginWindow) {
                        me.loginWindow.close();
                        delete me.loginWindow;
                    }
                    me.onLogin();
                } else {
                    // Login failed
                    NOC.error("Failed to change credentials: " + r.message);
                }
            },
            failure: function(response) {
                Ext.Msg.alert("Failed", "Login failed due to internal error");
            }
        });
    },
    // Called when session is authenticated or user logged in
    onLogin: function() {
        var me = this;
        // Initialize state provider
        Ext.state.Manager.setProvider(Ext.create("NOC.core.StateProvider"));
        // Apply user settings
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/user_settings/",
            scope: me,
            success: function(response) {
                var settings = Ext.decode(response.responseText),
                    displayName = [];
                // Check theme
                if(settings.theme != NOC.settings.theme) {
                    // User has non-default theme
                    me.restartApplication("Applying theme changes");
                }
                // Save settings
                NOC.username = settings.username;
                // Build display name
                if(settings.first_name) {
                    displayName.push(settings.first_name);
                }
                if(settings.last_name) {
                    displayName.push(settings.last_name);
                }
                if(displayName.length === 0) {
                    displayName.push(settings.username);
                }
                me.headerPanel.setUserName(displayName.join(" "));
                // Display username button
                me.headerPanel.showUserMenu(settings.can_change_credentials);
                // Reset opened tabs
                me.launchedTabs = {};
                // Load menu
                me.updateMenu();
                // Setup idle timer
                me.setIdleTimeout(settings.idle_timeout);
            }
        });
        // Launch welcome application
        if(!Ext.History.getHash()) {
            me.launchTab("NOC.main.welcome.Application", "Welcome", {});
        }
    },
    // Start logout sequence
    onLogout: function() {
        var me = this;
        Ext.Ajax.request({
            method: "POST",
            url: "/main/desktop/logout/",
            scope: me,
            success: function(response) {
                me.stopIdleTimer();
                me.restartApplication("Logging out");
            },
            failure: function(response) {
                Ext.Msg.alert("Failed", "Logout failed");
            }
        });
    },
    // Update navigation menu
    updateMenu: function() {
        var me = this;
        me.navPanel.updateMenu();
    },
    //
    // Process autologout
    //

    // Setup idle timeout
    setIdleTimeout: function(timeout) {
        var me = this;

        me.stopIdleTimer();
        me.idleTimeout = timeout * 1000;
        if(me.idleTimeout) {
            //
            console.log("Set idle timeout to", me.idleTimeout, "ms");
            me.idleTimerId = Ext.Function.defer(me.onIdle, me.idleTimeout, me);
            Ext.getDoc().on({
                scope: me,
                mousemove: me.resetIdleTimer,
                keydown: me.resetIdleTimer
            });
        }
        //
        window.NOCIdleHandler = Ext.bind(me.resetIdleTimer, me);
    },
    //
    stopIdleTimer: function() {
        var me = this;
        if(me.idleTimerId != -1) {
            clearTimeout(me.idleTimerId);
            me.idleTimerId = -1;
            Ext.getDoc().un({
                scope: me,
                mousemove: me.resetIdleTimer,
                keydown: me.resetIdleTimer
            });
        }
    },
    //
    resetIdleTimer: function() {
        var me = this;
        clearTimeout(me.idleTimerId);
        if(me.idleTimeout) {
            me.idleTimerId = Ext.Function.defer(me.onLogout, me.idleTimeout, me);
        }
    },
    //
    onUnload: function(e) {
        var me = this,
            msg = "You're trying to close NOC application. Unsaved changes may be lost.";
        if(me.restartReason) {
            return;
        }
        if(e) {
            e.returnValue = msg;
        }
        if(window.event) {
            window.event.returnValue = msg;
        }
        return msg;
    },
    //
    restartApplication: function(reason) {
        var me = this;
        me.restartReason = reason;
        window.location.reload();
    },
    // Request full-screen mode
    requestFullscreen: function() {
        var me = this,
            element = document.body,
            method = element.requestFullScreen
                || element.webkitRequestFullScreen
                || element.mozRequestFullScreen
                || element.msRequestFullScreen;
        if(method) {
            method(element);
        }
    },
    exitFullscreen: function() {
        var me = this,
            method = element.exitFullScreen
                || element.webkitExitFullScreen
                || element.mozCancelFullScreen
                || element.msExitFullScreen;
        if(method) {
            method();
        }


    }
});
