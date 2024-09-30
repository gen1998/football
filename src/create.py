import numpy as np

import sys
sys.path.append("../")

from src.object.team import Team
from src.object.formation import Formation
from src.object.player import Create_player
from config.formation import FORMATION_DICT
from config.config import N


def random_create_formation():
    random_int = np.random.randint(1, N)
    formation_name = list(FORMATION_DICT.keys())[random_int%len(FORMATION_DICT.keys())]
    select_foramtion = FORMATION_DICT[formation_name]
    
    output = Formation(name=select_foramtion["name"],
                       formation=select_foramtion["formation"],
                       formation_priority=select_foramtion['formation_priority'],
                       formation_num=select_foramtion['formation_num'],
                       formation_assist_rate=select_foramtion['formation_assist_rate'],
                       formation_shooting_rate=select_foramtion['formation_shooting_rate'],
                       formation_tired_vitality=select_foramtion['formation_tired_vitality'])
    return output

def create_team(num, team_name_list, 
                mean_rate=65, min_rate=40, 
                max_rate=100, age_mean=27, now_year=2000):
    teams = []

    for index in range(num):
        mean_rate_ = np.random.normal(mean_rate)
        Cp = Create_player(position_num={"ST":2, "RW":2, "CAM":2, "RM":2, "CM":4, "CDM":2, "CB":4, "RB":4, "GK":3}, 
                           min_rate=min_rate, max_rate=max_rate, 
                           age_mean=age_mean,
                           mean_rate=mean_rate_,
                           now_year=now_year)
        Cp.create_teams()
        players = Cp.players
        Cp = Create_player(position_num={"ST":1, "RW":1, "CM":1, "CB":1, "GK":1}, 
                           min_rate=min_rate, max_rate=max_rate, 
                           age_mean=age_mean,
                           mean_rate=mean_rate_,
                           now_year=now_year)
        
        Cp.create_teams(new=True)
        players.extend(Cp.players)
        formation = random_create_formation()
        T = Team(name=team_name_list[index], 
                 formation=formation,
                 before_rank=index+1)
        
        T.affilation_players = players
        teams.append(T)

    return teams
