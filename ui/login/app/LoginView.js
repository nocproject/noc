//---------------------------------------------------------------------
// NOC.login application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.LoginView");

__ = function(x) {return x}

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
        }],
        buttons: [{
            reference: 'okButton'
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
        var data = this.getViewModel().getData(),
            params = Ext.encode({
                user: data.user,
                password: data.password
        });
        if(params !== undefined) {
            Ext.Ajax.request({
                url: '/api/login/login'
                , params: params
                , method: 'POST'
                , success: Ext.Function.pass(this.onLoginSuccess, this.onLoginFailure)
                , failure: this.onLoginFailure
                , defaultPostHeader : 'application/json'
            });
        }
    }

    , onLoginFailure: function() {
        Ext.toast({
            html: '<div style="text-align: center;">' + __('Failed to log in') + '</div>',
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

    , onLoginSuccess: function(failureFunc, response) {
        var result = Ext.decode(response.responseText);
        if(result.status === true) {
            var param = Ext.urlDecode(location.search);
            if('uri' in param) {
                if(location.hash) { // web app
                    document.location = '/' + location.hash;
                } else { // cards
                    document.location = param.uri;
                }
            }
        } else {
            failureFunc();
        }
    }
});
