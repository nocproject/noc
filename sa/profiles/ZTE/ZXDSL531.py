##
## Vendor: Huawei
## OS:     VRP
## Compatible: 3.1
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="ZTE.ZXDSL531"
    method_pull_config="POST"
    path_pull_config="/psiBackupInfo.cgi"
    file_pull_config="backupsettings.xml"
    config_skip_head=0
    rogue_chars=None
    