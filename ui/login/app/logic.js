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
                    NOC.msg.complete("Logged in");
                } else {
                    NOC.msg.failed("Failed to log in");
                }
            },
            function(response) {
                NOC.msg.failed("Failed to login");
            }
        );
    },

    clear: function() {
        $$("login_form").clear();
        $$("login_form").focus("user");
    }
};
