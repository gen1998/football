import pandas as pd
import random

import sys
sys.path.append("../")

from config.config import ALL_POSITON_LOW, ALL_POSITON_LOW_GK, BENCH_POSITION_NUM, POSITION_LOW_DICT, YOUNG_OLD
from src.object.player import Create_player

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
        self.rental_num = 0
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

    def set_onfield_players(self, year, mean_rate, df_name_list, competition_name, kind):
        self.formation.set_players_position()
        self.formation.set_main_rate_formation()
        self.formation.players_flat = []
        
        for p in self.affilation_players:
            p.index = 0
            p.partification = 0
            p.startup = 0
            p.position_all_rate_sorted = sorted(p.position_all_rate.items(), key=lambda x:x[1], reverse=True)
        
        remain_players = [p for p in self.register_players if p.injury<1 and p.vitality>=60]

        count = 1
        gk_flag = 0
        new_flag = 0

        while True:
            # 5回繰り返しmain_rate_positionに選手が埋まっている場合にbreakする
            if count>7 and len([p for ps in list(self.formation.main_rate_formation.values()) for p in ps])==11:
                break
            # チームの人数が足りない
            if count%10==0:
                if len(self.formation.main_rate_formation['GK']) < 1:
                    p_s = sorted([p for p in self.not_register_players if p.main_position=="GK"], key=lambda x:x.main_rate, reverse=True)
                    gk_flag = 1
                else:
                    p_s = sorted([p for p in self.not_register_players if p.main_position!="GK"], key=lambda x:x.main_rate, reverse=True)

                if len(p_s) == 0:
                    new_flag = 1
                    empty_position = {}
                    if gk_flag:
                        empty_position["GK"] = 1
                    else:
                        empty_position["CM"] = 1
                    Cp = Create_player(position_num=empty_position, 
                                        min_rate=40, max_rate=80, 
                                        age_mean=19,
                                        now_year=year,
                                        mean_rate=mean_rate,
                                        df_name_list=df_name_list)
                    Cp.create_teams(new=True)
                    p_s = Cp.players

                plus_player = p_s[0]

                # リーグ・試合準備
                plus_player.set_game_variable()
                plus_player.set_player_result(competition_name, year, kind)
                plus_player.recovery_vitality(off=True)
                plus_player.index = 0
                plus_player.partification = 0
                plus_player.partification_position = None
                plus_player.startup = 0
                plus_player.position_all_rate_sorted = sorted(plus_player.position_all_rate.items(), key=lambda x:x[1], reverse=True)

                remain_players.append(plus_player)
                self.register_players.append(plus_player)
                if new_flag==0:
                    self.not_register_players.remove(plus_player)
                else:
                    self.affilation_players.append(plus_player)
                
                new_flag = 0
                gk_flag = 0
            
            if count>200:
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
    def set_empty_position(self, limited_rate):
        self.empty_position = {}
        
        for pos, value in self.formation.main_rate_formation.items():
            for p in value:
                if p.position_all_rate[pos]<limited_rate:
                    if pos in self.empty_position.keys():
                        self.empty_position[pos] += 1
                    else:
                        self.empty_position[pos] = 1
        
        gk_num = len([p for p in self.affilation_players if p.main_position=="GK"])
        if gk_num>3:
            self.empty_position["GK"] = 0
    
    # ランダムなポジションを補強する
    def set_empty_position_random(self, num, num_gk):
        self.empty_position = {}

        if num_gk>0:
            self.empty_position["GK"] = num_gk
            num -= num_gk
        
        randon_position = random.choices(ALL_POSITON_LOW, k=num)

        for pos in randon_position:
            if pos in self.empty_position.keys():
                self.empty_position[pos] += 1
            else:
                self.empty_position[pos] = 1
    
    # empety_positionに沿った選手を移籍市場から獲得する
    def get_free_players_starting(self, free_players, league):
        count = 1
        sorted_num = 5
        league_min_rate = league.min_rate

        # 所属チームの強さ
        slope = -(league.max_starting_mean_rate-league.min_starting_mean_rate)/19
        intercept = (20*league.max_starting_mean_rate-league.min_starting_mean_rate-2)/19

        if self.league_state == "stay":
            max_rating = slope * self.before_rank + intercept
        elif self.league_state == "promotion":
            max_rating = slope * 18 + intercept
        elif self.league_state == "relegation":
            max_rating = slope * 3 + intercept
        
        self.check_duplication()

        # 現状の最適スタメンを決定する
        self.set_main_rate_position()
        self.set_empty_position((max_rating+league.min_starting_mean_rate)/2)
        _, sum_rate, _ = self.cal_formation_rate_num()
        empty_rate = (max_rating+league.min_starting_mean_rate)/2

        self.check_duplication()

        #print(sum_rate, max_rating*11)
        if sum_rate >= max_rating*11:
            return free_players

        # 順位ごとに合計レートが高くなりすぎないように
        # もうちょい考えましょう
        while True:
            new_players = []
            if count > 160:
                #raise Exception(f'{self.name}はチームを作成できません', league_min_rate, empty_rate, max_rating)
                break
            if count%10==0:
                league_min_rate = league.min_rate-2
            if count%50==0:
                empty_rate -= 5
                self.set_empty_position(empty_rate)
            for pos in self.empty_position.keys():
                num = self.empty_position[pos]
                new_players_pos = [p for p in free_players if p.main_position in POSITION_LOW_DICT[pos] and p.main_rate>=league_min_rate and p.main_rate<=league.max_rate]
                new_players_pos = sorted(new_players_pos, key=lambda x:x.main_rate, reverse=True)[:sorted_num]
                if len(new_players_pos)>=num:
                    new_players_pos = random.sample(new_players_pos, num)
                free_players = [p for p in free_players if p not in new_players_pos]
                new_players.extend(new_players_pos)
            
            self.affilation_players.extend(new_players)
            self.check_duplication()
            self.set_main_rate_position()
            num_p, sum_rate, _ = self.cal_formation_rate_num()
            #print(num_p, sum_rate, max_rating*11, sorted_num, self.empty_position)
            
            if sum_rate < max_rating*num_p:
                break
            else:
                self.affilation_players = [p for p in self.affilation_players if p not in new_players]
            
            count += 1
            sorted_num += 5
            free_players.extend(new_players)

            del new_players

        self.check_duplication()
        for p in new_players:
            p.set_contract()
        #print(len(new_players))
        free_players = [p for p in free_players if p not in new_players]
        self.check_duplication()

        return free_players

    def get_free_players_bench(self, free_players, league):
        count = 1
        sorted_num = 5

        # 現状の最適スタメンを決定する
        self.set_main_rate_position()

        # 所属チームの強さ
        slope = -(league.max_bench_mean_rate-league.min_bench_mean_rate)/19
        intercept = (20*league.max_bench_mean_rate-league.min_bench_mean_rate-2)/19

        if self.league_state == "stay":
            max_rating = slope * self.before_rank + intercept
        elif self.league_state == "promotion":
            max_rating = slope * 18 + intercept
        elif self.league_state == "relegation":
            max_rating = slope * 3 + intercept
        
        sum_rate, bench_players, bench_low_players, gk_num = self.cal_bench_rate_num(max_rating, league)
        self.set_empty_position_random(bench_low_players, gk_num)


        if sum_rate >= max_rating*league.bench_num:
            return free_players

        # 順位ごとに合計レートが高くなりすぎないように
        while True:
            new_players = []

            if count > 160:
                #raise Exception(f'{self.name}はチームを作成できません')
                break
            if count%50 == 0:
                max_rating -= 5
                sum_rate, bench_players, bench_low_players, gk_num = self.cal_bench_rate_num(max_rating, league)
                self.set_empty_position_random(bench_low_players, gk_num)
            for pos in self.empty_position.keys():
                num = self.empty_position[pos]
                new_players_pos = [p for p in free_players if p.main_position in POSITION_LOW_DICT[pos] and p.main_rate<=league.max_rate]
                new_players_pos = sorted(new_players_pos, key=lambda x:x.main_rate, reverse=True)[:sorted_num]
                if len(new_players_pos)>=num:
                    new_players_pos = random.sample(new_players_pos, num)
                free_players = [p for p in free_players if p not in new_players_pos]
                new_players.extend(new_players_pos)
            
            sum_rate = 0
            bench_players.extend(new_players)
            bench_players_ = sorted(bench_players, key=lambda x:x.main_rate, reverse=True)[:league.bench_num]
            for p in bench_players_:
                sum_rate += p.main_rate
            del bench_players_

            if sum_rate < max_rating*league.bench_num:
                break
            else:
                bench_players = [p for p in bench_players if p not in new_players]
            
            count += 1
            sorted_num += 5
            free_players.extend(new_players)

            del new_players

        for p in new_players:
            p.set_contract()
        self.affilation_players.extend(new_players)
        free_players = [p for p in free_players if p not in new_players]

        return free_players
    
    def cal_formation_rate_num(self):
        rate_sum = 0
        num = 0

        for pos, value in self.formation.main_rate_formation.items():
            for p in value:
                rate_sum+=p.position_all_rate[pos]
                num += 1
        
        if num==0:
            rate_mean = 0
        else:
            rate_mean = rate_sum/num
        return num, rate_sum, rate_mean
    
    def cal_bench_rate_num(self, max_rating, league):
        main_rate_position_flat = []
        for pos, value in self.formation.main_rate_formation.items():
            for p in value:
                main_rate_position_flat.append(p)
        bench_players = [p for p in self.affilation_players if p not in main_rate_position_flat]
        gk_num = max(1-len([p for p in bench_players if p.main_rate>=league.min_rate]), 0)
        bench_players = bench_players[:league.bench_num]

        rate_sum = 0

        for p in bench_players:
            rate_sum += p.main_rate

        bench_low_players = len([p for p in bench_players if p.main_rate <= (max_rating+league.min_rate)/2])
        #self.set_empty_position_random(bench_low_players, gk_num)

        return rate_sum, bench_players, bench_low_players, gk_num
    
    def check_duplication(self):
        if len(self.affilation_players) != len(set(self.affilation_players)):
            print(len(self.affilation_players), len(set(self.affilation_players)))
            raise("重複しています")
