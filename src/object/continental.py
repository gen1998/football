import uuid
import math
import pandas as pd

import sys
sys.path.append("../")

from src.object.group_stage import Group_Stage
from src.object.competition import Competition

class Continental_Cup:
    def __init__(self, name, year, df_name_list):
        self.name = f"{name}_{year}"
        self.uuid = uuid.uuid1()
        self.year = year
        self.competition_teams = []

        self.group_stage = None
        self.group_sections = 0
        self.tournament_stage = None

        self.now_section = 0

        self.df_name_list = df_name_list
        self.result = {}

    def set_competition(self, group_num, g_team_num, t_team_num):
        self.group_stage = Group_Stage(name=self.name,
                                       year=self.year,
                                       group_num=group_num,
                                       g_team_num=g_team_num,
                                       df_name_list=self.df_name_list)
        self.group_stage.competition_teams = self.competition_teams
        self.group_stage.set_group_random()
        self.group_sections = math.comb(g_team_num, 2)

        self.tournament_stage = Competition(name=self.name,
                                            year=self.year,
                                            df_name_list=self.df_name_list)
        self.tournament_stage.set_max_round(num_teams=t_team_num)
        output = pd.DataFrame(columns=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
        self.result[self.name] = output
    
    def play_1section(self):
        if self.now_section == self.group_sections:
            self.group_stage.cal_result(win_rank=2)
            self.tournament_stage.competition_teams = self.group_stage.competition_teams

        if self.now_section < self.group_sections:
            self.group_stage.play_group_1section()
        
        if self.now_section >= self.group_sections:
            self.competition_result, t_result = self.tournament_stage.play_1competition_section(self.result)
        
        self.now_section += 1
