//
// template JS gettext
//

class NOCGettext{
  constructor(){
    this.lang = "{locale}";
    this.translations = "{translations}";
  }
  gettext(s){
    return this.translations[s] || s;
  }
}

var nocgettext = new NOCGettext();
window._ = nocgettext.gettext.bind(nocgettext);
window.__ = nocgettext.gettext.bind(nocgettext);