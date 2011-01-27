from noc.fm.rules.correlation import *
from noc.fm.rules.classes.chassis import *
##
## Fan Failed/Recovered
##
class Fan_Failed_Recovered_Rule(CorrelationRule):
    name="Fan Failed/Recovered" 
    description="" 
    rule_type="Pair" 
    action=CLOSE_EVENT
    same_object=True
    window=0
    classes=[FanFailed,FanRecovered]
    vars=[]
