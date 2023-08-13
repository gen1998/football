import uuid
import numpy as np
import pandas as pd

import sys
sys.path.append("../")

from src.object.game import Game
from src.utils import create_sections

def apply_points(row):
    return row.win*3+row.row

class Group_Stage:
    def __init__(self, name, year, group_num, g_team_num, df_name_list):
        self.name = name
        self.uuid = uuid.uuid1()
        self.year = year

        self.competition_teams = []
        self.group = {}
        self.group_result = {}
        self.group_num = group_num #groupの数
        self.g_team_num = g_team_num #1groupの人数
        self.sections = create_sections(num=self.g_team_num)
        self.sections_num = 0

        self.df_name_list = df_name_list

    def set_group_random(self):
        for gn in range(self.group_num):
            all_team_name = [t.name for t in self.competition_teams[gn*self.g_team_num:(gn+1)*self.g_team_num]]
            self.group[f"group_{gn}"] = [i for i in range(gn*self.g_team_num, (gn+1)*self.g_team_num)]
            output = pd.DataFrame(np.zeros((len(all_team_name), 5)), 
                                  index=all_team_name, 
                                  columns=["win", "lose", "row", "得点", "失点"], 
                                  dtype=np.int8)
            self.group_result[f"group_{gn}"] = output
    
    def cal_result(self, win_rank):
        win_teams = []
        for gn in range(self.group_num):
            self.group_result[f"group_{gn}"]["得失点差"] = self.group_result[f"group_{gn}"]["得点"]-self.group_result[f"group_{gn}"]["失点"]
            self.group_result[f"group_{gn}"]["Points"] = self.group_result[f"group_{gn}"].apply(apply_points, axis=1)
            self.group_result[f"group_{gn}"] = self.group_result[f"group_{gn}"].sort_values("得失点差", ascending=False)
            self.group_result[f"group_{gn}"] = self.group_result[f"group_{gn}"].sort_values("Points", ascending=False)

            win_team = list(self.group_result[f'group_{gn}'].index[:win_rank])
            win_teams.extend(win_team)
        
        self.competition_teams = [t for t in self.competition_teams if t.name in win_teams]
    
    def play_group_1section(self):
        sections = self.sections[:, self.sections_num]
        for gn in range(self.group_num):
            team_num = self.group[f"group_{gn}"]
            for sec in sections:
                home_team = self.competition_teams[team_num[sec[0]-1]]
                away_team = self.competition_teams[team_num[sec[1]-1]]

                game = Game(home=home_team, 
                            away=away_team,
                            competition_name=self.name,
                            moment_num=24,
                            random_std=0.3)
                game.battle(year=self.year,
                            kind="EU_杯",
                            df_name_list=self.df_name_list)

                if game.result=="home":
                    self.group_result[f"group_{gn}"].loc[home_team.name, "win"] += 1
                    self.group_result[f"group_{gn}"].loc[away_team.name, "lose"] += 1
                elif game.result=="away":
                    self.group_result[f"group_{gn}"].loc[away_team.name, "win"] += 1
                    self.group_result[f"group_{gn}"].loc[home_team.name, "lose"] += 1
                else:
                    self.group_result[f"group_{gn}"].loc[home_team.name, "row"] += 1
                    self.group_result[f"group_{gn}"].loc[away_team.name, "row"] += 1

                self.group_result[f"group_{gn}"].loc[home_team.name, "得点"] += game.home_goal
                self.group_result[f"group_{gn}"].loc[home_team.name, "失点"] += game.away_goal

                self.group_result[f"group_{gn}"].loc[away_team.name, "得点"] += game.away_goal
                self.group_result[f"group_{gn}"].loc[away_team.name, "失点"] += game.home_goal
        
        self.sections_num += 1


