from noc.fm.rules.correlation import *
from noc.fm.rules.classes.dot11 import *
##
## Rogue AP Detected/Removed
##
class Rogue_AP_Detected_Removed_Rule(CorrelationRule):
    name="Rogue AP Detected/Removed"
    description=""
    rule_type="Pair"
    action=CLOSE_EVENT
    same_object=True
    window=3600
    classes=[RogueAPDetected,RogueAPRemoved]
    vars=["mac","ap"]
