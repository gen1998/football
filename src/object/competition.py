import uuid
import pandas as pd

import sys
sys.path.append("../")

from config.config import N
from src.object.game import Game

class Competition:
    def __init__(self, name, year, df_name_list):
        self.name = name
        self.uuid = uuid.uuid1()
        self.year = year

        self.now_round = 1
        self.max_round = None

        self.df_name_list = df_name_list
    
    def set_max_round(self, num_teams):
        for max_round in range(N):
            if num_teams <= pow(2, max_round):
                break
        self.max_round = max_round
    
    def play_1competition_section(self, competition_result):
        #lose_teams = []
        buff_teams = self.competition_teams.copy()
        if self.now_round==1:
            self.competition_teams = self.competition_teams[:(len(self.competition_teams)-pow(2, self.max_round-1))*2]

        for i in range(0, len(self.competition_teams), 2):
            game_team = self.competition_teams[i:i+2]
            if len(game_team) < 2:
                continue

            cup_game = Game(home=game_team[0], 
                            away=game_team[1], 
                            competition_name=self.name,
                            moment_num=24,
                            random_std=0.3,
                            pk=1)

            cup_game.battle(year=self.year,
                            kind="カップ戦",
                            df_name_list=self.df_name_list)

            if cup_game.result=="home" or cup_game.result=="home-pk":
                win = game_team[0]
                lose = game_team[1]
            else:
                win = game_team[1]
                lose = game_team[0]

            if self.max_round-3 >= self.now_round:
                round_name = f"{self.now_round}回戦"
                result_name = f"{self.now_round}回戦"
            elif self.max_round-2 == self.now_round:
                round_name = f"準々決勝"
                result_name = f"ベスト8"
            elif self.max_round-1 == self.now_round:
                round_name = f"準決勝"
                result_name = f"ベスト4"
            elif self.max_round == self.now_round:
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
            competition_result[self.name].loc[f"{game_team[0].name}-{game_team[1].name}"] = output
            lose.competition_result[self.name] = result_name
            #lose_teams.append(lose)
            buff_teams.remove(lose)
        self.now_round += 1

        #self.competition_teams = [t for t in self.competition_teams if t not in lose_teams]
        self.competition_teams = buff_teams
        if len(self.competition_teams)<2:
            win.competition_result[self.name] = "優勝"
            #self.competition_result_top.loc[self.name, ["年度", "優勝", "準優勝"]] = [year, f"{win.name}({win.league_name})", f"{lose.name}({lose.league_name})"]
            return competition_result, [self.year, f"{win.name}({win.league_name})", f"{lose.name}({lose.league_name})"]
        else:
            return competition_result, []