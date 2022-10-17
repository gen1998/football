import numpy as np
import pandas as pd

import random
import time
import uuid

from tqdm import tqdm

import sys
sys.path.append("../")

from config.config import *
from src.apply import *
from src.utils import *

class FootBaller:
    def __init__(self, name, age, now_year, injury_possibility, grow_position_type):
        self.age = age
        self.name = name
        self.grow_min_age = min(max(np.int8(np.round(np.random.normal(24, 0.5))), 22), 26)
        self.grow_old_age_1 = min(max(np.int8(np.round(np.random.normal(29, 0.5))), 27), 31)
        self.grow_old_age_2 = max(np.int8(np.round(np.random.normal(33, 0.5))), 31)
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
        self.grow_type = random.choices(["legend", "genius", "general", "grass"], weights=[1, 10, 70, 19])[0]

        self.position_all_rate = {}
        self.position_all_rate_sorted = []
        self.index = None
    
    def get_goal(self, season_name):
        self.result[season_name]["goal"] += 1
    
    def get_assist(self, season_name):
        self.result[season_name]["assist"] += 1
    
    def get_game_count(self, season_name):
        self.result[season_name]["試合数"] += 1
    
    def get_cs(self, season_name):
        self.result[season_name]["CS"] += 1
    
    def get_default(self, season_name):
        self.result[season_name]["怪我欠場"] += 1
    
    def get_injury(self, season_name):
        self.result[season_name]["怪我回数"] += 1
    
    def consider_retirement(self):
        if self.retire!=1 and self.main_rate<80:
            rate = 0.00132*self.age*self.age - 1.18 + np.random.normal(0, 0.1) + self.injury_possibility
            if rate > np.random.rand():
                self.retire = 1
        
        if (self.free_time>1 and self.age>=26) or self.free_time>3:
            self.retire = 1

        self.age += 1

    def set_contract(self):
        self.free_time = 0
        self.contract = min(max(np.int8(np.round(np.random.normal((40 - self.age)/4, 0.5))), 1), 7)

class FieldPlayer(FootBaller):
    def __init__(self, name, age, now_year, position, pace, shooting, 
                 passing, dribbling, defending, physicality, 
                 injury_possibility=0, 
                 grow_position_type=None):
        super().__init__(name, age, now_year, injury_possibility, grow_position_type)
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

        self.partification = 0
        self.partification_position = None
    
    def cal_rate(self, position=None):
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
            self.shooting_exp += game_num*grow_game_rate + grow_year_rate
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)*0.7
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "ST_":
            self.shooting_exp += game_num*grow_game_rate + grow_year_rate
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.physicality_exp += game_num*grow_game_rate + grow_year_rate
        elif self.grow_position_type == "RW":
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.pace_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/3
        elif self.grow_position_type == "RW_":
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.pace_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)*0.9
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "RM":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.passing_exp += game_num*grow_game_rate + grow_year_rate
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "RB" or self.grow_position_type == "RWB":
            self.pace_exp += game_num*grow_game_rate + grow_year_rate
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/4
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.defending_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)/2
        elif self.grow_position_type == "RB_":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.shooting_exp += (game_num*grow_game_rate + grow_year_rate)/4
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
            self.defending_exp += game_num*grow_game_rate + grow_year_rate
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
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.defending_exp += game_num*grow_game_rate + grow_year_rate
            self.physicality_exp += (game_num*grow_game_rate + grow_year_rate)*0.8
        elif self.grow_position_type == "CB":
            self.pace_exp += (game_num*grow_game_rate + grow_year_rate)/1.5
            self.passing_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.dribbling_exp += (game_num*grow_game_rate + grow_year_rate)/2
            self.defending_exp += game_num*grow_game_rate + grow_year_rate
            self.physicality_exp += game_num*grow_game_rate + grow_year_rate
        
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
                 grow_position_type=None):
        super().__init__(name, age, now_year, injury_possibility, grow_position_type)
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
                 formation_num, formation_shooting_rate, formation_assist_rate):
        self.name = name
        self.formation = formation
        self.formation_priority = formation_priority
        self.formation_num = formation_num
        self.formation_shooting_rate = formation_shooting_rate
        self.formation_assist_rate = formation_assist_rate
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
    def __init__(self, name, formation, min_rate=75, max_rate=85, member_num=30):
        self.name = name
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.formation = formation
        self.relegation = 0
        self.promotion = 0
        self.result = pd.DataFrame(columns=['win', 'lose', 'row', '得点', '失点', '得失点差', 'Points', '順位', 'リーグ名'])
        self.competition_result = {}
        self.affilation_players = None
        self.register_players = None
        self.not_register_players = None
        self.league_name = None
        self.member_num = member_num

        self.empty_position = {}
        self.formation_rate = {}

    def set_register_players(self):
        """
        for p in self.affilation_players:
            p.register = 0

        for pos, num in GENERAL_POSITION_NUM.items():
            not_register = [p for p in self.affilation_players if p.register==0]
            not_register = sorted(not_register, key=lambda x:x.position_all_rate[pos], reverse=True)
            for p in not_register[:num]:
                p.register = 1
        """

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
    
    def set_affilation_players_rate(self):
        for p in self.register_players:
            p.partification = 0
    
    def set_onfield_players(self):
        """
        for p in self.register_players:
            p.partification = 0

        self.formation.set_players_position()
        self.formation.players_flat = []

        for fp in self.formation.formation_priority:
            select_num = self.formation.formation_num[fp]
            partification_players = [p for p in self.register_players if p.partification==0 and p.injury<1]
            partification_players = sorted(partification_players, key=lambda x:x.position_all_rate[fp], reverse=True)
            partification_players = partification_players[:select_num]

            for p in partification_players:
                p.partification = 1
                p.partification_position = fp
                self.formation.players[fp].append(p)

        for fps in self.formation.players.values():
            self.formation.players_flat.extend(fps)
        """

        self.formation.set_players_position()
        self.formation.players_flat = []
        self.formation.main_rate_formation = {}

        for pos in self.formation.formation_flat:
            self.formation.main_rate_formation[pos] = []
        
        for p in self.affilation_players:
            p.index = 0
            p.partification = 0
            p.position_all_rate_sorted = sorted(p.position_all_rate.items(), key=lambda x:x[1], reverse=True)
        
        remain_players = [p for p in self.register_players if p.injury<1]
        count = 0

        while True:
            if count>5 and len([p for ps in list(self.formation.main_rate_formation.values()) for p in ps])==11:
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
        
        for pos, players in self.formation.main_rate_formation.items():
            for p in players:
                p.partification = 1
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

        self.formation.mean_rate = rate_sum/num
    
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
                 mid_rate=0.5, gk_rate=0.2, random_std=10, 
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
        self.result = None
        self.pk = pk
        self.extra = extra
    
    # 誰が得点者でアシストしたか
    def cal_goal_assit_player(self, side):
        # goal
        a = np.array([s.shooting for s in side.formation.players_flat])
        b = np.array(side.formation.formation_shooting_rate)
        weights = a*b/sum(a*b)
        np.random.choice(side.formation.players_flat, 1, p=weights)[0].get_goal(self.competition_name)
        
        # asssit
        if np.random.randn() > 0:
            a = np.array([s.passing for s in side.formation.players_flat])
            b = np.array(side.formation.formation_assist_rate)
            weights = a*b/sum(a*b)
            np.random.choice(side.formation.players_flat, 1, p=weights)[0].get_assist(self.competition_name)
        
    
    def moment_battle(self):
        home_rate = self.home.formation.team_rate
        away_rate = self.away.formation.team_rate

        home_ratio = home_rate['ALL']/(home_rate['ALL']+away_rate['ALL'])
        away_ratio = away_rate['ALL']/(home_rate['ALL']+away_rate['ALL'])
        
        home_attack = (home_rate['ATT']+home_rate['MID']*self.mid_rate)*home_ratio
        away_attack = (away_rate['ATT']+away_rate['MID']*self.mid_rate)*away_ratio
        
        home_defence = (home_rate['DEF']+home_rate['MID']*self.mid_rate)*home_ratio+home_rate["GK"]*self.gk_rate
        away_defence = (away_rate['DEF']+away_rate['MID']*self.mid_rate)*away_ratio+away_rate["GK"]*self.gk_rate
        
        if home_attack-away_defence+np.random.normal(0, self.random_std) > 0:
            self.home_goal += 1
            self.cal_goal_assit_player(self.home)
            
        
        if away_attack-home_defence+np.random.normal(0, self.random_std) > 0:
            self.away_goal += 1
            self.cal_goal_assit_player(self.away)
    
    def battle(self):
        self.home_goal = 0
        self.away_goal = 0

        # 試合数カウント
        for t in self.home.formation.players_flat:
            t.get_game_count(self.competition_name)
        
        for t in self.away.formation.players_flat:
            t.get_game_count(self.competition_name)

        # 90分間試合
        for i in range(self.moment_num):
            self.moment_battle()
        
        if self.home_goal>self.away_goal:
            self.result="home"
        elif self.home_goal<self.away_goal:
            self.result="away"
        elif self.extra==1 or self.pk==1:
            #延長戦
            if self.extra==1:
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
            for t in self.home.formation.players_flat:
                t.get_cs(self.competition_name)
        if self.home_goal == 0:
            for t in self.away.formation.players_flat:
                t.get_cs(self.competition_name)
        
        # 怪我 F分布で表現
        for p in self.home.formation.players_flat:
            if p.injury_possibility>np.random.rand():
                p.injury=min(max(np.int8(np.round(np.random.f(100, 5)*5)), 1), 40)
                p.get_injury(self.competition_name)
                if p.injury > 20:
                    p.down_ability(3)
                    if p.injury > 30 and p.age > p.grow_old_age_1 and np.random.rand()<0.5:
                        p.retire = 1
        
        for p in self.away.formation.players_flat:
            if p.injury_possibility>np.random.rand():
                p.injury=min(max(np.int8(np.round(np.random.f(100, 5)*5)), 1), 40)
                p.get_injury(self.competition_name)
                if p.injury > 20:
                    p.down_ability(3)
                    if p.injury > 30 and p.age > p.grow_old_age_1 and np.random.rand()<0.5:
                        p.retire = 1

class League:
    def __init__(self, name, teams, num, category, relegation_num=0, promotion_num=0, min_rate=75, max_rate=85, mean_rate=80, standard_rate=78):
        self.name = name
        self.teams = teams
        self.num = num
        self.category = category
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.mean_rate = mean_rate
        self.standard_rate = standard_rate

        self.team_result = {}
        self.player_result = {}
        self.champion = pd.DataFrame(columns=["優勝", "得点王"])
        
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
        self.team_result[season_name]["順位"] = [f"{i}位" for i in range(1, 21)]
        self.team_result[season_name]["リーグ名"] = [f"{self.name}" for i in range(20)]
        
        for team in self.teams:
            team.result.loc[season_name] = self.team_result[season_name].loc[team.name, :]
        
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
            # 怪我を一つ進める
            for p in self.teams[section[0]-1].register_players:
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(season_name)
            for p in self.teams[section[1]-1].register_players:
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(season_name)

            # スターティングメンバーを作る
            #self.teams[section[0]-1].set_affilation_players_rate()
            self.teams[section[0]-1].set_onfield_players()
            self.teams[section[0]-1].formation.cal_team_rate()
            #self.teams[section[1]-1].set_affilation_players_rate()
            self.teams[section[1]-1].set_onfield_players()
            self.teams[section[1]-1].formation.cal_team_rate()
            

            game = Game(home=self.teams[section[0]-1], 
                        away=self.teams[section[1]-1], 
                        competition_name=season_name,
                        moment_num=9,
                        random_std=15)
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

class ProSoccerLeague:
    def __init__(self, name, leagues):
        self.name = name
        self.leagues = leagues

        self.players_result = pd.DataFrame()

        self.competition = None
        self.competition_teams = None
        self.competition_result = {}
        self.competition_result_top = pd.DataFrame(columns=["年度", "優勝", "準優勝"])

        self.retire_players = []
        self.free_players = []
    
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
                                        "ポジション":[p.partification_position for p in t.register_players],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in season_result],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":["" for i in range(len(t.register_players))],
                                        "分類":[result["分類"] for result in season_result],
                                        "順位" :  [f"{league_rank.index(t.name)+1}位" for i in range(len(t.register_players))],
                                        "試合数":[result["試合数"] for result in season_result],
                                        "goal":[result["goal"] for result in season_result],
                                        "assist":[result["assist"] for result in season_result],
                                        "CS":[result["CS"] for result in season_result],
                                        "怪我欠場":[result["怪我欠場"] for result in season_result],
                                        "怪我回数":[result["怪我回数"] for result in season_result],
                                        "賞":["" for i in range(len(t.register_players))]})
                all_output = pd.concat([all_output, output])

                output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                        "uuid":[p.uuid for p in t.register_players],
                                        "年齢":[result["年齢"] for result in competition_result],
                                        "Rate" : [p.main_rate for p in t.register_players],
                                        "残契約":[p.contract-1 for p in t.register_players],
                                        "ポジション":[p.partification_position for p in t.register_players],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in competition_result],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":["" for i in range(len(t.register_players))],
                                        "分類":[result["分類"] for result in competition_result],
                                        "順位" :  [f"{league_rank.index(t.name)+1}位" for i in range(len(t.register_players))],
                                        "試合数":[result["試合数"] for result in competition_result],
                                        "goal":[result["goal"] for result in competition_result],
                                        "assist":[result["assist"] for result in competition_result],
                                        "CS":[result["CS"] for result in competition_result],
                                        "怪我欠場":[result["怪我欠場"] for result in competition_result],
                                        "怪我回数":[result["怪我回数"] for result in competition_result],
                                        "賞":["" for i in range(len(t.register_players))]})
                all_output = pd.concat([all_output, output])
                """
                for p in t.register_players:
                    season_result = p.result[season_name]
                    competition_result = p.result[self.competition.name]

                    output = pd.DataFrame({"名前":[p.name, p.name],
                                           "uuid":[p.uuid, p.uuid],
                                           "年齢":[season_result["年齢"], competition_result["年齢"]],
                                           "Rate" : [p.main_rate, p.main_rate],
                                           "残契約":[p.contract-1, p.contract-1],
                                           "ポジション":[p.partification_position, p.partification_position],
                                           "リーグ":[l.name, l.name],
                                           "年度":[season_result["年度"], competition_result["年度"]],
                                           "チーム":[t.name, t.name],
                                           "レンタル元":["", ""],
                                           "分類":[season_result["分類"], competition_result["分類"]],
                                           "順位" :  f"{league_rank.index(t.name)+1}位",
                                           "試合数":[season_result["試合数"], competition_result["試合数"]],
                                           "goal":[season_result["goal"], competition_result["goal"]],
                                           "assist":[season_result["assist"], competition_result["assist"]],
                                           "CS":[season_result["CS"], competition_result["CS"]],
                                           "怪我欠場":[season_result["怪我欠場"], competition_result["怪我欠場"]],
                                           "賞":["", ""]})
                    all_output = pd.concat([all_output, output])
                """
                for p in t.register_players:
                    season_result = p.result[season_name]
                    competition_result = p.result[self.competition.name]
                    p.contract -= 1

                    # 再契約する処理
                    if p.contract == 0 and p.partification_position is not None:
                        if np.random.rand()<0.3:
                            p.set_contract()
                    
                    # 試合に出てない人を戦力外にする処理
                    if p.partification_position is None:
                        if p.contract<3 and np.random.rand()<0.7:
                            p.contract = 0
                    
                    # 成長
                    p.grow_up(season_result["試合数"]+competition_result["試合数"])
                    if p.main_position != "GK":
                        p.select_main_position()
                    else:
                        p.main_rate = p.cal_rate()
                    p.cal_all_rate()

                    # offseason分怪我を経過させる
                    p.injury = max(p.injury-10, 0)

                    # 引退
                    p.consider_retirement()
        
        self.players_result = pd.concat([self.players_result, all_output])
        self.players_result = self.players_result.reset_index(drop=True)

        # コンペティション最多得点
        df_search = self.players_result[((self.players_result["分類"]=="カップ戦")&(self.players_result["年度"]==year))]
        df_search_index = pd.to_numeric(df_search["goal"]).idxmax()
        self.players_result.loc[df_search_index, "賞"] += f"得点王({self.competition.name}), "
        self.competition_result_top.loc[self.competition.name, "得点王"] = f"{df_search.loc[df_search_index, '名前']}({df_search.loc[df_search_index, 'チーム']}({df_search.loc[df_search_index, 'リーグ']}))  /  {df_search.loc[df_search_index, 'goal']}点"

        # リーグ最多得点
        for l in self.leagues:
            season_name = f'{l.name}_{year}'
            df_search = self.players_result[((self.players_result["分類"]=="リーグ")&(self.players_result["年度"]==year)&(self.players_result["リーグ"]==l.name))]
            df_search_index = pd.to_numeric(df_search["goal"]).idxmax()
            self.players_result.loc[df_search_index, "賞"] += f"得点王({season_name}), "
            l.champion.loc[season_name, "得点王"] = f"{df_search.loc[df_search_index, '名前']}({df_search.loc[df_search_index, 'チーム']})  /  {df_search.loc[df_search_index, 'goal']}点"

    def set_register_member(self):
        for l in self.leagues:
            for t in l.teams:
                #print(len([p for p in t.affilation_players if p.main_position=="GK"]))
                t.set_main_rate_position()
                t.set_register_players()
    
    def play_1season(self, year, competition):
        league_calender = create_calender()
        num_section = len(league_calender)
        self.competition = competition
        self.set_competition(self.competition.name, year, num_section)
        self.set_players_partification()
        self.set_register_member()
        
        # 必要変数をセッティング
        for l in self.leagues:
            l.set_team_leaguename()
            season_name = f'{l.name}_{year}'
            l.set_player_result(season_name, year, "リーグ")
            l.set_team_result(season_name)
        #s = time.time()
        # 一年play
        for day in tqdm(range(num_section)):
            if day==int(self.competition.section_interval*self.competition.now_round):
                self.play_1competition_section(year)
            sections = league_calender.iloc[day, :]
            for league in self.leagues:
                league.play_1section(year, sections)
        #b = time.time()
        #print("1年play : ", b-s)
        
        #s = time.time()
        for l in self.leagues:
            l.cal_1year_result(year)
        #b = time.time()
        #print("リーグresult : ", b-s)

        #s = time.time()
        # 登録外のメンバーをレンタル先で活躍させる
        all_output = pd.DataFrame()
        for l in self.leagues:
            for t in l.teams:
                for p in t.not_register_players:
                    p.contract -= 1
                    p.grow_up(20)
                    df_result = rental_player_result(p, year, t.name)
                    all_output = pd.concat([all_output, df_result])

                    if p.main_position != "GK":
                        p.select_main_position()
                    else:
                        p.main_rate = p.cal_rate()
                    
                    # 登録メンバー外の成長が止まった選手は戦力外
                    if p.age>p.grow_min_age:
                        p.contract=0

                    p.cal_all_rate()
                    p.consider_retirement()
        self.players_result = pd.concat([self.players_result, all_output])
        self.players_result = self.players_result.reset_index(drop=True)
        #b = time.time()
        #print("レンタル : ", b-s)
        
        #s = time.time()
        self.cal_players_result(year)
        #print("self.players_result", self.players_result)
        #b = time.time()
        #print("player result : ", b-s)
        
        #s = time.time()
        for index in range(len(self.leagues)):
            season_name = f"{self.leagues[index].name}_{year}"
            if self.leagues[index].category!="top":
                promotion = self.leagues[index].promotion[season_name]
                promotion_team = [t for t in self.leagues[index].teams if t.name in promotion]
                self.leagues[index].teams = [s for s in self.leagues[index].teams if s not in promotion_team]
                self.leagues[index-1].teams.extend(promotion_team)

            if self.leagues[index].category!="lowest":
                relegation = self.leagues[index].relegation[season_name]
                relegation_team = [t for t in self.leagues[index].teams if t.name in relegation]
                self.leagues[index].teams = [s for s in self.leagues[index].teams if s not in relegation_team]
                self.leagues[index+1].teams.extend(relegation_team)
        #b = time.time()
        #print("昇格降格 : ", b-s)
            
        #print("self.players_result", self.players_result)
    
    def play_offseason(self, df_name_list, year):
        # フリー契約の人
        if len(self.free_players) > 0:
            for p in self.free_players:
                if p.age<=25:
                    p.grow_up(20)
                    df_result = parctice_player_result(p, year)
                    self.players_result = pd.concat([self.players_result, df_result])
                else:
                    p.grow_up(0)
                    df_result = self_study_player_result(p, year)
                    self.players_result = pd.concat([self.players_result, df_result])
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

        # 引退と契約切れを行う
        for l in self.leagues:
            for t in l.teams:
                # 引退
                retire_player = [p for p in t.affilation_players if p.retire==1]
                self.retire_players.extend(retire_player)
                t.affilation_players = [p for p in t.affilation_players if p not in retire_player]

                # 契約切れ
                free_players = [p for p in t.affilation_players if p.contract==0]
                self.free_players.extend(free_players)
                t.affilation_players = [p for p in t.affilation_players if p not in free_players]

                # リーグのレベルにそぐわない選手を契約切れに
                out_players = [p for p in t.affilation_players if p.main_rate>=l.max_rate]
                self.free_players.extend(out_players)
                t.affilation_players = [p for p in t.affilation_players if p not in out_players]

                empty_players_pos = {}
                empty_players_pos = create_empty_position(empty_players_pos, retire_player)
                empty_players_pos = create_empty_position(empty_players_pos, free_players)
                empty_players_pos = create_empty_position(empty_players_pos, out_players)
                t.empty_position = empty_players_pos
        
        random.shuffle(self.free_players)

        count = 0
        while True:
            if count > 2:
                break
            for l in self.leagues:
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
                    self.free_players.extend(out_players)
                    t.affilation_players = [p for p in t.affilation_players if p not in out_players]
            count+=1

        for l in self.leagues:
            for t in l.teams:
                lack_num = t.member_num - len(t.affilation_players)
                t.set_empty_position_random(lack_num, none_gk=True)

                # 新しく選手を作成する
                Cp = Create_player(position_num=t.empty_position, 
                                    min_rate=40, max_rate=80, 
                                    age_mean=20,
                                    now_year=year,
                                    mean_rate=l.mean_rate,
                                    df_name_list=df_name_list)

                Cp.create_teams(new=True)
                new_players = Cp.players
                t.affilation_players.extend(new_players)
        
        """
        for l in self.leagues:
            for t in random.sample(l.teams, len(l.teams)):
                # 移籍市場から選手を入団させる
                for pos in ALL_POSITON_LOW_GK:
                    if pos not in t.empty_position.keys():
                        continue
                    num = t.empty_position[pos]
                    new_players = [p for p in self.free_players if p.main_position in POSITION_LOW_DICT[pos] and p.main_rate>=l.min_rate and p.main_rate<=l.max_rate]
                    new_players = sorted(new_players, key=lambda x:x.main_rate, reverse=True)
                    if len(new_players) >= num:
                        new_players = new_players[:num]
                        t.empty_position.pop(pos)
                    else:
                        t.empty_position[pos] -= len(new_players)
                    for p in new_players:
                        p.set_contract()
                        #print(p.main_position)

                    t.affilation_players.extend(new_players)
                    self.free_players = [p for p in self.free_players if p not in new_players]

                # 新しく選手を作成する
                Cp = Create_player(position_num=t.empty_position, 
                                    min_rate=40, max_rate=80, 
                                    age_mean=20,
                                    now_year=year,
                                    mean_rate=l.mean_rate,
                                    df_name_list=df_name_list)
                Cp.create_teams(new=True)
                new_players = Cp.players
                t.affilation_players.extend(new_players)
        """
                    
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
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(self.competition.name)
            for p in game_team[1].register_players:
                if p.injury>0:
                    p.injury -= 1
                    p.get_default(self.competition.name)
            
            # スターティングメンバーを作る
            #game_team[0].set_affilation_players_rate()
            game_team[0].set_onfield_players()
            game_team[0].formation.cal_team_rate()
            #game_team[1].set_affilation_players_rate()
            game_team[1].set_onfield_players()
            game_team[1].formation.cal_team_rate()

            cup_game = Game(home=game_team[0], 
                            away=game_team[1], 
                            competition_name=self.competition.name,
                            moment_num=9,
                            random_std=20,
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
                injury_possibility = np.random.normal(0.05, 0.02) + max((self.pac-85)*0.005, 0)

                A = FieldPlayer(age=18, now_year=self.now_year, name=random.choice(self.df_name_list), position=None,
                                pace=self.pac, shooting=self.sho, passing=self.pas,
                                dribbling=self.dri, defending=self.de, physicality=self.phy,
                                injury_possibility=injury_possibility,
                                grow_position_type=grow_position_type)
                
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
            injury_possibility = np.random.normal(0.02, 0.01) + max((self.pac-85)*0.005, 0)

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
                   injury_possibility=injury_possibility)
            
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
    def create_player(self, pos):
        while True:
            if pos == "ST":
                if np.random.normal(0, 1) > 0:
                    self.pac = np.int8(np.round(np.random.normal(self.main_value, 5)))
                    self.sho = np.int8(np.round(np.random.normal(self.pac, 5)))
                    self.pas = np.int8(np.round(np.random.normal(60, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.pac-5, 5)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(60, 7)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(60, 7)))
                    self.sho = np.int8(np.round(np.random.normal(self.main_value, 5)))
                    self.pas = np.int8(np.round(np.random.normal(60, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.sho-5, 5)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(self.sho, 5)))
                    pos = "ST_"
            
            elif pos == "RW":
                if np.random.normal(0, 1) > 0:
                    self.pac = np.int8(np.round(np.random.normal(70, 7)))
                    self.sho = np.int8(np.round(np.random.normal(60, 7)))
                    self.pas = np.int8(np.round(np.random.normal(self.pac-5, 5)))
                    self.dri = np.int8(np.round(np.random.normal(self.pac, 5)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(50, 7)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(60, 7)))
                    self.dri = np.int8(np.round(np.random.normal(self.main_value, 5)))
                    self.sho = np.int8(np.round(np.random.normal(self.dri, 5)))
                    self.pas = np.int8(np.round(np.random.normal(self.dri-5, 5)))
                    self.de = np.int8(np.round(np.random.normal(30, 5)))
                    self.phy = np.int8(np.round(np.random.normal(50, 5)))
                    pos = "RW_"
            
            elif pos == "RM":
                self.pac = np.int8(np.round(np.random.normal(70, 7)))
                self.sho = np.int8(np.round(np.random.normal(60, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.pac, 5)))
                self.dri = np.int8(np.round(np.random.normal(self.pac-5, 5)))
                self.de = np.int8(np.round(np.random.normal(50, 7)))
                self.phy = np.int8(np.round(np.random.normal(60, 7)))
            
            elif pos == "RB":
                if np.random.normal(0, 1) > 0:
                    self.pac = np.int8(np.round(np.random.normal(70, 7)))
                    self.sho = np.int8(np.round(np.random.normal(50, 7)))
                    self.de = np.int8(np.round(np.random.normal(60, 7)))
                    self.pas = np.int8(np.round(np.random.normal(self.de-5, 5)))
                    self.dri = np.int8(np.round(np.random.normal(self.pas, 5)))
                    self.phy = np.int8(np.round(np.random.normal(60, 7)))
                else:
                    self.pac = np.int8(np.round(np.random.normal(60, 7)))
                    self.sho = np.int8(np.round(np.random.normal(50, 7)))
                    self.de = np.int8(np.round(np.random.normal(self.main_value, 5)))
                    self.pas = np.int8(np.round(np.random.normal(self.de, 5)))
                    self.dri = np.int8(np.round(np.random.normal(self.de, 5)))
                    self.phy = np.int8(np.round(np.random.normal(60, 7)))
                    pos = "RB_"

            elif pos=="CAM":
                self.pac = np.int8(np.round(np.random.normal(60, 7)))
                self.sho = np.int8(np.round(np.random.normal(65, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 5)))
                self.dri = np.int8(np.round(np.random.normal(self.pas, 5)))
                self.de = np.int8(np.round(np.random.normal(40, 7)))
                self.phy = np.int8(np.round(np.random.normal(60, 7)))
            
            elif pos=="CM":
                self.pac = np.int8(np.round(np.random.normal(65, 7)))
                self.sho = np.int8(np.round(np.random.normal(60, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 5)))
                self.dri = np.int8(np.round(np.random.normal(self.pas, 3)))
                self.de = np.int8(np.round(np.random.normal(self.pas-5, 3)))
                self.phy = np.int8(np.round(np.random.normal(self.pas-3, 3)))
            
            elif pos=="CDM":
                self.pac = np.int8(np.round(np.random.normal(60, 7)))
                self.sho = np.int8(np.round(np.random.normal(55, 7)))
                self.de = np.int8(np.round(np.random.normal(self.main_value, 5)))
                self.pas = np.int8(np.round(np.random.normal(self.de-5, 5)))
                self.dri = np.int8(np.round(np.random.normal(self.pas, 5)))
                self.phy = np.int8(np.round(np.random.normal(self.de, 5)))
            
            elif pos=="CB":
                self.pac = np.int8(np.round(np.random.normal(70, 7)))
                self.sho = np.int8(np.round(np.random.normal(40, 7)))
                self.pas = np.int8(np.round(np.random.normal(60, 7)))
                self.dri = np.int8(np.round(np.random.normal(60, 7)))
                self.de = np.int8(np.round(np.random.normal(self.main_value, 5)))
                self.phy = np.int8(np.round(np.random.normal(self.de, 5)))

            if self.pac>99 or self.de>99 or self.sho>99 or self.pas>99 or self.dri>99 or self.phy>99:
                continue
            else:
                break
        return pos

    def create_teams(self):
        for pos in ALL_POSITON_LOW:
            if pos not in self.position_num.keys():
                continue
            num = self.position_num[pos]
            count = 0
            while True:
                grow_position_type = self.create_player(pos)
                age = min(max(np.int8(np.round(np.random.normal(self.age_mean, 4))), 18), 37)
                injury_possibility = np.random.normal(0.03, 0.02) + max((self.pac-85)*0.005, 0)

                A = FieldPlayer(age=age, name=random.choice(self.df_name_list), position=None,
                                pace=self.pac, shooting=self.sho, passing=self.pas,
                                dribbling=self.dri, defending=self.de, physicality=self.phy,
                                injury_possibility=injury_possibility,
                                grow_position_type=grow_position_type)

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

            age = min(max(np.int8(np.round(np.random.normal(self.age_mean, 4))), 18), 37)
            div = np.int8(np.round(np.random.normal(70, 10)))
            han = np.int8(np.round(np.random.normal(div, 5)))
            kic = np.int8(np.round(np.random.normal(60, 10)))
            ref = np.int8(np.round(np.random.normal(div, 5)))
            spe = np.int8(np.round(np.random.normal(60, 15)))
            pos = np.int8(np.round(np.random.normal(div, 5)))

            if div>99 or han>99 or kic>99 or ref>99 or spe>99 or pos>99:
                continue

            A = GK(name=random.choice(self.df_name_list), age=age, position="GK",
                   diving=div, handling=han, kicking=kic,
                   reflexes=ref, speed=spe, positioning=pos)

            A.cal_rate()
            A.cal_all_rate()
            A.set_contract()

            if A.main_rate<self.min_rate or A.main_rate>self.max_rate:
                continue

            self.players.append(A)
            count += 1
    """