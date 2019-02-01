//---------------------------------------------------------------------
// Header
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.HeaderPanel");
Ext.define("NOC.main.desktop.HeaderPanel", {
    extend: "Ext.Panel",
    region: "north",
    layout: {
        type: "hbox",
        align: "middle"
    },
    pollingInterval: 3600000,
    localStoreName: "header-last-update",
    border: false,
    bodyStyle: {
        "background-color": NOC.settings.branding_background_color + " !important",
        "color": NOC.settings.branding_color
    },
    collapsible: true,
    animCollapse: true,
    collapseMode: "mini",
    //split: true,
    header: false,
    app: null,
    bodyPadding: 4,
    //
    initComponent: function() {
        var me = this;
        // Last update menu
        me.lastUpdateButton = Ext.create("NOC.core.LookupField", {
            restUrl: "main/remotesystem/brief_lookup/",
            pageSize: false,
            typeAhead: false,
            editable: false,
            hidden: true,
            emptyText: __("Remote sync time"),
            margin: "0 5",
            hideTrigger: true,
            displayTpl: '<tpl for=".">{label}: {last_successful_load}</tpl>',
            tpl: "<ul class='x-list-plain'><tpl for='.'>" +
                "<li role='option' class='x-boundlist-item'>" +
                "<span>{label}:</span></span><span style='padding-left: 3px'>{last_successful_load}</span></li>" +
                "</tpl></ul>",
            listeners: {
                scope: me,
                select: me.onSelectLastUpdate
            }
        });
        // User menu
        me.userMenuButton = Ext.create("Ext.button.Button", {
            text: __("Anonymous"),
            scale: "small",
            glyph: NOC.glyph.user,
            hidden: true,
            menu: [
                {
                    text: __("About system ..."),
                    glyph: NOC.glyph.question_circle,
                    scope: me.app,
                    handler: me.app.onAbout
                },
                "-",
                {
                    text: __("User profile ..."),
                    glyph: NOC.glyph.cog,
                    scope: me.app,
                    handler: me.app.onUserProfile
                },
                {
                    itemId: "header_menu_change_password",
                    text: __("Change password ..."),
                    disabled: true, // Changed on login
                    glyph: NOC.glyph.lock,
                    scope: me.app,
                    handler: me.app.onChangeCredentials
                },
                "-",
                {
                    text: __("Logout"),
                    glyph: NOC.glyph.power_off,
                    scope: me.app,
                    handler: me.app.onLogout
                }
            ]
        });
        //
        Ext.apply(me, {
            items: [
                // NOC logo
                Ext.create("Ext.Img", {
                    src: NOC.settings.logo_url,
                    style: {
                        width: NOC.settings.logo_width + "px",
                        height: NOC.settings.logo_height + "px"
                    }
                }),
                // Bold NOC|
                {
                    xtype: "container",
                    html: "&nbsp;" + NOC.settings.brand + "|&nbsp;",
                    style: {
                        fontSize: "18px",
                        fontWeight: "bold"
                    },
                    border: false
                },
                // Installation name
                {
                    xtype: "container",
                    flex: 1,
                    html: NOC.settings.installation_name,
                    style: {
                        fontSize: "18px"
                    },
                    border: false
                },
                // Last update
                me.lastUpdateButton,
                // User menu
                me.userMenuButton,
                // Search field
                {
                    xtype: "searchfield",
                    padding: "0 0 0 4",
                    explicitSubmit: true,
                    scope: me,
                    handler: me.app.onSearch,
                    hidden: !NOC.settings.enable_search
                }
            ]
        });
        me.userProfileItem = me.userMenuButton.menu.getComponent("header_menu_change_password");
        Ext.TaskManager.start({
            run: me.pollingTask,
            interval: me.pollingInterval,
            scope: me
        });
        me.callParent();
    },
    // Change displayed username
    setUserName: function(username) {
        var me = this;
        me.userMenuButton.setText(username);
    },
    //
    hideUserMenu: function() {
        var me = this;
        me.userMenuButton.hide();
    },
    //
    showUserMenu: function(canChangeCredentials) {
        var me = this;
        me.userProfileItem.setDisabled(!canChangeCredentials);
        me.userMenuButton.show();
    },
    //
    onSelectLastUpdate: function(self) {
        window.localStorage.setItem(this.localStoreName, self.getValue());
    },
    //
    pollingTask: function() {
        var me = this;
        this.lastUpdateButton.getStore().load({
            scope: me,
            callback: function(records, operation, success) {
                if(success) {
                    var values = records.filter(function(item) {return item.id === window.localStorage.getItem(me.localStoreName)});
                    if(values.length > 0) {
                        me.lastUpdateButton.setValue(values[0]);
                    }
                    me.lastUpdateButton.show();
                }
            }
        });
    }
});
