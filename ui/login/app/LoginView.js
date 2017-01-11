//---------------------------------------------------------------------
// NOC.login application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.LoginView");

Ext.define('NOC.LoginView', {
    extend: 'Ext.window.Window'
    , xtype: 'login'
    , autoShow: true
    , closable: false
    , resizable: false
    , title: __("NOC Login")
    , layout: 'fit'
    , modal: true
    , defaultListenerScope: true
    , defaultFocus: 'user'
    , defaultButton: 'okButton'
    , referenceHolder: true
    , requires: [
        'Ext.form.Panel',
        'Ext.window.Toast'
    ]
    , viewModel: 'default'
    , items: {
        xtype: 'form'
        , padding: 15
        , reference: 'loginForm'
        , fixed: true
        , border: false
        , bodyStyle: {
            background: '#e0e0e0',
            padding: '10px'
        }
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
            , reference: 'okButton'
            , margin: '15 0 0 200'
            , width: 50
            , formBind: true
            , handler: 'onLoginClick'
            , text: __('Login')
            , autoEl: {
                // tag: 'input',
                // type: 'submit'
            }
            , listeners: {
                beforerender: function() {
                    if(!Ext.isIE) {
                        Ext.apply(this.autoEl, {type: 'submit'})
                    }
                }
            }
        }]
    }
    , onLoginClick: function() {
        var me = this,
            params = Ext.encode({
                jsonrpc: '2.0',
                method: 'login',
                params: [me.getViewModel().getData()]
            });
        if(params !== undefined) {
            Ext.Ajax.request({
                url: '/api/login/'
                , params: params
                , method: 'POST'
                , success: me.onLoginSuccess
                , failure: me.onLoginFailure
            });
        }
    }
    , onLoginFailure: function() {
        Ext.toast({
            html: '<center>' + __('Failed to log in') + '</center>',
            align: 't',
            closable: false,
            spacing: 0,
            paddingY: 0,
            width: '100%',
            bodyStyle: {
                background: 'red',
                Color: 'white'
            }
        });
    }
    , onLoginSuccess: function(response) {
        var me = this;
        try {
            var o = Ext.decode(response.responseText);
            if(true !== o.result) {
                me.onLoginFailure();
            } else {
                var param = Ext.urlDecode(location.search);
                if('uri' in param) {
                    document.location = param.uri;
                } else {
                    document.location = '/';
                }
            }
        } catch(e) {
            Ext.toast({
                html: '<center>' + __('Failed to log in') + '</center>',
                align: 't',
                closable: false,
                spacing: 0,
                paddingY: 0,
                width: '100%',
                bodyStyle: {
                    background: 'red',
                    Color: 'white'
                }
            });
        }
    }

// , afterRender: function(cmp) {
//     if(cmp.hasOwnProperty('inputEl')) {
//         cmp.inputEl.set({
//             autocomplete: 'on'
//         });
//     }
// }
});