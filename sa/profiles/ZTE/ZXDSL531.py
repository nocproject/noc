##
## Vendor: Huawei
## OS:     VRP
## Compatible: 3.1
##
import noc.sa.profiles

class Profile(noc.sa.profiles.Profile):
    name="ZTE.ZXDSL531"
    post_path_pull_config="/psiBackupInfo.cgi"
    post_pull_config_file_name="backupsettings.xml"
    config_skip_head=0