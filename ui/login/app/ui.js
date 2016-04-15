NOC.namespace("NOC.login.app");

NOC.login.app.ui = {
    id: "login_panel",
    rows: [
        {},  // Top spacer
        {
            cols: [
                {},  // Left spacer
                {
                    rows: [
                        {
                            type: "header",
                            template: _("NOC Login")
                        },
                        // Login form
                        {
                            view: "form",
                            id: "login_form",
                            width: 300,
                            elementsConfig: {
                                labelWidth: 80
                            },
                            elements: [
                                {
                                    view: "text",
                                    name: "user",
                                    id: "user",
                                    placeholder: _("Username"),
                                    label: _("User"),
                                    required: true,
                                    invalidMessage: _("User name cannot be empty")
                                },
                                {
                                    view: "text",
                                    type: "password",
                                    name: "password",
                                    label: _("Password"),
                                    placeholder: _("Password"),
                                    required: true,
                                    invalidMessage: _("Password cannot be empty")
                                },
                                //
                                {
                                    cols: [
                                        {
                                            view: "button",
                                            value: _("Login"),
                                            width: 100,
                                            click: "NOC.login.app.logic.on_login",
                                            hotkey: "enter"
                                        },
                                        {
                                            view: "button",
                                            value: _("Reset"),
                                            width: 100,
                                            click: "NOC.login.app.logic.clear_form"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {}  // Right spacer
            ]
        },
        {}  // Bottom spacer
    ]
};
