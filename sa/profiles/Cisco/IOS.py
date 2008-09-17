from noc.sa.profiles import BaseProfile

class Profile(BaseProfile):
    pattern_lg_as_path_list=r"^(\s+\d+(?: \d+)*),"
    pattern_lg_best_path=r"(<A HREF.+?>.+?best)"
    requires_netmask_conversion=True