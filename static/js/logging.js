//
// Create console.* stub if missed
//
if (!window.console) {
    console = {
        log: function(message) {},
        debug: function(message) {},
        info: function(message) {},
        warn: function(message) {},
        error: function(message) {alert(message);}
    }
}
