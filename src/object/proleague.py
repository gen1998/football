import pandas as pd
import random
import json

import sys
sys.path.append("../")

from src.object.competition import Competition
from src.object.object import Object

class ProLeague(Object):
    def __init__(self, name, leagues, df_name_list, competition_name=None):
        super().__init__()
        self.name = name
        self.leagues = leagues

        self.competition_name = competition_name
        self.competition_result = {}
        self.competition_result_top = pd.DataFrame(columns=["年度", "優勝", "準優勝"])

        self.df_name_list = df_name_list        
    
    def prepare_competition(self, year):
        if self.competition_name is None:
            return -1
        else:
            competition = Competition(name=f"{self.competition_name}_{year}",
                                      year=year, country_uuid=self.uuid,
                                      df_name_list=self.df_name_list)
            return competition

    def cal_players_result(self, competition, result_text):
        self.competition_result_top.loc[competition.name, "得点王"] = result_text 
        self.competition_result[competition.name] = competition.competition_result[competition.name]
