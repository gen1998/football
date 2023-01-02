import numpy as np
import pandas as pd

import random
import time
import uuid
import json

from tqdm import tqdm

import sys
sys.path.append("../")

from config.config import *
from src.apply import *
from src.utils import *

class FootBaller:
    def __init__(self, name, age, now_year, injury_possibility, grow_position_type, recovery_power):
        self.age = age
        self.name = name
        self.grow_min_age = min(max(np.int8(np.round(np.random.normal(24, 1))), 22), 26)
        self.grow_old_age_1 = min(max(np.int8(np.round(np.random.normal(29, 1))), 27), 31)
        self.grow_old_age_2 = max(np.int8(np.round(np.random.normal(33, 1))), 32)
        self.grow_position_type = grow_position_type

        self.injury = 0
        self.injury_possibility = injury_possibility
        self.retire = 0
        self.contract = 0
        self.uuid = uuid.uuid1()
        self.result = {}

        self.main_rate = None
        self.free_time = 0
        self.born_year = now_year-age
        self.register = 0

        self.grow_exp_dict = {}
        self.grow_type = random.choices(["legend", "genius", "general", "grass"], weights=[10, 60, 700, 230])[0]

        self.position_all_rate = {}
        self.position_all_rate_sorted = []
        self.index = None
    
        self.vitality = 100
        self.recovery_power = recovery_power

        self.today_playing_time = 0
        self.today_goal = 0
        self.today_assist = 0
        self.today_rating = 0

        self.partification = 0
        self.partification_position = None
        self.startup = 0

        self.rental = 0
        self.origin_team = None
        self.origin_team_name = ""
        self.b_team_count = 0

    def get_goal(self, season_name):
        self.today_goal += 1
        self.result[season_name]["goal"] += 1
    
    def get_assist(self, season_name):
        self.today_assist += 1
        self.result[season_name]["assist"] += 1
    
    def get_game_count(self, season_name):
        self.result[season_name]["試合数"] += 1
    
    def get_cs(self, season_name):
        self.result[season_name]["CS"] += 1
    
    def get_default(self, season_name):
        self.result[season_name]["怪我欠場"] += 1
    
    def get_injury(self, season_name):
        self.result[season_name]["怪我回数"] += 1
    
    def get_game_time(self, season_name, minute):
        self.today_playing_time += minute
        self.result[season_name]["出場時間"] += minute
    
    def get_position(self, season_name, position):
        if position in self.result[season_name]["ポジション"].keys():
            self.result[season_name]["ポジション"][position] += 1
        else:
            self.result[season_name]["ポジション"][position] = 1
    
    def get_man_of_the_match(self, season_name):
        self.result[season_name]["MOM"] += 1
    
    def recovery_vitality(self, off=False):
        if off:
            self.vitality = 100
        else:
            self.vitality = min(self.vitality+self.recovery_power, 100)
    
    def set_game_variable(self):
        self.today_goal = 0
        self.today_assist = 0
        self.today_playing_time = 0
        self.today_rating = 0
    
    def cal_rating(self, season_name, min_rate, max_rate, enemy_goal, result, all_time=90):
        random_rating = (self.position_all_rate[self.partification_position]-min_rate)/(max_rate-min_rate)*self.today_playing_time/all_time*min(np.random.normal(0.7, 0.2), 1.0)
        rating = 5.0+self.today_goal+self.today_assist*1.2+result+random_rating

        if self.partification_position in ["LB", "RB", "CB", "CDM", "GK"] and enemy_goal==0:
            rating+=1
        rating = min(rating, 10)
        self.today_rating = rating
        self.result[season_name]["合計評価点"] += rating
    
    def consider_retirement(self):
        if self.retire!=1 and self.main_rate<80:
            rate = 0.00132*self.age*self.age - 1.18 + np.random.normal(0, 0.1) + self.injury_possibility
            if rate > np.random.rand():
                self.retire = 1
        
        if (self.free_time>1 and self.age>=26) or self.free_time>3:
            self.retire = 1

        self.age += 1

    def set_contract(self):
        if self.rental!=1:
            self.free_time = 0
            self.b_team_count = 0
            self.contract = min(max(np.int8(np.round(np.random.normal((40 - self.age)/4, 0.5))), 1), 7)

class FieldPlayer(FootBaller):
    def __init__(self, name, age, now_year, position, pace, shooting, 
                 passing, dribbling, defending, physicality, 
                 injury_possibility=0, 
                 grow_position_type=None,
                 recovery_power=100):
        super().__init__(name, age, now_year, injury_possibility, grow_position_type, recovery_power)
        self.main_position = position
        self.pace = pace
        self.shooting = shooting
        self.passing = passing
        self.dribbling = dribbling
        self.defending = defending
        self.physicality = physicality
        self.main_rate = self.cal_rate(self.main_position)

        self.pace_initial = pace
        self.shooting_initial = shooting
        self.passing_initial = passing
        self.dribbling_initial = dribbling
        self.defending_initial = defending
        self.physicality_initial = physicality

        self.pace_exp = 0.0
        self.shooting_exp = 0.0
        self.passing_exp = 0.0
        self.dribbling_exp = 0.0
        self.defending_exp = 0.0
        self.physicality_exp = 0.0
    
    def cal_rate(self, position=None):
        """
        if position=='ST':
            pac, sho, pas, dri, de, phy = 0.10, 0.80, 0.00, 0.03, 0.00, 0.10
        if position=='CAM' or position=='CF':
            pac, sho, pas, dri, de, phy = 0.10, 0.20, 0.38, 0.30, 0.00, 0.05
        if position=='CM':
            pac, sho, pas, dri, de, phy = 0.05, 0.05, 0.58, 0.20, 0.10, 0.05
        if position=='CDM':
            pac, sho, pas, dri, de, phy = 0.03, 0.00, 0.30, 0.10, 0.40, 0.20

        if position=='CB':
            pac, sho, pas, dri, de, phy = 0.08, 0.00, 0.00, 0.00, 0.75, 0.20

        if position=='RW' or position=='LW':
            pac, sho, pas, dri, de, phy = 0.39, 0.10, 0.15, 0.39, 0.00, 0.00
        if position=='LM' or position=='RM':
            pac, sho, pas, dri, de, phy = 0.20, 0.20, 0.33, 0.20, 0.10, 0.00
        if position=='LWB' or position=='RWB':
            pac, sho, pas, dri, de, phy = 0.38, 0.00, 0.20, 0.10, 0.30, 0.05
        if position=='LB' or position=='RB':
            pac, sho, pas, dri, de, phy = 0.38, 0.00, 0.10, 0.20, 0.30, 0.05
        """

        if position=='ST':
            pac, sho, pas, dri, de, phy = 0.10, 0.80, 0.00, 0.03, 0.00, 0.10
        if position=='CAM' or position=='CF':
            pac, sho, pas, dri, de, phy = 0.08, 0.25, 0.40, 0.30, 0.00, 0.00
        if position=='CM':
            pac, sho, pas, dri, de, phy = 0.05, 0.05, 0.48, 0.30, 0.10, 0.05
        if position=='CDM':
            pac, sho, pas, dri, de, phy = 0.03, 0.00, 0.30, 0.10, 0.40, 0.20

        if position=='CB':
            pac, sho, pas, dri, de, phy = 0.08, 0.00, 0.00, 0.00, 0.65, 0.30

        if position=='RW' or position=='LW':
            pac, sho, pas, dri, de, phy = 0.25, 0.20, 0.23, 0.35, 0.00, 0.00
        if position=='LM' or position=='RM':
            pac, sho, pas, dri, de, phy = 0.20, 0.10, 0.33, 0.30, 0.10, 0.00
        if position=='LWB' or position=='RWB':
            pac, sho, pas, dri, de, phy = 0.38, 0.00, 0.20, 0.10, 0.30, 0.05
        if position=='LB' or position=='RB':
            pac, sho, pas, dri, de, phy = 0.38, 0.00, 0.10, 0.20, 0.30, 0.05
        
        if position is None:
            return 75
 
        rate = self.pace*pac+self.shooting*sho+self.passing*pas+self.dribbling*dri+self.defending*de+self.physicality*phy
        return np.int8(np.round(rate))
    
    def select_main_position(self):
        rate_list = []
        for pos in ALL_POSITON_LOW:
            rate_list.append(self.cal_rate(pos))
        self.main_position = ALL_POSITON_LOW[np.argmax(rate_list)]
        self.main_rate = self.cal_rate(self.main_position)
        
        if self.main_position=='RW':
            if np.random.rand()<0.5:
                self.main_position='LW'

        elif self.main_position=='RM':
            if np.random.rand()<0.5:
                self.main_position='LM'
        
        elif self.main_position=='RWB':
            if np.random.rand()<0.5:
                self.main_position='LWB'
        
        if self.main_position=='RB':
            if np.random.rand()<0.5:
                self.main_position='LB'

    def cal_all_rate(self):
        for pos in ALL_POSITON:
            self.position_all_rate[pos] = self.cal_rate(pos)
        
        self.position_all_rate["GK"] = 0
    
    def grow_up(self, game_num):
        grow_game_rate = 0.0
        grow_year_rate = 0.0

        if self.age <= self.grow_min_age:
            if self.grow_type == "general":
                grow_game_rate = 0.04
                grow_year_rate = 0.6
            elif self.grow_type == "legend":
                grow_game_rate = 0.035
                grow_year_rate = 2.0
            elif self.grow_type == "genius":
                grow_game_rate = 0.025
                grow_year_rate = 1.5
            elif self.grow_type == "grass":
                grow_game_rate = 0.007
                grow_year_rate = 0.4
        elif self.age <= self.grow_old_age_1:
            if self.grow_type == "general" or self.grow_type == "grass":
                grow_game_rate = 0.0
                grow_year_rate = 0.0
            else:
                grow_game_rate = 0.001
                grow_year_rate = 0.0
        elif self.age <= self.grow_old_age_2:
            if self.grow_type == "general" or self.grow_type == "genius" or self.grow_type == "grass":
                grow_game_rate = 0.0
                grow_year_rate = -1.0
            elif self.grow_type == "legend":
                grow_game_rate = 0.0
                grow_year_rate = -1.5
        else:
            if self.grow_type == "general" or self.grow_type == "genius" or self.grow_type == "grass":
                grow_game_rate = 0.0
                grow_year_rate = -3.0
            elif self.grow_type == "legend":
                grow_game_rate = 0.0
                grow_year_rate = -2.0

        if self.grow_position_type == "ST":
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)*0.7
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "ST_":
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.physicality_exp += game_num*grow_game_rate + grow_year_rate
        elif self.grow_position_type == "RW":
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.pace_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += game_num*grow_game_rate + grow_year_rate
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/3
        elif self.grow_position_type == "RM":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.passing_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += game_num*grow_game_rate + grow_year_rate
            self.defending_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "RB" or self.grow_position_type == "RWB":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/4
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.defending_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "CAM":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.passing_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += game_num*grow_game_rate + grow_year_rate
            self.defending_exp += (game_num*grow_game_rate + grow_year_rate)/4
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "CM":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.passing_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.defending_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
        elif self.grow_position_type == "CDM":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/3
            self.passing_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.defending_exp += game_num*grow_game_rate + grow_year_rate
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "CB":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.defending_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
        
        self.pace = min(np.int8(np.round(self.pace_initial+self.pace_exp)), 99)
        self.shooting = min(np.int8(np.round(self.shooting_initial+self.shooting_exp)), 99)
        self.passing = min(np.int8(np.round(self.passing_initial+self.passing_exp)), 99)
        self.dribbling = min(np.int8(np.round(self.dribbling_initial+self.dribbling_exp)), 99)
        self.defending = min(np.int8(np.round(self.defending_initial+self.defending_exp)), 99)
        self.physicality = min(np.int8(np.round(self.physicality_initial+self.physicality_exp)), 99)

        if self.age == self.grow_min_age:
            self.grow_exp_dict["max"] = [self.pace_exp, self.shooting_exp, self.passing_exp, self.dribbling_exp, self.defending_exp, self.physicality_exp]
        elif self.age == self.grow_old_age_2-1:
            self.grow_exp_dict["down"] = [self.pace_exp, self.shooting_exp, self.passing_exp, self.dribbling_exp, self.defending_exp, self.physicality_exp]

    def down_ability(self, value):
        self.pace -= value
        self.shooting -= value
        self.passing -= value
        self.dribbling -= value
        self.defending -= value
        self.physicality -= value

        self.pace_exp -= value
        self.shooting_exp -= value
        self.passing_exp -= value
        self.dribbling_exp -= value
        self.defending_exp -= value
        self.physicality_exp -= value
    
    def print_player_data(self):
        print(self.name, '  Rate:', self.main_rate, '(', self.main_position, ')')
        print('-'*25)
        print('  PAC ', self.pace, '  DRI ', self.dribbling)
        print('  SHO ', self.shooting, '  DEF ', self.defending)
        print('  PAS ', self.passing, '  PHY ', self.physicality)
        print()
        
        print(f"        ST:{self.cal_rate('ST')}")
        print(f" LW:{self.cal_rate('LW')} CAM,CF:{self.cal_rate('CAM')} RW:{self.cal_rate('RW')}")
        print(f" LM:{self.cal_rate('LM')}  CM:{self.cal_rate('CM')}    RM:{self.cal_rate('RM')}")
        print(f"LWB:{self.cal_rate('LWB')} CDM:{self.cal_rate('CDM')}    RWB:{self.cal_rate('RWB')}")
        print(f" LB:{self.cal_rate('LB')}  CB:{self.cal_rate('CB')}    RB:{self.cal_rate('RB')}")
        print()

class GK(FootBaller):
    def __init__(self, name, age, now_year, position, diving, 
                 handling, kicking, reflexes, 
                 speed, positioning, injury_possibility=0,
                 grow_position_type=None,
                 recovery_power=100):
        super().__init__(name, age, now_year, injury_possibility, grow_position_type, recovery_power)
        self.main_position = position
        self.diving = diving
        self.handling = handling
        self.kicking = kicking
        self.reflexes = reflexes
        self.speed = speed
        self.positioning = positioning
        self.main_rate = self.cal_rate()

        # 一般能力を15統一
        self.pace = 15
        self.shooting = 15
        self.passing = 15
        self.dribbling = 15
        self.defending = 15
        self.physicality = 15

        self.diving_initial = diving
        self.handling_initial = handling
        self.kicking_initial = kicking
        self.reflexes_initial = reflexes
        self.speed_initial = speed
        self.positioning_initial = positioning

        self.diving_exp = 0.0
        self.handling_exp = 0.0
        self.kicking_exp = 0.0
        self.reflexes_exp = 0.0
        self.speed_exp = 0.0
        self.positioning_exp = 0.0
    
    def cal_rate(self):
        div, han, kic, ref, spe, pos = 0.23, 0.23, 0.06, 0.23, 0.05, 0.23
        output = self.diving*div + self.handling*han + self.kicking*kic + self.reflexes*ref + self.speed*spe + self.positioning*pos
        return np.int8(np.round(output))
    
    def cal_all_rate(self):
        for pos in ALL_POSITON:
            self.position_all_rate[pos] = 0
        self.position_all_rate["GK"] = self.cal_rate()
    
    def grow_up(self, game_num):
        grow_game_rate = 0.0
        grow_year_rate = 0.0

        if self.age <= self.grow_min_age:
            if self.grow_type == "general":
                grow_game_rate = 0.042
                grow_year_rate = 0.5
            elif self.grow_type == "genius":
                grow_game_rate = 0.0375
                grow_year_rate = 1.0
            elif self.grow_type == "grass":
                grow_game_rate = 0.007
                grow_year_rate = 0.4
            elif self.grow_type == "legend":
                grow_game_rate = 0.033
                grow_year_rate = 2.0
        elif self.age <= self.grow_old_age_1:
            if self.grow_type == "general" or self.grow_type == "grass":
                grow_game_rate = 0.0
                grow_year_rate = 0.0
            else:
                grow_game_rate = 0.001
                grow_year_rate = 0.0
        elif self.age <= self.grow_old_age_2:
            if self.grow_type == "general" or self.grow_type == "genius" or self.grow_type == "grass":
                grow_game_rate = 0.0
                grow_year_rate = -1.0
            elif self.grow_type == "legend":
                grow_game_rate = 0.0
                grow_year_rate = -1.5
        else:
            if self.grow_type == "general" or self.grow_type == "genius" or self.grow_type == "grass":
                grow_game_rate = 0.0
                grow_year_rate = -3.0
            elif self.grow_type == "legend":
                grow_game_rate = 0.0
                grow_year_rate = -2.0
        
        self.diving_exp += game_num*grow_game_rate + grow_year_rate
        self.handling_exp += game_num*grow_game_rate + grow_year_rate
        self.kicking_exp += (game_num*grow_game_rate + grow_year_rate)/2
        self.reflexes_exp += game_num*grow_game_rate + grow_year_rate
        self.speed_exp += (game_num*grow_game_rate + grow_year_rate)/2
        self.positioning_exp += game_num*grow_game_rate + grow_year_rate

        self.diving = min(np.int8(np.round(self.diving_initial + self.diving_exp)), 99)
        self.handling = min(np.int8(np.round(self.handling_initial + self.handling_exp)), 99)
        self.kicking = min(np.int8(np.round(self.kicking_initial + self.kicking_exp)), 99)
        self.reflexes = min(np.int8(np.round(self.reflexes_initial + self.reflexes_exp)), 99)
        self.speed = min(np.int8(np.round(self.speed_initial + self.speed_exp)), 99)
        self.positioning = min(np.int8(np.round(self.positioning_initial + self.positioning_exp)), 99)
    
    def down_ability(self, value):
        self.diving -= value
        self.handling -= value
        self.kicking -= value
        self.reflexes -= value
        self.speed -= value
        self.positioning -= value

        self.diving_initial -= value
        self.handling_initial -= value
        self.kicking_initial-= value
        self.reflexes_initial -= value
        self.speed_initial -= value
        self.positioning_initial -= value

    def print_player_data(self):
        print(self.name, '  Rate:', self.main_rate, '(', self.main_position, ')')
        print('-'*25)
        print('  DIV ', self.diving, '  REF ', self.reflexes)
        print('  HAN ', self.handling, '  SPE ', self.speed)
        print('  KIC ', self.kicking, '  POS ', self.positioning)
        print()

class Formation:
    def __init__(self, name, formation, formation_priority, 
                 formation_num, formation_shooting_rate, 
                 formation_assist_rate, formation_tired_vitality):
        self.name = name
        self.formation = formation
        self.formation_priority = formation_priority
        self.formation_num = formation_num
        self.formation_shooting_rate = formation_shooting_rate
        self.formation_assist_rate = formation_assist_rate
        self.formation_tired_vitality = formation_tired_vitality
        self.formation_flat = self.__flat_formation()
        self.set_players_position()
        self.players_flat = []

        self.main_rate_formation = {}
        self.mean_rate = 0
    
    def __flat_formation(self):
        output = []
        for _, value in self.formation.items():
            output.extend(value)
        output.append("GK")
        return output
    
    def set_players_position(self):
        output = {}
        for ff in self.formation_flat:
            output[ff] = []
        output["GK"] = []
        self.players = output

    def cal_team_rate(self):
        place_list = ['ATT', 'MID', 'DEF']
        self.team_rate = {}
        sum_all_rate = 0

        for place in place_list:
            sum_rate = 0
            num = 0
            position = self.formation[place]
            for pos in position:
                pos_players = self.players[pos]
                for pp in pos_players:
                    sum_rate += pp.position_all_rate[pos]
                    sum_all_rate += pp.position_all_rate[pos]
                    num += 1
            sum_rate /= num
            self.team_rate[place] = sum_rate
        
        self.team_rate["GK"] = self.players["GK"][0].main_rate
        
        sum_all_rate += self.players["GK"][0].main_rate
        self.team_rate["ALL"] = sum_all_rate/11
    
    def print_formation(self):
        for pos in self.formation_flat:
            player = self.players[pos]
            if pos == "GK":
                player = player[0]
                print(player.name, '  Rate:', player.main_rate, '(', player.main_position, ')')
                print('-'*25)
                print('  DIV ', player.diving, '  REF ', player.reflexes)
                print('  HAN ', player.handling, '  SPE ', player.speed)
                print('  KIC ', player.kicking, '  POS ', player.positioning)
                print()
            else:
                for player_ in player:
                    print(player_.name, '  Rate:', player_.position_all_rate[player_.partification_position], '(', player_.partification_position, ')')
                    print('-'*25)
                    print('  PAC ', player_.pace, '  DRI ', player_.dribbling)
                    print('  SHO ', player_.shooting, '  DEF ', player_.defending)
                    print('  PAS ', player_.passing, '  PHY ', player_.physicality)
                    print()
    
    def print_formation_(self):
        for pos in self.formation_flat:
            player = self.main_rate_formation[pos]
            if len(player) < 1:
                print('配置なし  Rate:' '(', pos, ')')

            if pos == "GK":
                player = player[0]
                print(player.name, '  Rate:', player.main_rate, '(', player.main_position, ')')
            else:
                for player_ in player:
                    print(player_.name, '  Rate:', player_.position_all_rate[pos], '(', pos, ')')

class Team:
    def __init__(self, name, formation, member_num=30):
        self.name = name
        self.formation = formation
        self.result = pd.DataFrame(columns=['win', 'lose', 'row', '得点', '失点', '得失点差', 'Points', '順位', 'リーグ名'])
        self.competition_result = {}
        self.affilation_players = None
        self.register_players = None
        self.not_register_players = None
        self.league_name = None
        self.member_num = member_num

        self.rank_point = 0
        self.rank_point_list = []

        self.empty_position = {}
        self.formation_rate = {}

        # 昇格降格変数
        self.relegation = 0
        self.promotion = 0

    def set_register_players(self):
        for p in self.affilation_players:
            p.register = 0
        
        for key, players in self.formation.main_rate_formation.items():
            for p in players:
                p.register = 1

        for pos, num in BENCH_POSITION_NUM.items():
            not_register = [p for p in self.affilation_players if p.register==0]
            not_register = sorted(not_register, key=lambda x:x.position_all_rate[pos], reverse=True)
            for p in not_register[:num]:
                p.register = 1
        
        self.not_register_players = [p for p in self.affilation_players if p.register==0]
        self.register_players = [p for p in self.affilation_players if p.register==1]
    
    def set_onfield_players(self):
        self.formation.set_players_position()
        self.formation.players_flat = []
        self.formation.main_rate_formation = {}

        for pos in self.formation.formation_flat:
            self.formation.main_rate_formation[pos] = []
        
        for p in self.affilation_players:
            p.index = 0
            p.partification = 0
            p.startup = 0
            p.position_all_rate_sorted = sorted(p.position_all_rate.items(), key=lambda x:x[1], reverse=True)
        
        remain_players = [p for p in self.register_players if p.injury<1 and p.vitality>=60]
        #if len(remain_players)<18:
         #   print(len(remain_players), self.name)
        count = 0

        while True:
            if count>5 and len([p for ps in list(self.formation.main_rate_formation.values()) for p in ps])==11:
                break

            if count>10:
                raise Exception(f'{self.name}はチームを作成できません')

            for p in remain_players:
                for index in range(p.index, len(p.position_all_rate_sorted)):
                    pos = p.position_all_rate_sorted[index][0]
                    if pos in self.formation.formation_flat:
                        self.formation.main_rate_formation[pos].append(p)
                        p.index = index+1
                        break
            
            remain_players = []
            for pos in self.formation.formation_flat:
                if len(self.formation.main_rate_formation[pos])<1:
                    continue
                buff_players = self.formation.main_rate_formation[pos]
                self.formation.main_rate_formation[pos] = sorted(self.formation.main_rate_formation[pos], key=lambda x:x.position_all_rate[pos], reverse=True)[:self.formation.formation_num[pos]]
                remain_players.extend([p for p in buff_players if p not in self.formation.main_rate_formation[pos]])
            count += 1
        
        for pos, players in self.formation.main_rate_formation.items():
            for p in players:
                p.partification = 1
                p.startup = 1
                p.partification_position = pos
                self.formation.players[pos].append(p)
        
        for fps in self.formation.players.values():
            self.formation.players_flat.extend(fps)
    
    # 現状の最強スカッドを作成する
    def set_main_rate_position(self):
        self.formation.main_rate_formation = {}
        for pos in self.formation.formation_flat:
            self.formation.main_rate_formation[pos] = []
        
        for p in self.affilation_players:
            p.index = 0
            p.position_all_rate_sorted = sorted(p.position_all_rate.items(), key=lambda x:x[1], reverse=True)
        
        remain_players = self.affilation_players
        count = 0

        while True:
            if count>5:
                break

            for p in remain_players:
                for index in range(p.index, len(p.position_all_rate_sorted)):
                    pos = p.position_all_rate_sorted[index][0]
                    if pos in self.formation.formation_flat:
                        self.formation.main_rate_formation[pos].append(p)
                        p.index = index+1
                        break
            
            remain_players = []
            for pos in self.formation.formation_flat:
                if len(self.formation.main_rate_formation[pos])<1:
                    continue
                buff_players = self.formation.main_rate_formation[pos]
                self.formation.main_rate_formation[pos] = sorted(self.formation.main_rate_formation[pos], key=lambda x:x.position_all_rate[pos], reverse=True)[:self.formation.formation_num[pos]]
                remain_players.extend([p for p in buff_players if p not in self.formation.main_rate_formation[pos]])
            count += 1
        
        rate_sum = 0
        num = 0

        for pos, value in self.formation.main_rate_formation.items():
            for p in value:
                rate_sum+=p.position_all_rate[pos]
                num += 1

        if num>0:
            self.formation.mean_rate = rate_sum/num
        else:
            self.formation.mean_rate = 0
    
    # スタメンの弱いpositionを見つける
    def set_empty_position(self, league_rate):
        self.empty_position = {}

        if self.formation.mean_rate < league_rate:
            identify_rate = league_rate
        else:
            identify_rate = (self.formation.mean_rate+league_rate)/2
        
        for pos, value in self.formation.main_rate_formation.items():
            for p in value:
                if p.position_all_rate[pos]<identify_rate:
                    if pos in self.empty_position.keys():
                        self.empty_position[pos] += 1
                    else:
                        self.empty_position[pos] = 1
        
        gk_num = len([p for p in self.affilation_players if p.main_position=="GK"])
        if gk_num>3:
            self.empty_position["GK"] = 0
    
    # ランダムなポジションを補強する
    def set_empty_position_random(self, num, none_gk=False):
        self.empty_position = {}
        gk_num = len([p for p in self.affilation_players if p.main_position=="GK"])

        if none_gk==True and gk_num<3:
            self.empty_position["GK"] = 3-gk_num
            gk_num_ = 3-gk_num
            if num<gk_num_:
                num = gk_num_
        else:
            gk_num_ = 0

        if gk_num<4:
            randon_position = random.choices(ALL_POSITON_LOW_GK, k=num-gk_num_)
        else:
            randon_position = random.choices(ALL_POSITON_LOW, k=num-gk_num_)

        for pos in randon_position:
            if pos in self.empty_position.keys():
                self.empty_position[pos] += 1
            else:
                self.empty_position[pos] = 1
    
    # empety_positionに沿った選手を移籍市場から獲得する
    def get_free_players(self, free_players, league):
        for pos in self.empty_position.keys():
            num = self.empty_position[pos]
            new_players = [p for p in free_players if p.main_position in POSITION_LOW_DICT[pos] and p.main_rate>=league.min_rate and p.main_rate<=league.max_rate]
            new_players = sorted(new_players, key=lambda x:x.main_rate, reverse=True)
            if len(new_players) >= num:
                new_players = new_players[:num]
            for p in new_players:
                p.set_contract()
            
            self.affilation_players.extend(new_players)
            free_players = [p for p in free_players if p not in new_players]
        return free_players
    
    def set_register_players_(self):
        for p in self.affilation_players:
            p.register = 0
        
        for key, players in self.formation.main_rate_formation.items():
            for p in players:
                p.register = 1

        for pos, num in BENCH_POSITION_NUM.items():
            not_register = [p for p in self.affilation_players if p.register==0]
            not_register = sorted(not_register, key=lambda x:x.position_all_rate[pos], reverse=True)
            for p in not_register[:num]:
                p.register = 1
        
        #self.not_register_players = [p for p in self.affilation_players if p.register==0]
        #self.register_players = [p for p in self.affilation_players if p.register==1]

class Game:
    def __init__(self, home, away, competition_name=None, 
                 mid_rate=0.5, gk_rate=0.2, random_std=0.3, 
                 moment_num=10, extra=0, pk=0):
        self.home = home
        self.away = away
        self.mid_rate = mid_rate
        self.gk_rate = gk_rate
        self.random_std = random_std
        self.moment_num = moment_num
        self.competition_name = competition_name

        self.home_goal = 0
        self.away_goal = 0
        self.home_pk_goal = 0
        self.away_pk_goal = 0
        self.home_replacement = 0
        self.away_replacement = 0
        self.now_time = 0
        self.result = None
        self.pk = pk
        self.extra = extra
    
    # 誰が得点者でアシストしたか
    def cal_goal_assit_player(self, side):
        # goal
        a = np.array([s.shooting for s in side.formation.players_flat])
        a = np.maximum(a-np.max(a)/2, 10)
        b = np.array(side.formation.formation_shooting_rate)
        weights = a*b/sum(a*b)
        goal_player = np.random.choice(side.formation.players_flat, 1, p=weights)[0]
        goal_player.get_goal(self.competition_name)
        
        # asssit
        if np.random.rand()>0.4:
            a = np.array([s.passing for s in side.formation.players_flat])
            a = np.maximum(a-np.max(a)/2, 5)
            b = np.array(side.formation.formation_assist_rate)
            weights = a*b/sum(a*b)
            while True:
                assist_player = np.random.choice(side.formation.players_flat, 1, p=weights)[0]
                if assist_player!=goal_player:
                    break
            assist_player.get_assist(self.competition_name)
    
    # 途中交代
    def change_player(self):
        if self.home_replacement<REPLACEMENT_MAX:
            tired_player = [p for p in self.home.formation.players_flat if p.vitality<30]
            change_num = min(len(tired_player), REPLACEMENT_MAX-self.home_replacement)
            if change_num>0:
                change_player = tired_player[:change_num]
                for c_p in change_player:
                    pos = c_p.partification_position
                    bench_player = [p for p in self.home.register_players if p.partification==0 and p.injury<1 and p.vitality>=30]
                    if len(bench_player)<1:
                        break
                    new_player = sorted(bench_player, key=lambda x:x.position_all_rate[pos], reverse=True)[0]
                    new_player.partification_position = pos
                    new_player.partification = 1
                    new_player.get_game_count(self.competition_name)
                    new_player.get_position(self.competition_name, pos)
                    self.home.formation.players[pos].append(new_player)
                    self.home.formation.players[pos].remove(c_p)
                    self.home.formation.players_flat = []
                    for fps in self.home.formation.players.values():
                        self.home.formation.players_flat.extend(fps)
                    self.home.formation.cal_team_rate()
                    self.home_replacement += 1

        if self.away_replacement<REPLACEMENT_MAX:
            tired_player = [p for p in self.away.formation.players_flat if p.vitality<30]
            change_num = min(len(tired_player), REPLACEMENT_MAX-self.away_replacement)
            change_player = tired_player[:change_num]
            if change_num>0:
                for c_p in change_player:
                    pos = c_p.partification_position
                    bench_player = [p for p in self.away.register_players if p.partification==0 and p.injury<1 and p.vitality>=30]
                    if len(bench_player)<1:
                        break
                    new_player = sorted(bench_player, key=lambda x:x.position_all_rate[pos], reverse=True)[0]
                    new_player.partification_position = pos
                    new_player.partification = 1
                    new_player.get_game_count(self.competition_name)
                    new_player.get_position(self.competition_name, pos)
                    self.away.formation.players[pos].append(new_player)
                    self.away.formation.players[pos].remove(c_p)
                    self.away.formation.players_flat = []
                    for fps in self.away.formation.players.values():
                        self.away.formation.players_flat.extend(fps)
                    self.away.formation.cal_team_rate()
                    self.away_replacement += 1
    
    def moment_battle(self):
        home_rate = self.home.formation.team_rate
        away_rate = self.away.formation.team_rate

        home_ratio = home_rate['ALL']/(home_rate['ALL']+away_rate['ALL'])
        away_ratio = away_rate['ALL']/(home_rate['ALL']+away_rate['ALL'])
        
        home_attack = ((home_rate['ATT']+home_rate['MID']*self.mid_rate)*home_ratio)/100
        away_attack = ((away_rate['ATT']+away_rate['MID']*self.mid_rate)*away_ratio)/100
        
        home_defence = ((home_rate['DEF']+home_rate['MID']*self.mid_rate)*home_ratio+home_rate["GK"]*self.gk_rate)/100
        away_defence = ((away_rate['DEF']+away_rate['MID']*self.mid_rate)*away_ratio+away_rate["GK"]*self.gk_rate)/100
        
        if home_attack-away_defence+np.random.normal(-0.3, self.random_std) > 0:
            self.home_goal += 1
            self.cal_goal_assit_player(self.home)
        
        if away_attack-home_defence+np.random.normal(-0.3, self.random_std) > 0:
            self.away_goal += 1
            self.cal_goal_assit_player(self.away)
        
        for p in self.home.formation.players_flat:
            p.vitality -= self.home.formation.formation_tired_vitality[p.partification_position]/self.moment_num
            p.get_game_time(self.competition_name, 90/self.moment_num)
        
        for p in self.away.formation.players_flat:
            p.vitality -= self.away.formation.formation_tired_vitality[p.partification_position]/self.moment_num
            p.get_game_time(self.competition_name, 90/self.moment_num)
        
        if self.now_time<self.moment_num:
            self.change_player()

    def battle(self):
        self.home_goal = 0
        self.away_goal = 0

        all_time = 90

        # 試合数・ポジションカウント
        for p in self.home.formation.players_flat:
            p.get_game_count(self.competition_name)
            p.get_position(self.competition_name, p.partification_position)
        
        for p in self.away.formation.players_flat:
            p.get_game_count(self.competition_name)
            p.get_position(self.competition_name, p.partification_position)

        # 90分間試合
        for i in range(self.moment_num):
            self.now_time+=1
            self.moment_battle()
        
        if self.home_goal>self.away_goal:
            self.result="home"
        elif self.home_goal<self.away_goal:
            self.result="away"
        elif self.extra==1 or self.pk==1:
            #延長戦
            if self.extra==1:
                all_time = 120
                for i in range(int(self.moment_num/3)):
                    self.moment_battle()
            
            if self.home_goal>self.away_goal:
                self.result="home"
            elif self.home_goal<self.away_goal:
                self.result="away"
            else:
                #PK戦
                home_pk_players = sorted(self.home.formation.players_flat, key=lambda x:x.shooting, reverse=True)
                away_pk_players = sorted(self.away.formation.players_flat, key=lambda x:x.shooting, reverse=True)

                home_gk = self.home.formation.players["GK"][0]
                away_gk = self.away.formation.players["GK"][0]

                self.home_pk_goal = 0
                self.away_pk_goal = 0

                for i in range(5):
                    if home_pk_players[i].shooting - away_gk.main_rate + np.random.normal(30, 10) > 0:
                        self.home_pk_goal += 1
                    if away_pk_players[i].shooting - home_gk.main_rate + np.random.normal(30, 10) > 0:
                        self.away_pk_goal += 1
                
                if self.home_pk_goal > self.away_pk_goal:
                    self.result = "home-pk"
                elif self.home_pk_goal < self.away_pk_goal:
                    self.result = "away-pk"
                else:
                    i = 0
                    while True:
                        if home_pk_players[(i+5)%10].shooting - away_gk.main_rate + np.random.normal(30, 10) > 0:
                            self.home_pk_goal += 1
                        if away_pk_players[(i+5)%10].shooting - home_gk.main_rate + np.random.normal(30, 10) > 0:
                            self.away_pk_goal += 1
                        
                        if self.home_pk_goal > self.away_pk_goal:
                            self.result = "home-pk"
                            break
                        elif self.home_pk_goal < self.away_pk_goal:
                            self.result = "away-pk"
                            break
                        
                        i+=1
        else:
            self.result = "row"
        
        # クリーンシート
        if self.away_goal == 0:
            for p in self.home.formation.players_flat:
                if p.startup==1:
                    p.get_cs(self.competition_name)
        if self.home_goal == 0:
            for p in self.away.formation.players_flat:
                if p.startup==1:
                    p.get_cs(self.competition_name)
        
        # 怪我 F分布で表現
        for p in [p for p in self.home.register_players if p.partification==1]:
            if p.injury_possibility>np.random.rand():
                p.injury=min(max(np.int8(np.round(np.random.f(100, 5)*5)), 1), 40)
                p.get_injury(self.competition_name)
                if p.injury > 20:
                    p.down_ability(3)
                    if p.injury > 30 and p.age > p.grow_old_age_1 and np.random.rand()<0.5:
                        p.retire = 1
        
        for p in [p for p in self.away.register_players if p.partification==1]:
            if p.injury_possibility>np.random.rand():
                p.injury=min(max(np.int8(np.round(np.random.f(100, 5)*5)), 1), 40)
                p.get_injury(self.competition_name)
                if p.injury > 20:
                    p.down_ability(3)
                    if p.injury > 30 and p.age > p.grow_old_age_1 and np.random.rand()<0.5:
                        p.retire = 1

        min_rate, max_rate=cal_game_rating_rate(self.home)
        if self.result=="home":
            easy_result = 1
        elif self.result=="away":
            easy_result = -1
        else:
            easy_result = 0
        for p in self.home.register_players:
            p.recovery_vitality()
            if p.partification==1:
                p.cal_rating(self.competition_name, min_rate, max_rate, self.away_goal, easy_result, all_time)
        
        min_rate, max_rate=cal_game_rating_rate(self.away)
        if self.result=="home":
            easy_result = -1
        elif self.result=="away":
            easy_result = 1
        else:
            easy_result = 0
        for p in self.away.register_players:
            p.recovery_vitality()
            if p.partification==1:
                p.cal_rating(self.competition_name, min_rate, max_rate, self.home_goal, easy_result, all_time)

        all_game_player = self.home.register_players.copy()
        all_game_player.extend(self.away.register_players)
        p = max(all_game_player ,key=lambda x:x.today_rating)
        p.get_man_of_the_match(self.competition_name)

class League:
    def __init__(self, name, teams, num, category, league_level, relegation_num=0, promotion_num=0, min_rate=75, max_rate=85, mean_rate=80, standard_rate=78):
        self.name = name
        self.teams = teams
        self.num = num
        self.category = category
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.mean_rate = mean_rate
        self.standard_rate = standard_rate
        self.league_level = league_level

        self.team_result = {}
        self.player_result = {}
        self.champion = pd.DataFrame(columns=["優勝", "得点王", "MVP", "yMVP", "ベストGK"])
        
        self.relegation = {}
        self.relegation_num = relegation_num
        self.promotion = {}
        self.promotion_num = promotion_num

        self.set_team_leaguename()
    
    def set_team_leaguename(self):
        for t in self.teams:
            t.league_name = self.name
    
    def set_player_result(self, competition_name, year, kind):
        for t in self.teams:
            for p in t.affilation_players:
                p.result[competition_name] = {}
                p.result[competition_name]["goal"] = 0
                p.result[competition_name]["assist"] = 0
                p.result[competition_name]["CS"] = 0
                p.result[competition_name]["試合数"] = 0
                p.result[competition_name]["年度"] = year
                p.result[competition_name]["分類"] = kind
                p.result[competition_name]["年齢"] = p.age
                p.result[competition_name]["怪我欠場"] = 0
                p.result[competition_name]["怪我回数"] = 0
                p.result[competition_name]["出場時間"] = 0
                p.result[competition_name]["合計評価点"] = 0
                p.result[competition_name]["MOM"] = 0
                p.result[competition_name]["ポジション"] = {}
                p.result[competition_name]["ポジション"][p.main_position] = 0
                p.recovery_vitality(off=True)
    
    def set_team_result(self, season_name):
        all_team_name = [s.name for s in self.teams]
        output = pd.DataFrame(np.zeros((len(all_team_name), 5)), 
                              index=all_team_name, 
                              columns=["win", "lose", "row", "得点", "失点"], 
                              dtype=np.int8)
        self.team_result[season_name] = output
    
    def cal_1year_result(self, year):
        season_name = f'{self.name}_{year}'
        
        self.team_result[season_name]["得失点差"] = self.team_result[season_name]["得点"]-self.team_result[season_name]["失点"]
        self.team_result[season_name]["Points"] = self.team_result[season_name].apply(apply_points, axis=1)
        self.team_result[season_name] = self.team_result[season_name].sort_values("Points", ascending=False)
        self.team_result[season_name]["順位"] = [i for i in range(1, 21)]
        self.team_result[season_name]["リーグ名"] = [f"{self.name}" for i in range(20)]
        
        for team in self.teams:
            team.result.loc[season_name] = self.team_result[season_name].loc[team.name, :]
            team.rank_point += int(self.team_result[season_name].loc[team.name, "順位"]+(self.league_level-1)*20)
            team.rank_point_list.append(team.rank_point)
        
        self.champion.loc[season_name, "優勝"] = list(self.team_result[season_name].index)[0]
        
        # 昇格決定
        if self.category!="top":
            self.promotion[season_name] = list(self.team_result[season_name][:self.promotion_num].index)
        
        #降格決定
        if self.category!="lowest":
            self.relegation[season_name] = list(self.team_result[season_name][-self.relegation_num:].index)
        
    def play_1section(self, year, sections):
        season_name = f'{self.name}_{year}'
        
        for section in sections:
            # 必要変数をセッティング
            for p in self.teams[section[0]-1].register_players:
                p.set_game_variable()
            for p in self.teams[section[1]-1].register_players:
                p.set_game_variable()

            # スターティングメンバーを作る
            self.teams[section[0]-1].set_onfield_players()
            self.teams[section[0]-1].formation.cal_team_rate()
            self.teams[section[1]-1].set_onfield_players()
            self.teams[section[1]-1].formation.cal_team_rate()
            
            game = Game(home=self.teams[section[0]-1], 
                        away=self.teams[section[1]-1],
                        competition_name=season_name,
                        moment_num=24,
                        random_std=0.3)
            game.battle()

            home_team_name = self.teams[section[0]-1].name
            away_team_name = self.teams[section[1]-1].name

            if game.result=="home":
                self.team_result[season_name].loc[home_team_name, "win"] += 1
                self.team_result[season_name].loc[away_team_name, "lose"] += 1
            elif game.result=="away":
                self.team_result[season_name].loc[away_team_name, "win"] += 1
                self.team_result[season_name].loc[home_team_name, "lose"] += 1
            else:
                self.team_result[season_name].loc[home_team_name, "row"] += 1
                self.team_result[season_name].loc[away_team_name, "row"] += 1

            self.team_result[season_name].loc[home_team_name, "得点"] += game.home_goal
            self.team_result[season_name].loc[home_team_name, "失点"] += game.away_goal

            self.team_result[season_name].loc[away_team_name, "得点"] += game.away_goal
            self.team_result[season_name].loc[away_team_name, "失点"] += game.home_goal

            # 怪我を一つ進める
            for p in self.teams[section[0]-1].register_players:
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(season_name)
            for p in self.teams[section[1]-1].register_players:
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(season_name)

class Competition:
    def __init__(self, name):
        self.name = name
        self.now_round = 1
        self.section_interval = 0
        self.max_round = None
    
    def set_max_round(self, num_teams, num_section):
        for max_round in range(N):
            if num_teams < pow(2, max_round):
                break
        self.max_round = max_round
        self.section_interval = num_section//self.max_round

class CountryLeague:
    def __init__(self, name, leagues, competition_name=None):
        self.name = name
        self.leagues = leagues

        self.players_result = pd.DataFrame()

        self.competition = None
        self.competition_name = competition_name
        self.competition_teams = None
        self.competition_result = {}
        self.competition_result_top = pd.DataFrame(columns=["年度", "優勝", "準優勝"])
    
    def set_competition(self, competition_name, year, num_section):
        self.competition_teams=[]

        for l in self.leagues:
            self.competition_teams.extend(l.teams)
            l.set_player_result(competition_name, year, "カップ戦")
        
        self.competition.set_max_round(len(self.competition_teams), num_section)
        random.shuffle(self.competition_teams)
        output = pd.DataFrame(columns=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
        self.competition_result[competition_name] = output
    
    def set_players_partification(self):
        for l in self.leagues:
            for t in l.teams:
                for p in t.affilation_players:
                    p.today_playing_time = 0
                    p.partification = 0
                    p.partification_position = None
    
    def cal_players_result(self, year):
        all_output = pd.DataFrame()
        for l in self.leagues:
            season_name = f'{l.name}_{year}'
            league_rank = l.team_result[season_name].index.tolist()
            for t in l.teams:
                t.formation_rate[season_name] = t.formation.team_rate
                season_result = [p.result[season_name] for p in t.register_players]
                competition_result = [p.result[self.competition.name] for p in t.register_players]

                output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                        "uuid":[p.uuid for p in t.register_players],
                                        "年齢":[result["年齢"] for result in season_result],
                                        "Rate" : [p.main_rate for p in t.register_players],
                                        "残契約":[p.contract-1 for p in t.register_players],
                                        "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in season_result],
                                        "国":[self.name for i in range(len(t.register_players))],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in season_result],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":[p.origin_team_name for p in t.register_players],
                                        "分類":[result["分類"] for result in season_result],
                                        "順位" :  [f"{league_rank.index(t.name)+1}位" for i in range(len(t.register_players))],
                                        "試合数":[result["試合数"] for result in season_result],
                                        "出場時間":[result["出場時間"] for result in season_result],
                                        "goal":[result["goal"] for result in season_result],
                                        "assist":[result["assist"] for result in season_result],
                                        "CS":[result["CS"] for result in season_result],
                                        "評価点":[result["合計評価点"]/result["試合数"] if result["試合数"]>0 else 0 for result in season_result],
                                        "MOM":[result["MOM"] for result in season_result],
                                        "怪我欠場":[result["怪我欠場"] for result in season_result],
                                        "怪我回数":[result["怪我回数"] for result in season_result],
                                        "賞":["" for i in range(len(t.register_players))],
                                        "全ポジション回数":[json.dumps(result["ポジション"]) for result in season_result],})
                all_output = pd.concat([all_output, output])

                output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                        "uuid":[p.uuid for p in t.register_players],
                                        "年齢":[result["年齢"] for result in competition_result],
                                        "Rate" : [p.main_rate for p in t.register_players],
                                        "残契約":[p.contract-1 for p in t.register_players],
                                        "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in competition_result],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in competition_result],
                                        "国":[self.name for i in range(len(t.register_players))],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":[p.origin_team_name for p in t.register_players],
                                        "分類":[result["分類"] for result in competition_result],
                                        "順位" :  [f"{league_rank.index(t.name)+1}位" for i in range(len(t.register_players))],
                                        "試合数":[result["試合数"] for result in competition_result],
                                        "出場時間":[result["出場時間"] for result in competition_result],
                                        "goal":[result["goal"] for result in competition_result],
                                        "assist":[result["assist"] for result in competition_result],
                                        "CS":[result["CS"] for result in competition_result],
                                        "評価点":[result["合計評価点"]/result["試合数"] if result["試合数"]>0 else 0 for result in competition_result],
                                        "MOM":[result["MOM"] for result in competition_result],
                                        "怪我欠場":[result["怪我欠場"] for result in competition_result],
                                        "怪我回数":[result["怪我回数"] for result in competition_result],
                                        "賞":["" for i in range(len(t.register_players))],
                                        "全ポジション回数":[json.dumps(result["ポジション"]) for result in competition_result],})
                all_output = pd.concat([all_output, output])

                for p in t.register_players:
                    season_result = p.result[season_name]
                    competition_result = p.result[self.competition.name]
                    p.contract -= 1

                    # 再契約する処理
                    if p.contract == 0 and p.partification_position is not None and p.rental!=1:
                        if np.random.rand()<0.3:
                            p.set_contract()
                    
                    # 試合に出てない人を戦力外にする処理
                    if p.partification_position is None and p.main_position!="GK" and p.rental!=1:
                        p.contract = 0
                    
                    # 成長
                    #p.grow_up((season_result["出場時間"]+competition_result["出場時間"])/90)
                    p.grow_up((season_result["試合数"]+competition_result["試合数"]))
                    if p.main_position != "GK":
                        p.select_main_position()
                    else:
                        p.main_rate = p.cal_rate()
                    p.cal_all_rate()

                    # offseason分怪我を経過させる
                    p.injury = max(p.injury-10, 0)

                    # 引退
                    p.consider_retirement()

            #リーグ最多得点
            all_output = all_output.reset_index(drop=True)
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name))]
            df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
            l.champion.loc[season_name, "得点王"] = ""
            for index in df_search_index:
                all_output.loc[index, "賞"] += f"得点王({season_name}),"
                l.champion.loc[season_name, "得点王"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            l.champion.loc[season_name, "得点王"] += f"  /  {df_search.loc[index, 'goal']}点"

            #リーグMVP
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.7))]
            df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
            l.champion.loc[season_name, "MVP"] = ""
            for index in df_search_index[:1]:
                all_output.loc[index, "賞"] += f"MVP({season_name}),"
                l.champion.loc[season_name, "MVP"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            
            #若手MVP
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.5)&(all_output["年齢"]<24))]
            df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
            l.champion.loc[season_name, "yMVP"] = ""
            for index in df_search_index[:1]:
                all_output.loc[index, "賞"] += f"yMVP({season_name}),"
                l.champion.loc[season_name, "yMVP"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            
            #リーグMVP
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.7))]
            df_search = df_search[df_search["ポジション"]=="GK"]
            df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
            l.champion.loc[season_name, "ベストGK"] = ""
            for index in df_search_index[:1]:
                all_output.loc[index, "賞"] += f"ベストGK({season_name}),"
                l.champion.loc[season_name, "ベストGK"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
        
        # コンペティション最多得点
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[(all_output["分類"]=="カップ戦")]
        df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
        self.competition_result_top.loc[self.competition.name, "得点王"] = ""
        for index in df_search_index:
            all_output.loc[index, "賞"] += f"得点王({self.competition.name}),"
            self.competition_result_top.loc[self.competition.name, "得点王"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}({df_search.loc[index, 'リーグ']})), "  
        self.competition_result_top.loc[self.competition.name, "得点王"] += f"/  {df_search.loc[index, 'goal']}点"

        self.players_result = pd.concat([self.players_result, all_output])
        self.players_result = self.players_result.reset_index(drop=True)

    def set_register_member(self):
        for l in self.leagues:
            for t in l.teams:
                t.set_main_rate_position()
                t.set_register_players()

    def play_holiday(self):
        for l in self.leagues:
            for t in l.teams:
                for p in t.register_players:
                    p.recovery_vitality(off=True)
    
    def prepare_1season(self, year):
        league_calender = create_calender()
        num_section = len(league_calender)
        self.competition = Competition(name=f"{self.competition_name}_{year}")
        self.set_competition(self.competition.name, year, num_section)
        self.set_players_partification()
        self.set_register_member()
        
        # 必要変数をセッティング
        for l in self.leagues:
            l.set_team_leaguename()
            season_name = f'{l.name}_{year}'
            l.set_player_result(season_name, year, "リーグ")
            l.set_team_result(season_name)
                    
    def play_1competition_section(self, year):
        buff_teams = self.competition_teams.copy()
        if self.competition.now_round==1:
            self.competition_teams = self.competition_teams[:(len(self.competition_teams)-pow(2, self.competition.max_round-1))*2]

        for i in range(0, len(self.competition_teams), 2):
            game_team = self.competition_teams[i:i+2]
            if len(game_team) < 2:
                continue

            # 怪我を一つ進める
            for p in game_team[0].register_players:
                p.set_game_variable()
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(self.competition.name)
            for p in game_team[1].register_players:
                p.set_game_variable()
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(self.competition.name)
            
            # スターティングメンバーを作る
            game_team[0].set_onfield_players()
            game_team[0].formation.cal_team_rate()
            game_team[1].set_onfield_players()
            game_team[1].formation.cal_team_rate()

            cup_game = Game(home=game_team[0], 
                            away=game_team[1], 
                            competition_name=self.competition.name,
                            moment_num=24,
                            random_std=0.3,
                            pk=1)
            cup_game.battle()
            if cup_game.result=="home" or cup_game.result=="home-pk":
                win = game_team[0]
                lose = game_team[1]
            else:
                win = game_team[1]
                lose = game_team[0]

            if self.competition.max_round-3 >= self.competition.now_round:
                round_name = f"{self.competition.now_round}回戦"
                result_name = f"{self.competition.now_round}回戦"
            elif self.competition.max_round-2 == self.competition.now_round:
                round_name = f"準々決勝"
                result_name = f"ベスト8"
            elif self.competition.max_round-1 == self.competition.now_round:
                round_name = f"準決勝"
                result_name = f"ベスト4"
            elif self.competition.max_round == self.competition.now_round:
                round_name = f"決勝"
                result_name = f"準優勝"

            if "pk" in cup_game.result:
                score = f"{cup_game.home_goal}-{cup_game.away_goal}(pk:{cup_game.home_pk_goal}-{cup_game.away_pk_goal})"
            else:
                score = f"{cup_game.home_goal}-{cup_game.away_goal}"

            output = pd.Series([f"{game_team[0].name}({game_team[0].league_name})", 
                                f"{game_team[1].name}({game_team[1].league_name})",
                                win.name, score, round_name], 
                               index=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
            self.competition_result[self.competition.name].loc[f"{game_team[0].name}-{game_team[1].name}"] = output
            lose.competition_result[self.competition.name] = result_name
            buff_teams.remove(lose)
        self.competition.now_round += 1
        self.competition_teams = buff_teams
        if len(self.competition_teams)<2:
            win.competition_result[self.competition.name] = "優勝"
            self.competition_result_top.loc[self.competition.name, ["年度", "優勝", "準優勝"]] = [year, f"{win.name}({win.league_name})", f"{lose.name}({lose.league_name})"]

class World_soccer:
    def __init__(self, country_leagues):
        self.country_leagues = country_leagues

        self.players_result = pd.DataFrame()

        self.free_players = []
        self.retire_players = []
    
    def play_1season(self, year):
        # 全リーグ同じチーム数の時、変える必要がある
        league_calender = create_calender()
        num_section = len(league_calender)

        # 全カントリーリーグの準備
        for c in self.country_leagues:
            c.prepare_1season(year)

        for day in tqdm(range(num_section)):
            for c in self.country_leagues:
                if day==int(c.competition.section_interval*c.competition.now_round):
                    c.play_1competition_section(year)
                sections = league_calender.iloc[day, :]
                for l in c.leagues:
                    l.play_1section(year, sections)
                
                if day%5==0:
                    c.play_holiday()
        
        # リーグ成績の計算
        for c in self.country_leagues:
            for l in c.leagues:
                l.cal_1year_result(year)
        
        # アンダーの練習
        for c in self.country_leagues:
            output = pd.DataFrame({"名前":[p.name for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "uuid":[p.uuid for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "年齢":[p.age for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "Rate" : [p.main_rate for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "残契約":[p.contract-1 for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "ポジション":[p.main_position for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "リーグ":["Under League" for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "年度":[year for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "国":[c.name for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "チーム":[f"{t.name}_B" for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "レンタル元":["" for l in c.leagues for t in l.teams for p in t.not_register_players],
                                    "分類":["Bチーム" for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "順位" :  [f"記録なし" for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "試合数":[30 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "出場時間":[1800 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "goal":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "assist":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "CS":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "評価点":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "MOM":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "怪我欠場":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "怪我回数":[0 for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "賞":["" for l in c.leagues for t in l.teams  for p in t.not_register_players],
                                    "全ポジション回数":["" for l in c.leagues for t in l.teams  for p in t.not_register_players],})
            
            c.players_result = pd.concat([c.players_result, output])
            c.players_result = c.players_result.reset_index(drop=True)

            for l in c.leagues:
                for t in l.teams:
                    for p in t.not_register_players:
                        p.contract -= 1
                        p.b_team_count += 1
                        p.grow_up(20)

                        if p.main_position != "GK":
                            p.select_main_position()
                        else:
                            p.main_rate = p.cal_rate()
                        
                        # 登録メンバー外の成長が止まった選手は戦力外
                        if (p.age>p.grow_min_age or p.b_team_count>2) and p.rental==0:
                            p.contract=0

                        p.cal_all_rate()
                        p.consider_retirement()
                        p.injury = 0
        
        # 選手の成績の計算
        for c in self.country_leagues:
            c.cal_players_result(year)

        # 昇格降格
        for c in self.country_leagues:
            for index in range(len(c.leagues)):
                season_name = f"{c.leagues[index].name}_{year}"
                if c.leagues[index].category!="top":
                    promotion = c.leagues[index].promotion[season_name]
                    promotion_team = [t for t in c.leagues[index].teams if t.name in promotion]
                    c.leagues[index].teams = [s for s in c.leagues[index].teams if s not in promotion_team]
                    c.leagues[index-1].teams.extend(promotion_team)

                if c.leagues[index].category!="lowest":
                    relegation = c.leagues[index].relegation[season_name]
                    relegation_team = [t for t in c.leagues[index].teams if t.name in relegation]
                    c.leagues[index].teams = [s for s in c.leagues[index].teams if s not in relegation_team]
                    c.leagues[index+1].teams.extend(relegation_team)
    
    def play_offseason(self, df_name_list, year):
        print("オフシーズン")
        print("-"*30)

        sum_retire_player = 0

        # フリー契約の人
        if len(self.free_players) > 0:
            for p in self.free_players:
                # TODO:ここ変えたい
                if p.age<=25:
                    p.grow_up(20)
                    df_result = parctice_player_result(p, year)
                    self.players_result = pd.concat([self.players_result, df_result])
                    p.injury = 0
                else:
                    p.grow_up(0)
                    df_result = self_study_player_result(p, year)
                    self.players_result = pd.concat([self.players_result, df_result])
                    p.injury = 0
                if p.main_position != "GK":
                    p.select_main_position()
                else:
                    p.main_rate = p.cal_rate()
                p.cal_all_rate()

                p.free_time += 1
                p.consider_retirement()
            self.players_result = self.players_result.reset_index(drop=True)
            retire_player = [p for p in self.free_players if p.retire==1]
            self.retire_players.extend(retire_player)
            self.free_players = [p for p in self.free_players if p not in retire_player]

            sum_retire_player += len(retire_player)
        
        # レンタル選手を元のチームに戻す
        for c in self.country_leagues:
            for l in c.leagues:
                for t in l.teams:
                    rental_players = [p for p in t.affilation_players if p.rental==1]
                    t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
                    for p in rental_players:
                        origin_team = p.origin_team
                        p.rental = 0
                        p.origin_team = None
                        p.origin_team_name = ""
                        origin_team.affilation_players.append(p)

        for c in self.country_leagues:
            # 引退と契約切れを行う
            for l in c.leagues:
                for t in l.teams:
                    # 引退
                    retire_player = [p for p in t.affilation_players if p.retire==1]
                    sum_retire_player += len(retire_player)
                    self.retire_players.extend(retire_player)
                    t.affilation_players = [p for p in t.affilation_players if p not in retire_player]

                    # 契約切れ
                    free_players = [p for p in t.affilation_players if p.contract==0]
                    self.free_players.extend(free_players)
                    t.affilation_players = [p for p in t.affilation_players if p not in free_players]

                    # リーグのレベルにそぐわない選手を契約切れに
                    out_players = [p for p in t.affilation_players if p.main_rate>l.max_rate]
                    self.free_players.extend(out_players)
                    t.affilation_players = [p for p in t.affilation_players if p not in out_players]

                    # リーグのレベル以下の選手をレンタル選手に
                    # TODO:のちのちレベル以下も試合に出場したりできるように、誰をレンタルにするかもっと考慮できるシステムを
                    rental_players = [p for p in t.affilation_players if p.main_rate<l.min_rate]
                    set_rental_transfer(rental_players, t)
                    self.free_players.extend(rental_players)
                    t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
        
        print(" 引退人数   　: ", sum_retire_player)
        print(" 移籍市場人数 : ", len(self.free_players))
        
        random.shuffle(self.free_players)

        count = 0
        while True:
            if count > 3:
                break

            for c in random.sample(self.country_leagues, len(self.country_leagues)):
                for l in c.leagues:
                    for t in random.sample(l.teams, len(l.teams)):
                        # 移籍市場から選手を入団させる
                        t.set_main_rate_position()
                        t.set_empty_position(l.standard_rate)
                        self.free_players = t.get_free_players(self.free_players, l)
                        lack_num = t.member_num - len(t.affilation_players)
                        t.set_empty_position_random(lack_num)
                        self.free_players = t.get_free_players(self.free_players, l)
                        t.set_main_rate_position()
                        t.set_register_players_()

                        # 登録外の選手でレンタルにもならない選手を外に出す
                        out_players = [p for p in t.affilation_players if p.register==0 and p.age>=27]
                        for p in out_players:
                            p.contract = 0
                        self.free_players.extend(out_players)
                        t.affilation_players = [p for p in t.affilation_players if p not in out_players]

                        if count<1:
                            # メンバー外の若手をレンタルに
                            rental_players = [p for p in t.affilation_players if p.register==0 and p.age<23]
                            set_rental_transfer(rental_players, t)
                            self.free_players.extend(rental_players)
                            t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
            count+=1
    
        for c in self.country_leagues:
            for l in c.leagues:
                for t in l.teams:
                    lack_num = t.member_num - len(t.affilation_players)
                    t.set_empty_position_random(lack_num, none_gk=True)

                    # 新しく選手を作成する
                    Cp = Create_player(position_num=t.empty_position, 
                                        min_rate=40, max_rate=80, 
                                        age_mean=19,
                                        now_year=year,
                                        mean_rate=l.mean_rate,
                                        df_name_list=df_name_list)

                    Cp.create_teams(new=True)
                    new_players = Cp.players
                    t.affilation_players.extend(new_players)
        
        # 移籍市場からレンタル選手を元のチームに戻す
        rental_players = [p for p in self.free_players if p.rental==1]
        self.free_players = [p for p in self.free_players if p not in rental_players]
        for p in rental_players:
            origin_team = p.origin_team
            p.rental = 0
            p.origin_team = None
            p.origin_team_name = ""
            origin_team.affilation_players.append(p)

class Create_player:
    def __init__(self, position_num, min_rate, max_rate, age_mean, df_name_list, mean_rate=75, now_year=1900):
        self.position_num = position_num
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.mean_rate = mean_rate
        self.df_name_list = df_name_list
        
        self.age_mean = age_mean
        self.now_year = now_year
        self.players = []
        
        # buff zone
        self.pac = 0
        self.sho = 0
        self.pas = 0
        self.dri = 0
        self.de = 0
        self.phy = 0
        self.main_value = 0
    
    def create_teams(self, new=False):
        for pos in ALL_POSITON_LOW:
            if pos not in self.position_num.keys():
                continue
            num = self.position_num[pos]
            count = 0
            while True:
                self.main_value = np.int8(np.round(np.random.normal(self.mean_rate, 1)))
                grow_position_type = self.create_player(pos)
                if new:
                    age = 18
                else:
                    age = min(max(np.int8(np.round(np.random.normal(self.age_mean, 5))), 18), 37)
                injury_possibility = np.random.normal(0.035, 0.02) + max((self.pac-85)*0.005, 0)
                recovery_power = min(max(np.random.normal(69, 5), 50), 80)

                A = FieldPlayer(age=18, now_year=self.now_year, name=random.choice(self.df_name_list), position=None,
                                pace=self.pac, shooting=self.sho, passing=self.pas,
                                dribbling=self.dri, defending=self.de, physicality=self.phy,
                                injury_possibility=injury_possibility,
                                grow_position_type=grow_position_type,
                                recovery_power=recovery_power)
                
                for age_ in range(18, age):
                    A.grow_up(min(np.int8(np.random.normal(30, 3)), 40))
                    A.age += 1

                A.select_main_position()
                if A.main_rate<self.min_rate or A.main_rate>self.max_rate:
                    continue

                A.cal_all_rate()
                A.set_contract()
                count += 1
                self.players.append(A)
                if count >= num:
                    break
        
        count = 0
        while True:
            if "GK" not in self.position_num.keys():
                break
            if count>=self.position_num["GK"]:
                break

            self.main_value = np.int8(np.round(np.random.normal(self.mean_rate, 1)))
            injury_possibility = np.random.normal(0.035, 0.01) + max((self.pac-85)*0.005, 0)
            recovery_power = min(max(np.random.normal(69, 5), 50), 80)

            div = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
            han = np.int8(np.round(np.random.normal(div, 1)))
            kic = np.int8(np.round(np.random.normal(60, 10)))
            ref = np.int8(np.round(np.random.normal(div, 1)))
            spe = np.int8(np.round(np.random.normal(60, 15)))
            pos = np.int8(np.round(np.random.normal(div, 1)))

            if div>99 or han>99 or kic>99 or ref>99 or spe>99 or pos>99:
                continue

            if new:
                age = 18
            else:
                age = min(max(np.int8(np.round(np.random.normal(self.age_mean, 5))), 18), 37)

            A = GK(name=random.choice(self.df_name_list), age=age, now_year=self.now_year, 
                   position="GK",diving=div, handling=han, kicking=kic,
                   reflexes=ref, speed=spe, positioning=pos,
                   injury_possibility=injury_possibility,
                   recovery_power=recovery_power)
            
            for age_ in range(18, age):
                A.grow_up(40)
                A.age += 1

            A.main_rate = A.cal_rate()
            A.cal_all_rate()
            A.set_contract()

            if A.main_rate<self.min_rate or A.main_rate>self.max_rate:
                continue

            self.players.append(A)
            count += 1

    def create_player(self, pos):
        while True:
            if pos == "ST":
                if np.random.normal(0, 1) > 0:
                    self.sho = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.pac = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.pas = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.main_value-5, 1)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                    self.sho = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.pas = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.main_value-5, 1)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(self.main_value, 0.5)))
                    pos = "ST_"

            elif pos == "RW":
                self.pac = np.int8(np.round(np.random.normal(80, 5)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value, 0.5)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.sho = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.de = np.int8(np.round(np.random.normal(30, 5)))
                self.phy = np.int8(np.round(np.random.normal(50, 7)))

            elif pos == "RM":
                self.pac = np.int8(np.round(np.random.normal(70, 7)))
                self.sho = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.de = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.phy = np.int8(np.round(np.random.normal(50, 7)))

            elif pos == "RB" or pos == "RWB":
                self.pac = np.int8(np.round(np.random.normal(80, 5)))
                self.sho = np.int8(np.round(np.random.normal(40, 7)))
                self.de = np.int8(np.round(np.random.normal(self.main_value-3, 5)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                self.phy = np.int8(np.round(np.random.normal(self.main_value-10, 7)))

            elif pos=="CAM":
                self.pac = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.sho = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.de = np.int8(np.round(np.random.normal(40, 7)))
                self.phy = np.int8(np.round(np.random.normal(50, 7)))

            elif pos=="CM":
                self.pac = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                self.sho = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.de = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                self.phy = np.int8(np.round(np.random.normal(self.main_value-10, 7)))

            elif pos=="CDM":
                self.pac = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.sho = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.de = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value-5, 3)))
                self.phy = np.int8(np.round(np.random.normal(self.main_value-5, 3)))

            elif pos=="CB":
                self.pac = np.int8(np.round(np.random.normal(60, 7)))
                self.sho = np.int8(np.round(np.random.normal(40, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value-20, 10)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value-20, 10)))
                self.de = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.phy = np.int8(np.round(np.random.normal(self.main_value, 1.5)))

            if self.pac>99 or self.de>99 or self.sho>99 or self.pas>99 or self.dri>99 or self.phy>99:
                continue
            else:
                break
        return pos
        """
        while True:
            if pos == "ST":
                if np.random.normal(0, 1) > 0:
                    self.pac = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.sho = np.int8(np.round(np.random.normal(self.pac, 0.5)))
                    self.pas = np.int8(np.round(np.random.normal(60, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.pac-5, 1)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(60, 7)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(60, 7)))
                    self.sho = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.pas = np.int8(np.round(np.random.normal(60, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.sho-5, 1)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(self.sho, 0.5)))
                    pos = "ST_"
            
            elif pos == "RW":
                if np.random.normal(0, 1) > 0:
                    self.pac = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.sho = np.int8(np.round(np.random.normal(60, 7)))
                    self.pas = np.int8(np.round(np.random.normal(self.pac-5, 1)))
                    self.dri = np.int8(np.round(np.random.normal(self.pac, 0.5)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(50, 7)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(60, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.sho = np.int8(np.round(np.random.normal(self.dri, 0.5)))
                    self.pas = np.int8(np.round(np.random.normal(self.dri-5, 1)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(50, 5)))
                    pos = "RW_"
            
            elif pos == "RM":
                self.pac = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.sho = np.int8(np.round(np.random.normal(60, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.pac, 0.5)))
                self.dri = np.int8(np.round(np.random.normal(self.pac-5, 1)))
                self.de = np.int8(np.round(np.random.normal(50, 7)))
                self.phy = np.int8(np.round(np.random.normal(60, 7)))
            
            elif pos == "RB" or pos == "RWB":
                if np.random.normal(0, 1) > 0:
                    self.pac = np.int8(np.round(np.random.normal(70, 7)))
                    self.sho = np.int8(np.round(np.random.normal(50, 7)))
                    self.de = np.int8(np.round(np.random.normal(self.main_value-5, 1)))
                    self.pas = np.int8(np.round(np.random.normal(self.de-5, 1)))
                    self.dri = np.int8(np.round(np.random.normal(self.pas, 0.5)))
                    self.phy = np.int8(np.round(np.random.normal(60, 7)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(60, 7)))
                    self.sho = np.int8(np.round(np.random.normal(50, 7)))
                    self.de = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                    self.pas = np.int8(np.round(np.random.normal(self.de, 0.5)))
                    self.dri = np.int8(np.round(np.random.normal(self.de, 0.5)))
                    self.phy = np.int8(np.round(np.random.normal(60, 7)))
                    pos = "RB_"

            elif pos=="CAM":
                self.pac = np.int8(np.round(np.random.normal(60, 7)))
                self.sho = np.int8(np.round(np.random.normal(70, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.pas, 0.5)))
                self.de = np.int8(np.round(np.random.normal(40, 7)))
                self.phy = np.int8(np.round(np.random.normal(60, 7)))
            
            elif pos=="CM":
                self.pac = np.int8(np.round(np.random.normal(65, 7)))
                self.sho = np.int8(np.round(np.random.normal(60, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.pas, 0.5)))
                self.de = np.int8(np.round(np.random.normal(self.pas-5, 1)))
                self.phy = np.int8(np.round(np.random.normal(self.pas-3, 1)))
            
            elif pos=="CDM":
                self.pac = np.int8(np.round(np.random.normal(60, 7)))
                self.sho = np.int8(np.round(np.random.normal(55, 7)))
                self.de = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.pas = np.int8(np.round(np.random.normal(self.de-5, 1)))
                self.dri = np.int8(np.round(np.random.normal(self.pas, 0.5)))
                self.phy = np.int8(np.round(np.random.normal(self.de, 0.5)))
            
            elif pos=="CB":
                self.pac = np.int8(np.round(np.random.normal(60, 7)))
                self.sho = np.int8(np.round(np.random.normal(40, 7)))
                self.pas = np.int8(np.round(np.random.normal(60, 7)))
                self.dri = np.int8(np.round(np.random.normal(60, 7)))
                self.de = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.phy = np.int8(np.round(np.random.normal(self.de-5, 1)))

            if self.pac>99 or self.de>99 or self.sho>99 or self.pas>99 or self.dri>99 or self.phy>99:
                continue
            else:
                break
        return pos
    """
