import numpy as np
import uuid
import random

import sys
sys.path.append("../")

from config.config import ALL_POSITON, ALL_POSITON_LOW

class FootBaller:
    def __init__(self, name, age, now_year, main_position, injury_possibility, grow_position_type, recovery_power):
        # 選手固有の値
        self.uuid = uuid.uuid1()
        self.name = name
        self.age = age
        self.born_year = now_year-age
        self.grow_min_age = min(max(np.int8(np.round(np.random.normal(24, 1))), 22), 26)
        self.grow_old_age_1 = min(max(np.int8(np.round(np.random.normal(29, 1))), 27), 31)
        self.grow_old_age_2 = max(np.int8(np.round(np.random.normal(33, 1))), 32)
        self.main_position = main_position
        self.grow_position_type = grow_position_type
        self.injury_possibility = injury_possibility
        self.recovery_power = recovery_power

        # フラグ値
        self.retire = 0
        self.rental = 0
        self.register = 0
        self.index = None

        # 変化する値
        self.injury = 0
        self.contract = 0
        self.free_time = 0
        self.origin_team = None
        self.origin_team_name = ""
        self.b_team_count = 0

        # 能力値
        self.main_rate = None
        self.grow_type = random.choices(["legend", "genius", "general", "grass"], weights=[10, 60, 350, 580])[0]
        self.grow_exp_dict = {}
        self.position_all_rate = {}
        self.position_all_rate_sorted = []
        self.vitality = 100

        # 試合に関する値
        self.startup = 0
        self.partification = 0
        self.partification_position = None
        self.today_playing_time = 0
        self.today_goal = 0
        self.today_assist = 0
        self.today_rating = 0

        # 選手個人の結果
        self.result = {}
        self.history = {}        

    # 試合結果の計算
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

    def set_player_result(self, competition_name, year, kind):
        self.result[competition_name] = {}
        self.result[competition_name]["goal"] = 0
        self.result[competition_name]["assist"] = 0
        self.result[competition_name]["CS"] = 0
        self.result[competition_name]["試合数"] = 0
        self.result[competition_name]["年度"] = year
        self.result[competition_name]["分類"] = kind
        self.result[competition_name]["年齢"] = self.age
        self.result[competition_name]["怪我欠場"] = 0
        self.result[competition_name]["怪我回数"] = 0
        self.result[competition_name]["出場時間"] = 0
        self.result[competition_name]["合計評価点"] = 0
        self.result[competition_name]["MOM"] = 0
        self.result[competition_name]["ポジション"] = {}
        self.result[competition_name]["ポジション"][self.main_position] = 0
    
    def set_history(self, t_name, year):
        if self.rental == 1:
            self.history[year] = [t_name, self.origin_team_name]
        else:
            self.history[year] = [t_name]

    # 試合に関する変数のリセット
    def set_game_variable(self):
        self.today_goal = 0
        self.today_assist = 0
        self.today_playing_time = 0
        self.today_rating = 0

    def recovery_vitality(self, off=False):
        if off:
            self.vitality = 100
        else:
            self.vitality = min(self.vitality+self.recovery_power, 100)
    
    # 試合のレーティング計算
    def cal_rating(self, season_name, min_rate, max_rate, enemy_goal, result, all_time=90):
        random_rating = (self.position_all_rate[self.partification_position]-min_rate)/(max_rate-min_rate)*self.today_playing_time/all_time*min(np.random.normal(0.7, 0.2), 1.0)
        rating = 5.0+self.today_goal+self.today_assist*1.2+result+random_rating

        if self.partification_position in ["LB", "RB", "CB", "CDM", "GK"] and enemy_goal==0:
            rating += 1
        rating = min(rating, 10)
        self.today_rating = rating
        self.result[season_name]["合計評価点"] += rating

    # 引退するか否か決定する
    def consider_retirement(self, year):
        if self.retire!=1 and self.main_rate<85:
            rate = 0.00132*self.age*self.age - 1.18 + np.random.normal(0, 0.1) + self.injury_possibility
            if rate > np.random.rand():
                self.retire = 1
                self.history[year+1] = "Retire"
        
        if (self.free_time>1 and self.age>=26) or self.free_time>3:
            self.retire = 1
            self.history[year+1] = "Retire"

        self.age += 1

    # 再契約時の処理
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
        super().__init__(name, age, now_year, position, injury_possibility, grow_position_type, recovery_power)
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

class GK(FootBaller):
    def __init__(self, name, age, now_year, position, diving, 
                 handling, kicking, reflexes, 
                 speed, positioning, injury_possibility=0,
                 grow_position_type=None,
                 recovery_power=100):
        super().__init__(name, age, now_year, position, injury_possibility, grow_position_type, recovery_power)
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

class Create_player:
    def __init__(self, position_num, min_rate, max_rate, age_mean, df_name_list, 
                 mean_rate=75, now_year=1900):
        # 初期値
        self.position_num = position_num
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.mean_rate = mean_rate
        self.df_name_list = df_name_list
        self.age_mean = age_mean
        self.now_year = now_year

        # 変化値
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
                self.main_value = np.int8(np.round(np.random.normal(self.mean_rate, 3)))
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

            self.main_value = np.int8(np.round(np.random.normal(self.mean_rate, 3)))
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
                self.phy = np.int8(np.round(np.random.normal(self.main_value-30, 7)))

            elif pos == "RM":
                self.pac = np.int8(np.round(np.random.normal(70, 7)))
                self.sho = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.pas = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.dri = np.int8(np.round(np.random.normal(self.main_value, 1.5)))
                self.de = np.int8(np.round(np.random.normal(self.main_value-10, 7)))
                self.phy = np.int8(np.round(np.random.normal(self.main_value-25, 7)))

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
                self.phy = np.int8(np.round(np.random.normal(self.main_value-30, 7)))

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
    def print_player_data(self):
        print(self.name, '  Rate:', self.main_rate, '(', self.main_position, ')')
        print('-'*25)
        print('  DIV ', self.diving, '  REF ', self.reflexes)
        print('  HAN ', self.handling, '  SPE ', self.speed)
        print('  KIC ', self.kicking, '  POS ', self.positioning)
        print()

    
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
"""
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
