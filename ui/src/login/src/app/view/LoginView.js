//---------------------------------------------------------------------
// NOC.login application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.login.view.LoginView");

Ext.define('NOC.login.view.LoginView', {
    extend: 'Ext.window.Window'
    , xtype: 'login'
    , autoShow: true
    , closable: false
    , title: __("NOC Login")
    , layout: 'fit'
    , modal: true
    , defaultListenerScope: true
    , defaultFocus: 'user'
    , referenceHolder: true
    , requires: [
        'Ext.form.Panel',
        'Ext.window.Toast'
    ]
    , viewModel: 'default'
    , items: [{
        xtype: 'form'
        , padding: 15
        , reference: 'loginForm'
        , fixed: true
        , autoEl: {
            tag: 'form'
        }
        , defaults: {
            anchor: '100%'
            , allowBlank: false
            , enableKeyEvents: true
            , xtype: 'textfield'
        }
        , items: [{
            xtype: 'displayfield'
            , value: __('Type username and password:')
            , hideLabel: true
        }, {
            xtype: 'textfield'
            , itemId: 'user'
            , name: 'user'
            , bind: '{user}'
            , fieldLabel: __('User')
            , blankText: __('User name cannot be empty')
            // , listeners: {
            //     afterrender: 'afterRender'
            // }
        }, {
            xtype: 'textfield'
            , itemId: 'password'
            , name: 'password'
            , bind: '{password}'
            , fieldLabel: __('Password')
            , blankText: __('Password cannot be empty')
            , inputType: 'password'
            // , listeners: {
            //     afterrender: 'afterRender'
            // }
        }, {
            xtype: 'button'
            , margin: '15 0 0 200'
            , formBind: true
            , handler: 'onLoginClick'
            , autoEl: {
                tag: 'input',
                value: __('Login'),
                type: 'submit'
            }
        }]
    }]
    , onLoginClick: function () {
        var me = this,
            params = Ext.encode({
                jsonrpc: '2.0',
                method: 'login',
                params: [me.getViewModel().getData()]
            });
        if (params !== undefined) {
            Ext.Ajax.request({
                url: '/api/login/api/login/'
                , params: params
                , method: 'POST'
                , success: me.onLoginSuccess
                , failure: function(response) {
                    Ext.toast({
                        html: 'server-side failure with status code ' + response.status,
                        align: 't',
                        spacing: 0,
                        paddingY: 0,
                        width: '100%'
                    });
                }
            });
        }
    }
    , onLoginSuccess: function(response) {
        var o = Ext.decode(response.responseText);

        if(true !== o.result) {
            Ext.toast({
                html: __('Failed to log in'),
                align: 't',
                spacing: 0,
                paddingY: 0,
                width: '100%'
            });
        } else {
            var param = Ext.urlDecode(location.search);

            if('uri' in param) {
                console.log(param.uri);
                document.location = param.uri;
            } else {
                document.location = '/';
            }
        }
    }
// , afterRender: function(cmp) {
//     if(cmp.hasOwnProperty('inputEl')) {
//         cmp.inputEl.set({
//             autocomplete: 'on'
//         });
//     }
// }
})
;