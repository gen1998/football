ALL_POSITON_LOW = ["ST", "CAM", "RW", "RM", "CM", "CDM", "RB", "CB", "RWB"]
ALL_POSITON_LOW_GK = ["ST", "CAM", "RW", "RM", "CM", "CDM", "RB", "CB", "RWB", "GK"]
ALL_POSITON = ["ST", "CF", "CAM", "RW", "LW", "RM", "LM", "CM", "CDM", "RB", "LB", "CB", "RWB", "LWB"]
POSITION_LOW_DICT = {"ST" : ["ST", "CF", "CAM"],
                     "CAM" : ["CF", "CAM", "LW", "RW"],
                     "RW" : ["RW", "LW", "CAM", "RM", "LW", "ST"],
                     "RM" : ["RM", "LM", "RW", "LW"],
                     "CM" : ["CM", "CAM", "CDM"],
                     "CDM" : ["CDM", "CB", "CM", "RB", "LB"],
                     "RB" : ["RB", "LB", "RWB", "LWB", "RM", "LM"],
                     "CB" : ["CB", "RB", "LB", "CDM"],
                     "RWB" : ["RB", "LB", "RWB", "LWB", "RM", "LM"],
                     "GK" : ["GK"]}

N = 1000000