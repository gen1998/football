import pandas as pd
import numpy as np

import uuid

import sys
sys.path.append("../")

from src.object.game import Game

def apply_points(row):
    return row.win*3+row.row

class League:
    def __init__(self, name, teams, num, category, league_level,
                 df_name_list,
                 relegation_num=0, promotion_num=0, 
                 min_rate=75, max_rate=85, mean_rate=80,
                 min_starting_mean_rate=73,
                 max_starting_mean_rate=99,
                 min_bench_mean_rate=75,
                 max_bench_mean_rate=80,
                 bench_num=8):
        # 固定値
        self.name = name
        self.uuid = uuid.uuid1()
        self.teams = teams
        self.num = num
        self.bench_num = bench_num
        self.category = category
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.mean_rate = mean_rate
        self.min_starting_mean_rate = min_starting_mean_rate
        self.max_starting_mean_rate = max_starting_mean_rate
        self.min_bench_mean_rate = min_bench_mean_rate
        self.max_bench_mean_rate = max_bench_mean_rate
        self.league_level = league_level
        self.sections = None

        # 結果
        self.team_result = {}
        self.player_result = {}
        self.champion = pd.DataFrame(columns=["優勝", "得点王", "MVP", "yMVP", "ベストGK"])
        
        # 昇格降格チーム
        self.relegation = {}
        self.relegation_num = relegation_num
        self.promotion = {}
        self.promotion_num = promotion_num

        self.df_name_list = df_name_list
        self.set_team_leaguename()
    
    def set_team_leaguename(self):
        for t in self.teams:
            t.league_name = self.name
    
    def set_player_result(self, competition_name, year, kind):
        for t in self.teams:
            for p in t.affilation_players:
                p.set_player_result(competition_name, year, kind)
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
            team.before_rank = int(self.team_result[season_name].loc[team.name, "順位"])
        
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
            game = Game(home=self.teams[section[0]-1], 
                        away=self.teams[section[1]-1],
                        competition_name=season_name,
                        moment_num=24,
                        random_std=0.3)
            game.battle(year=year,
                        kind="リーグ戦",
                        df_name_list=self.df_name_list)

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