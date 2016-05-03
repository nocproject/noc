NOC.namespace("NOC.login.app");

NOC.login.app.logic = {
    init: function () {
        // Build UI objects
        webix.ui(NOC.login.app.ui);
    },

    on_login: function() {
                if (!$$("login_form").validate()) {
            return;
        }
        data = $$("login_form").getValues();
        API.login.login(data).then(
            function(result) {
                if(result === true) {
                    document.location = NOC.login.app.original_uri;
                } else {
                    NOC.msg.failed(__("Failed to log in"));
                }
            },
            function(response) {
                NOC.msg.failed(__("Failed to login"));
            }
        );
    },

    clear: function() {
        $$("login_form").clear();
        $$("login_form").focus("user");
    }
};
