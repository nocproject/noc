//
// Create console.* stub if missed
//
if (typeof(console) == "undefined") {
    console = {
        log: function(message) {},
        info: function(message) {},
        ward: function(message) {},
        error: function(message) {alert(message);}
    }
}
