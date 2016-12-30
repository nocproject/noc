//
// Simple JS gettext implementation
//

var NOCGettext = function() {
    this.lang = "en";
    this.translations = {};
};

NOCGettext.prototype.initialize = function() {
    var lang = document.getElementsByTagName("html")[0].getAttribute("lang");
    this.set_translation(lang);
};

NOCGettext.prototype.gettext = function(s) {
    var t = this.translations[s];
    if(t === undefined) {
        return s;
    }
    if(typeof t === "string") {
        return t;
    } else {
        return t[1];
    }
};

NOCGettext.prototype.ngettext = function() {
    console.log("ngettext is not implemented yet");
    return this.gettext(arguments[0]);
};

NOCGettext.prototype.set_translation = function(lang) {
    var me = this;
    // Get URL
    var links = document.getElementsByTagName("link"),
        url = null,
        xobj, i;
    //
    for(i = 0; i <= links.length; i++) {
        if(links[i].getAttribute("rel") === "gettext" && links[i].getAttribute("lang") === lang) {
            url = links[i].getAttribute("href");
            break;
        }
    }
    // Reset to english when improperly configured
    if ((!url) || (url.search("/en.json") != -1)) {
        this.lang = "en";
        this.translations = {};
        return;
    }
    //
    this.lang = lang;
    // Get translation
    xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open("GET", url, false);
    xobj.send(null);
    if(xobj.status === 200) {
        me.lang = lang;
        me.translations = JSON.parse(xobj.responseText);
        me.compile_plurals();
    }
};

NOCGettext.prototype.plural_index = function(n) {
    // English fallback
    if(n > 1) {
        return 1;
    } else {
        return 0;
    }
};

NOCGettext.prototype.compile_plurals = function () {
    // English plurals
    var plurals = "nplurals = 2; plural = n ? 1 : 0",
        code;
    // Translation plurals
    if(this.translations[""] && this.translations[""]["Plural-Forms"]) {
        plurals = this.translations[""]["Plural-Forms"];
    }
    // Build function
    code = "(function(n) {" + plurals + ";return plural;})";
    this.plural_index = eval(code);
};

nocgettext = new NOCGettext();
nocgettext.initialize();
_ = nocgettext.gettext.bind(nocgettext);
__ = nocgettext.gettext.bind(nocgettext);
ngettext = nocgettext.ngettext.bind(nocgettext);
