import pandas as pd
import random

import sys
sys.path.append("../")

from config.config import ALL_POSITON_LOW, ALL_POSITON_LOW_GK, BENCH_POSITION_NUM, POSITION_LOW_DICT

class Team:
    def __init__(self, name, formation, member_num=30):
        # 固定値
        self.name = name
        self.league_name = None
        self.member_num = member_num
        self.formation = formation

        # 所属選手
        self.affilation_players = None
        self.register_players = None
        self.not_register_players = None
        self.empty_position = {}

        # 結果
        self.result = pd.DataFrame(columns=['win', 'lose', 'row', '得点', '失点', '得失点差', 'Points', '順位', 'リーグ名'])
        self.competition_result = {}
        self.formation_rate = {}
        self.rank_point = 0
        self.rank_point_list = []
        self.before_rank = 0

        # 昇格降格変数
        self.relegation = 0
        self.promotion = 0
        self.league_state = "stay"

    def set_register_players(self, injury_level=100, change_register=True):
        for p in self.affilation_players:
            p.register = 0
        
        for key, players in self.formation.main_rate_formation.items():
            for p in players:
                p.register = 1

        for pos, num in BENCH_POSITION_NUM.items():
            not_register = [p for p in self.affilation_players if p.register==0 and p.injury<injury_level]
            not_register = sorted(not_register, key=lambda x:x.position_all_rate[pos], reverse=True)
            for p in not_register[:num]:
                p.register = 1
        
        if change_register:
            self.not_register_players = [p for p in self.affilation_players if p.register==0]
            self.register_players = [p for p in self.affilation_players if p.register==1]

    def set_onfield_players(self):
        self.formation.set_players_position()
        self.formation.set_main_rate_formation()
        self.formation.players_flat = []
        
        for p in self.affilation_players:
            p.index = 0
            p.partification = 0
            p.startup = 0
            p.position_all_rate_sorted = sorted(p.position_all_rate.items(), key=lambda x:x[1], reverse=True)
        
        remain_players = [p for p in self.register_players if p.injury<1 and p.vitality>=60]

        count = 0

        while True:
            # 5回繰り返しmain_rate_positionに選手が埋まっている場合にbreakする
            if count>5 and len([p for ps in list(self.formation.main_rate_formation.values()) for p in ps])==11:
                break
            # チームの人数が足りない
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
    def set_main_rate_position(self, injury_level=100):
        # injury_level:怪我をどれくらい許容するか
        self.formation.set_main_rate_formation()
        
        for p in self.affilation_players:
            p.index = 0
            p.position_all_rate_sorted = sorted(p.position_all_rate.items(), key=lambda x:x[1], reverse=True)
        
        remain_players = [p for p in self.affilation_players if p.injury<injury_level]
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
