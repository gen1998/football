import numpy as np
import pandas as pd

import random

import sys
sys.path.append("../")

from src.object import *
from config.formation import *
from config.config import *


def random_create_formation():
    random_int = np.random.randint(1, N)
    formation_name = list(FORMATION_DICT.keys())[random_int%len(FORMATION_DICT.keys())]
    select_foramtion = FORMATION_DICT[formation_name]
    
    output = Formation(name=select_foramtion["name"],
                       formation=select_foramtion["formation"],
                       formation_priority=select_foramtion['formation_priority'],
                       formation_num=select_foramtion['formation_num'],
                       formation_assist_rate=select_foramtion['formation_assist_rate'],
                       formation_shooting_rate=select_foramtion['formation_shooting_rate'])
    return output

"""
def change_players(team, df_name_list):
    retire_player = [p for p in team.affilation_players if p.retire==1]
    
    num_gk = len([p for p in retire_player if p.main_position=="GK"])
    num_fieldplayer = len(retire_player) - num_gk
    
    # チームから外す あとあとそれぞれの人間についてチームから外す操作を付け加えたい
    team.affilation_players = [p for p in team.affilation_players if p not in retire_player]
    
    new_players = random_create_players(num_fieldplayer, num_gk, team.min_rate, team.max_rate+15, df_name_list, 20)
    
    team.affilation_players.extend(new_players)


def random_create_players(num_fieldplayer, num_gk, min_rate, max_rate, df_name_list, age_mean=27):
    players = []
    count = 0
    df_name_list = random.sample(df_name_list, num_fieldplayer+num_gk)

    while True:
        if count>=num_fieldplayer:
            break
        age = min(max(np.int8(np.round(np.random.normal(age_mean, 4))), 18), 37)
        pac = np.int8(np.round(np.random.normal(65, 15)))
        sho = np.int8(np.round(np.random.normal(60, 10)))
        pas = np.int8(np.round(np.random.normal(60, 10)))
        dri = np.int8(np.round(np.random.normal(60, 15)))
        de = np.int8(np.round(np.random.normal(60, 10)))
        if de>70:
            phy = np.int8(np.round(np.random.normal(de, 5)))
        else:
            phy = np.int8(np.round(np.random.normal(60, 10)))
        injury_possibility = np.random.normal(0.03, 0.02) + max((pac-85)*0.005, 0)

        if pac>99 or de>99 or sho>99 or pas>99 or dri>99 or phy>99:
            continue

        A = FieldPlayer(age=age, name=df_name_list[count], position=None,
                        pace=pac, shooting=sho, passing=pas,
                        dribbling=dri, defending=de, physicality=phy,
                        injury_possibility=injury_possibility)

        A.select_main_position()
        if A.main_rate<min_rate or A.main_rate>max_rate:
            continue
        A.cal_all_rate()
        players.append(A)
        count += 1

    count = 0

    while True:
        if count>=num_gk:
            break

        age = min(max(np.int8(np.round(np.random.normal(age_mean, 4))), 18), 37)
        div = np.int8(np.round(np.random.normal(65, 15)))
        han = np.int8(np.round(np.random.normal(div, 5)))
        kic = np.int8(np.round(np.random.normal(60, 10)))
        ref = np.int8(np.round(np.random.normal(div, 5)))
        spe = np.int8(np.round(np.random.normal(60, 15)))
        pos = np.int8(np.round(np.random.normal(div, 5)))

        if div>99 or han>99 or kic>99 or ref>99 or spe>99 or pos>99:
            continue

        A = GK(name=df_name_list[num_fieldplayer+count], age=age, position="GK",
               diving=div, handling=han, kicking=kic,
               reflexes=ref, speed=spe, positioning=pos)
        
        A.cal_rate()
        A.cal_all_rate()

        if A.main_rate<min_rate or A.main_rate>max_rate:
            continue

        players.append(A)
        count += 1
    
    return players
"""