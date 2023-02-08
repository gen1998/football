import numpy as np

import sys
sys.path.append("../")

from config.config import REPLACEMENT_MAX
from src.utils import cal_game_rating_rate

class Game:
    def __init__(self, home, away, competition_name=None, 
                 mid_influence_rate=0.5, gk_influence_rate=0.2, random_std=0.3, assist_rate=0.4,
                 moment_num=10, extra=0, pk=0):
        # 固定値
        self.home = home
        self.away = away

        # 試合寄与変数
        self.mid_influence_rate = mid_influence_rate
        self.gk_influence_rate = gk_influence_rate
        self.random_std = random_std
        self.moment_num = moment_num # 試合時間
        self.competition_name = competition_name
        self.assist_rate = assist_rate

        # 試合結果
        self.home_goal = 0
        self.away_goal = 0
        self.home_pk_goal = 0
        self.away_pk_goal = 0
        self.home_replacement = 0 # 交代枠
        self.away_replacement = 0
        self.now_time = 0
        self.result = None

        # 試合フラグ
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
        if np.random.rand()>self.assist_rate:
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
        
        home_attack = ((home_rate['ATT']+home_rate['MID']*self.mid_influence_rate)*home_ratio)/100
        away_attack = ((away_rate['ATT']+away_rate['MID']*self.mid_influence_rate)*away_ratio)/100
        
        home_defence = ((home_rate['DEF']+home_rate['MID']*self.mid_influence_rate)*home_ratio+home_rate["GK"]*self.gk_influence_rate)/100
        away_defence = ((away_rate['DEF']+away_rate['MID']*self.mid_influence_rate)*away_ratio+away_rate["GK"]*self.gk_influence_rate)/100
        
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

        # 怪我の経過を行う
        for p in [p for p in self.home.register_players if p.partification==0]:
            if p.injury>0:
                p.injury -= 1
                p.get_default(self.competition_name)
        
        for p in [p for p in self.away.register_players if p.partification==0]:
            if p.injury>0:
                p.injury -= 1
                p.get_default(self.competition_name)
        
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
