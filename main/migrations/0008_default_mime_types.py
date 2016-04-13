
from south.db import db
from django.db import models

MIME_TYPES=[
    (".pdf"      , "application/pdf"),
    (".sig"      , "application/pgp-signature"),
    (".spl"      , "application/futuresplash"),
    (".class"    , "application/octet-stream"),
    (".ps"       , "application/postscript"),
    (".torrent"  , "application/x-bittorrent"),
    (".dvi"      , "application/x-dvi"),
    (".gz"       , "application/x-gzip"),
    (".pac"      , "application/x-ns-proxy-autoconfig"),
    (".swf"      , "application/x-shockwave-flash"),
    (".tar.gz"   , "application/x-tgz"),
    (".tgz"      , "application/x-tgz"),
    (".tar"      , "application/x-tar"),
    (".zip"      , "application/zip"),
    (".mp3"      , "audio/mpeg"),
    (".m3u"      , "audio/x-mpegurl"),
    (".wma"      , "audio/x-ms-wma"),
    (".wax"      , "audio/x-ms-wax"),
    (".ogg"      , "application/ogg"),
    (".wav"      , "audio/x-wav"),
    (".gif"      , "image/gif"),
    (".jpg"      , "image/jpeg"),
    (".jpeg"     , "image/jpeg"),
    (".png"      , "image/png"),
    (".xbm"      , "image/x-xbitmap"),
    (".xpm"      , "image/x-xpixmap"),
    (".xwd"      , "image/x-xwindowdump"),
    (".css"      , "text/css"),
    (".html"     , "text/html"),
    (".htm"      , "text/html"),
    (".js"       , "text/javascript"),
    (".asc"      , "text/plain"),
    (".c"        , "text/plain"),
    (".cpp"      , "text/plain"),
    (".log"      , "text/plain"),
    (".conf"     , "text/plain"),
    (".text"     , "text/plain"),
    (".txt"      , "text/plain"),
    (".spec"     , "text/plain"),
    (".py"       , "text/plain"),
    (".dtd"      , "text/xml"),
    (".xml"      , "text/xml"),
    (".mpeg"     , "video/mpeg"),
    (".mpg"      , "video/mpeg"),
    (".mov"      , "video/quicktime"),
    (".qt"       , "video/quicktime"),
    (".avi"      , "video/x-msvideo"),
    (".asf"      , "video/x-ms-asf"),
    (".asx"      , "video/x-ms-asf"),
    (".wmv"      , "video/x-ms-wmv"),
    (".bz2"      , "application/x-bzip"),
    (".tbz"      , "application/x-bzip-compressed-tar"),
    (".tar.bz2"  , "application/x-bzip-compressed-tar"),
    (".odt"      , "application/vnd.oasis.opendocument.text"),
    (".ods"      , "application/vnd.oasis.opendocument.spreadsheet"),
    (".odp"      , "application/vnd.oasis.opendocument.presentation"),
    (".odg"      , "application/vnd.oasis.opendocument.graphics"),
    (".odc"      , "application/vnd.oasis.opendocument.chart"),
    (".odf"      , "application/vnd.oasis.opendocument.formula"),
    (".odi"      , "application/vnd.oasis.opendocument.image"),
    (".odm"      , "application/vnd.oasis.opendocument.text-master"),
    (".ott"      , "application/vnd.oasis.opendocument.text-template"),
    (".ots"      , "application/vnd.oasis.opendocument.spreadsheet-template"),
    (".otp"      , "application/vnd.oasis.opendocument.presentation-template"),
    (".otg"      , "application/vnd.oasis.opendocument.graphics-template"),
    (".otc"      , "application/vnd.oasis.opendocument.chart-template"),
    (".otf"      , "application/vnd.oasis.opendocument.formula-template"),
    (".oti"      , "application/vnd.oasis.opendocument.image-template"),
    (".oth"      , "application/vnd.oasis.opendocument.text-web")
]

class Migration:
    
    def forwards(self):
        for ext,mime_type in MIME_TYPES:
            db.execute("INSERT INTO main_mimetype(extension,mime_type) VALUES(%s,%s)",[ext,mime_type])
    
    def backwards(self):
        "Write your backwards migration here"
