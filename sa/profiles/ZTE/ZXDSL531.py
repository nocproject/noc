##
## Vendor: ZTE
## OS:     ZXDSL531
## Compatible:
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="ZTE.ZXDSL531"
    method_pull_config="POST"
    path_pull_config="/psiBackupInfo.cgi"
    file_pull_config="backupsettings.xml"
    config_skip_head=0
    config_volatile=["<entry1 sessionID=.+?/>"]
    