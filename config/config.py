ALL_POSITON_LOW = ["ST", "CAM", "RW", "RM", "CM", "CDM", "RB", "CB", "RWB"]
ALL_POSITON_LOW_GK = ["ST", "CAM", "RW", "RM", "CM", "CDM", "RB", "CB", "RWB", "GK"]
ALL_POSITON = ["ST", "CF", "CAM", "RW", "LW", "RM", "LM", "CM", "CDM", "RB", "LB", "CB", "RWB", "LWB"]
POSITION_LOW_DICT = {"ST" : ["ST", "CF", "CAM"],
                     "CAM" : ["CF", "CAM", "LW", "RW"],
                     "RW" : ["RW", "LW", "CAM", "RM", "LW", "ST"],
                     "LW" : ["RW", "LW", "CAM", "RM", "LW", "ST"],
                     "RM" : ["RM", "LM", "RW", "LW"],
                     "LM" : ["RM", "LM", "RW", "LW"],
                     "CM" : ["CM", "CAM", "CDM"],
                     "CDM" : ["CDM", "CB", "CM", "RB", "LB"],
                     "RB" : ["RB", "LB", "RWB", "LWB", "RM", "LM"],
                     "LB" : ["RB", "LB", "RWB", "LWB", "RM", "LM"],
                     "CB" : ["CB", "RB", "LB", "CDM"],
                     "RWB" : ["RB", "LB", "RWB", "LWB", "RM", "LM"],
                     "LWB" : ["RB", "LB", "RWB", "LWB", "RM", "LM"],
                     "GK" : ["GK"]}
GENERAL_POSITION_NUM = {"ST":2, "RW":2, "CAM":2, "RM":2, "CM":4, "CDM":2, "CB":4, "RB":4, "GK":3}
BENCH_POSITION_NUM = {"ST":1, "RW":1, "CM":3, "CB":2, "GK":2}
BEST_ELEVEN_LIST = [[["ST", "CAM"], 2],
                    [["RW", "LW", "RM", "LM"], 2],
                    [["CM", "CDM"], 2],
                    [["RB", "LB"], 2],
                    [["CB"], 2],
                    [["GK"], 1]]

N = 1000000
REPLACEMENT_MAX = 3
YOUNG_OLD = 24
LEAGUE_LEVEL_MAX = 4