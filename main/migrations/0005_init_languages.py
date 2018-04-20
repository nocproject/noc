# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Populate Languiages table with ISO639-1 codes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from south.db import db
from django.db import models
=======
##----------------------------------------------------------------------
## Populate Languiages table with ISO639-1 codes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from south.db import db
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

LANGUAGES=[
    ("Afar",            "Afaraf"),
    ("Abkhazian",       "Аҧсуа"),
    ("Avestan",         "avesta"),
    ("Afrikaans",       "Afrikaans"),
    ("Akan",            "Akan"),
    ("Amharic",         "አማርኛ"),
    ("Aragonese",       "Aragonés"),
    ("Arabic",          "العربية"),
    ("Assamese",         "অসমীয়া"),
    ("Avaric",          "авар мацӀ"),
    ("Aymara",          "aymar aru"),
    ("Azerbaijani",     "azərbaycan dili"),
    ("Bashkir",         "башҡорт теле"),
    ("Belarusian",      "Беларуская"),
    ("Bulgarian",       "български език"),
    ("Bihari",          "भोजपुरी"),
    ("Bislama",         "Bislama"),
    ("Bambara",         "bamanankan"),
    ("Bengali",         "বাংলা"),
    ("Tibetan",         "བོད་ཡིག"),
    ("Breton",          "brezhoneg"),
    ("Bosnian",         "bosanski jezik"),
    ("Catalan",         "Català"),
    ("Chechen",         "нохчийн мотт"),
    ("Chamorro",        "Chamoru"),
    ("Corsican",        "corsu; lingua corsa"),
    ("Cree",            "ᓀᐦᐃᔭᐍᐏᐣ"),
    ("Czech",           "česky"),
    ("Church Slavic",   "ѩзыкъ словѣньскъ"),
    ("Chuvash",         "чӑваш чӗлхи"),
    ("Welsh",           "Cymraeg"),
    ("Danish",          "Dansk"),
    ("German",          "Deutsch"),
    ("Divehi",           "ދިވެހި"),
    ("Dzongkha",        "རྫོང་ཁ"),
    ("Ewe",             "Ɛʋɛgbɛ"),
    ("Greek",           "Ελληνικά"),
    ("English",         "English"),
    ("Esperanto",       "Esperanto"),
    ("Spanish",         "Español;"),
    ("Estonian",        "Eesti"),
    ("Basque",          "euskara"),
    ("Persian",         "فارسی"),
    ("Fulah",           "Fulfulde"),
    ("Finnish",         "Suomi"),
    ("Fijian",          "Vosa Vakaviti"),
    ("Faroese",         "Føroyskt"),
    ("French",          "Français"),
    ("Western Frisian", "Frysk"),
    ("Irish",           "Gaeilge"),
    ("Scottish Gaelic", "Gàidhlig"),
    ("Galician",        "Galego"),
    ("Guaraní",         "Avañe'ẽ"),
    ("Gujarati",        "ગુજરાતી"),
    ("Manx",            "Gaelg"),
    ("Hausa",           "هَوُسَ"),
    ("Hebrew",          "עברית"),
    ("Hindi",           "हिन्दी"),
    ("Hiri Motu",       "Hiri Motu"),
    ("Croatian",        "Hrvatski"),
    ("Haitian",         "Kreyòl ayisyen"),
    ("Hungarian",       "Magyar"),
    ("Armenian",        "Հայերեն"),
    ("Herero",          "Otjiherero"),
    ("Interlingua",     "Interlingua"),
    ("Indonesian",      "Bahasa Indonesia"),
    ("Interlingue",     "Interlingue"),
    ("Igbo",            "Igbo"),
    ("Sichuan Yi",      "ꆇꉙ"),
    ("Inupiaq",         "Iñupiaq"),
    ("Ido",             "Ido"),
    ("Icelandic",       "Íslenska"),
    ("Italian",         "Italiano"),
    ("Inuktitut",       "ᐃᓄᒃᑎᑐᑦ"),
    ("Japanese",        "日本語"),
    ("Javanese",        "basa Jawa"),
    ("Georgian",        "ქართული"),
    ("Kongo",           "KiKongo"),
    ("Kikuyu",          "Gĩkũyũ"),
    ("Kwanyama",        "Kuanyama"),
    ("Kazakh",          "Қазақ тілі"),
    ("Kalaallisut",     "kalaallisut; kalaallit oqaasii"),
    ("Khmer",           "ភាសាខ្មែរ"),
    ("Kannada",         "ಕನ್ನಡ"),
    ("Korean",          "한국어"),
    ("Kanuri",          "Kanuri"),
    ("Kashmiri",        "कश्मीरी"),
    ("Kurdish",         "كوردی‎"),
    ("Komi",            "коми кыв"),
    ("Cornish",         "Kernewek"),
    ("Kirghiz",         "кыргыз тили"),
    ("Latin",           "Latine"),
    ("Luxembourgish",   "Lëtzebuergesch"),
    ("Ganda",           "Luganda"),
    ("Limburgish",      "Limburgs"),
    ("Lingala",         "Lingála"),
    ("Lao",             "ພາສາລາວ"),
    ("Lithuanian",      "Lietuvių kalba"),
    ("Latvian",         "Latviešu valoda"),
    ("Malagasy",        "Malagasy fiteny"),
    ("Marshallese",     "Kajin M̧ajeļ"),
    ("Māori",           "te reo Māori"),
    ("Macedonian",      "македонски јазик"),
    ("Malayalam",        "മലയാളം"),
    ("Mongolian",       "Монгол"),
    ("Marathi",         "मराठी"),
    ("Malay",           "بهاس ملايو‎"),
    ("Maltese",         "Malti"),
    ("Burmese",          "ဗမာစာ"),
    ("Nauru",           "Ekakairũ Naoero"),
    ("Norwegian Bokmål","Norsk bokmål"),
    ("North Ndebele",   "isiNdebele"),
    ("Nepali",          "नेपाली"),
    ("Ndonga",          "Owambo"),
    ("Dutch",           "Nederlands"),
    ("Norwegian Nynorsk","Norsk nynorsk"),
    ("Norwegian",       "Norsk"),
    ("South Ndebele",   "isiNdebele"),
    ("Navajo",          "Dinékʼehǰí"),
    ("Chichewa",        "chiCheŵa"),
    ("Occitan",         "Occitan"),
    ("Ojibwa",          "ᐊᓂᔑᓈᐯᒧᐎᓐ"),
    ("Oromo",           "Afaan Oromoo"),
    ("Oriya",           "ଓଡ଼ିଆ"),
    ("Ossetian",        "Ирон æвзаг"),
    ("Panjabi",         "ਪੰਜਾਬੀ"),
    ("Pāli",            "पाऴि"),
    ("Polish",          "Polski"),
    ("Pashto",          "پښتو"),
    ("Portuguese",      "Português"),
    ("Quechua",         "Runa Simi"),
    ("Raeto-Romance",   "rumantsch grischun"),
    ("Kirundi",         "kiRundi"),
    ("Romanian",        "română"),
    ("Russian",         "Русский"),
    ("Kinyarwanda",     "Ikinyarwanda"),
    ("Sanskrit",        "संस्कृतम्"),
    ("Sardinian",       "Sardu"),
    ("Sindhi",          "सिन्धी"),
    ("Northern Sami",   "Davvisámegiella"),
    ("Sango",           "yângâ tî sängö"),
    ("Serbo-Croatian",  "Српскохрватски"),
    ("Sinhala",          "සිංහල"),
    ("Slovak",          "Slovenčina"),
    ("Slovenian",       "Slovenščina"),
    ("Samoan",          "gagana fa'a Samoa"),
    ("Shona",           "chiShona"),
    ("Somali",          "Soomaaliga"),
    ("Albanian",        "Shqip"),
    ("Serbian",         "српски језик"),
    ("Swati",           "SiSwati"),
    ("Southern Sotho",  "Sesotho"),
    ("Sundanese",       "Basa Sunda"),
    ("Swedish",         "Svenska"),
    ("Swahili",         "Kiswahili"),
    ("Tamil",           "தமிழ்"),
    ("Telugu",           "తెలుగు"),
    ("Tajik",           "тоҷикӣ"),
    ("Thai",            "ไทย"),
    ("Tigrinya",         "ትግርኛ"),
    ("Turkmen",         "Түркмен"),
    ("Tagalog",         "Tagalog"),
    ("Tswana",          "Setswana"),
    ("Tonga",           "faka Tonga"),
    ("Turkish",         "Türkçe"),
    ("Tsonga",          "Xitsonga"),
    ("Tatar",           "татарча"),
    ("Twi",             "Twi"),
    ("Tahitian",        "Reo Mā`ohi"),
    ("Uighur",          "Uyƣurqə"),
    ("Ukrainian",       "Українська"),
    ("Urdu",            "اردو"),
    ("Uzbek",           "Ўзбек"),
    ("Venda",           "Tshivenḓa"),
    ("Vietnamese",      "Tiếng Việt"),
    ("Volapük",         "Volapük"),
    ("Walloon",         "Walon"),
    ("Wolof",           "Wollof"),
    ("Xhosa",           "isiXhosa"),
    ("Yiddish",         "ייִדיש"),
    ("Yoruba",          "Yorùbá"),
    ("Zhuang",          "Saɯ cueŋƅ"),
    ("Chinese",         "中文"),
    ("Zulu",            "isiZulu"),
]

class Migration:
<<<<<<< HEAD

    def forwards(self):
        for lang,native in LANGUAGES:
            db.execute("INSERT INTO main_language(name,native_name,is_active) VALUES(%s,%s,%s)",[lang,native,lang=="English"])

=======
    
    def forwards(self):
        for lang,native in LANGUAGES:
            db.execute("INSERT INTO main_language(name,native_name,is_active) VALUES(%s,%s,%s)",[lang,native,lang=="English"])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        "Write your backwards migration here"
