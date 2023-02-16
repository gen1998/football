import pandas as pd
import random
import time
from tqdm import tqdm

import sys
sys.path.append("../")

from src.utils import create_calender, parctice_player_result, self_study_player_result, set_rental_transfer
from src.object.player import Create_player
from config.config import YOUNG_OLD, LEAGUE_LEVEL_MAX

class Worldsoccer:
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
                
                #if day%10==0:
                    #c.set_register_member(injury_level=10)
        
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
                                    "リーグレベル":[10 for l in c.leagues for t in l.teams for p in t.not_register_players],
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
            for l in c.leagues:
                for t in l.teams:
                    t.league_state = "stay"

            for index in range(len(c.leagues)):
                season_name = f"{c.leagues[index].name}_{year}"
                if c.leagues[index].category!="top":
                    promotion = c.leagues[index].promotion[season_name]
                    promotion_team = [t for t in c.leagues[index].teams if t.name in promotion]
                    for t in promotion_team:
                        t.league_state = "promotion"
                    c.leagues[index].teams = [s for s in c.leagues[index].teams if s not in promotion_team]
                    c.leagues[index-1].teams.extend(promotion_team)

                if c.leagues[index].category!="lowest":
                    relegation = c.leagues[index].relegation[season_name]
                    relegation_team = [t for t in c.leagues[index].teams if t.name in relegation]
                    for t in relegation_team:
                        t.league_state = "relegation"
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
                #print(l.name)
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
                    rental_players = [p for p in t.affilation_players if p.main_rate<l.min_rate and p.age<YOUNG_OLD]
                    set_rental_transfer(rental_players, t)
                    self.free_players.extend(rental_players)
                    t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
                    rental_players_ = rental_players.copy()
                    t.rental_num = len(rental_players_)

                    t.check_duplication()
                    self.check_duplication()

                    #print(" ", t.name)
                    #print(" 所属人数：", len(t.affilation_players))
                    #print(" レンタル予定選手：", len(rental_players))
        
        print(" 引退人数   　: ", sum_retire_player)
        print(" 移籍市場人数 : ", len(self.free_players))
        print()
        
        random.shuffle(self.free_players)

        transfer_start = time.time()

        count = 0

        while True:
            if count>1:
                break
        
            for league_level in range(1, LEAGUE_LEVEL_MAX+1):
                #print(f"count{count}, league_level{league_level}")
                #print("-"*20)
                # 移籍市場からスタメン選手を入団させる
                for c in random.sample(self.country_leagues, len(self.country_leagues)):
                    for l in c.leagues:
                        if l.league_level==league_level:
                            for t in random.sample(l.teams, len(l.teams)):
                                #print(t.name)
                                t.check_duplication()
                                self.free_players = t.get_free_players_starting(self.free_players, l)
                                t.check_duplication()
                
                #print("starting finish")
            
                # 移籍市場からベンチ選手を入団させる
                for c in random.sample(self.country_leagues, len(self.country_leagues)):
                    for l in c.leagues:
                        if l.league_level==league_level:
                            for t in random.sample(l.teams, len(l.teams)):
                                self.free_players = t.get_free_players_bench(self.free_players, l)

                                young_player_num = max(0, t.member_num - len(t.affilation_players) - t.rental_num)
                                gk_num = min(3, len([p for p in t.affilation_players if p.main_position=="GK"]))
                                t.set_empty_position_random(young_player_num, 3-gk_num)

                                # 新しく選手を作成する
                                Cp = Create_player(position_num=t.empty_position, 
                                                    min_rate=40, max_rate=80, 
                                                    age_mean=19,
                                                    now_year=year,
                                                    mean_rate=l.mean_rate,
                                                    df_name_list=df_name_list)
                                
                                Cp.create_teams(new=True)
                                t.check_duplication()
                                new_players = Cp.players
                                t.affilation_players.extend(new_players)

                                t.set_main_rate_position()
                                t.set_register_players(change_register=False)

                                # 登録外の選手でレンタルにもならない選手を外に出す
                                # TODO:のちの修正ポイント
                                #print(f"affilation {len(t.affilation_players)}")
                                t.check_duplication()
                                out_players = [p for p in t.affilation_players if p.register==0 and p.age>=YOUNG_OLD]
                                for p in out_players:
                                    p.contract = 0
                                self.free_players.extend(out_players)
                                self.check_duplication()
                                t.affilation_players = [p for p in t.affilation_players if p not in out_players]

                                # メンバー外の若手をレンタルに
                                rental_players = [p for p in t.affilation_players if p.register==0 and p.age<YOUNG_OLD]
                                set_rental_transfer(rental_players, t)
                                self.free_players.extend(rental_players)
                                t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
                                rental_players_ = rental_players.copy()
                                t.rental_num += len(rental_players_)
                                #print(f"out {len(out_players)}, rental {len(rental_players)}")
                                #print(t.name, "bench")
                                self.check_duplication()
            count += 1   
        
        # 移籍市場からレンタル選手を元のチームに戻す
        rental_players = [p for p in self.free_players if p.rental==1]
        self.free_players = [p for p in self.free_players if p not in rental_players]

        for p in rental_players:
            #print(p, p.origin_team, p.origin_team_name)
            origin_team = p.origin_team
            p.rental = 0
            p.origin_team = None
            p.origin_team_name = ""
            origin_team.affilation_players.append(p)
        
        transfer_end = time.time()

        print(" 移籍市場経過時間 : {:.2f}秒".format(transfer_end-transfer_start))
        print(" 残留籍市場人数 : ", len(self.free_players))
        print()
    
    def check_duplication(self):
        if len(self.free_players) != len(set(self.free_players)):
            print(len(self.free_players), len(set(self.free_players)))
            raise("重複しています")
