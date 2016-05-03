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
                            template: __("NOC Login")
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
                                    placeholder: __("Username"),
                                    label: __("User"),
                                    required: true,
                                    invalidMessage: __("User name cannot be empty")
                                },
                                {
                                    view: "text",
                                    type: "password",
                                    name: "password",
                                    label: __("Password"),
                                    placeholder: __("Password"),
                                    required: true,
                                    invalidMessage: __("Password cannot be empty")
                                },
                                //
                                {
                                    cols: [
                                        {
                                            view: "button",
                                            value: __("Login"),
                                            width: 100,
                                            click: "NOC.login.app.logic.on_login",
                                            hotkey: "enter"
                                        },
                                        {
                                            view: "button",
                                            value: __("Reset"),
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
