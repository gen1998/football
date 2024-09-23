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

        self.players_result = pd.DataFrame()

        self.competition = None
        self.competition_name = competition_name
        #self.competition_teams = None
        self.competition_result = {}
        self.competition_result_top = pd.DataFrame(columns=["年度", "優勝", "準優勝"])

        self.df_name_list = df_name_list
    
    def set_competition(self, competition_name, year, leagues):
        self.competition.competition_teams=[]

        for l in leagues:
            if l.country_uuid==self.uuid:
                self.competition.competition_teams.extend(l.teams)
                l.set_player_result(competition_name, year, "カップ戦")
        
        self.competition.set_max_round(len(self.competition.competition_teams))
        random.shuffle(self.competition.competition_teams)
        output = pd.DataFrame(columns=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
        self.competition_result[competition_name] = output

    def play_holiday(self):
        for l in self.leagues:
            for t in l.teams:
                for p in t.register_players:
                    p.recovery_vitality(off=True)
    
    def prepare_1season(self, year, leagues):
        self.competition = Competition(name=f"{self.competition_name}_{year}",
                                       year=year,
                                       df_name_list=self.df_name_list)
        self.set_competition(self.competition.name, year, leagues)
                    
    def play_1competition_section(self):
        self.competition_result, t_result = self.competition.play_1competition_section(competition_result=self.competition_result)
        
        if len(t_result)>0:
            self.competition_result_top.loc[self.competition.name, ["年度", "優勝", "準優勝"]] = t_result

    def cal_players_result(self, year, leagues):
        all_output = pd.DataFrame()
        competition_name = f"{self.competition_name}_{year}"
        for l in leagues:
            league_rank = l.league_level
            for t in l.teams:
                # リーグ途中参戦の選手の結果を追加する
                for p in t.register_players:
                    if self.competition.name not in p.result.keys():
                        p.set_player_result(self.competition.name, year, "カップ戦")

                competition_result = [p.result[competition_name] for p in t.register_players]
                team_competition_result = t.competition_result[competition_name]

                output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                        "uuid":[p.uuid for p in t.register_players],
                                        "年齢":[result["年齢"] for result in competition_result],
                                        "Rate" : [p.main_rate for p in t.register_players],
                                        "E_Rate" : [p.evaluate_rate for p in t.register_players],
                                        "残契約":[p.contract-1 for p in t.register_players],
                                        "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in competition_result],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "リーグレベル":[l.league_level for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in competition_result],
                                        "国":[self.name for i in range(len(t.register_players))],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":[p.origin_team_name for p in t.register_players],
                                        "分類":[result["分類"] for result in competition_result],
                                        "順位" :  [team_competition_result for i in range(len(t.register_players))],
                                        "試合数":[result["試合数"] for result in competition_result],
                                        "出場時間":[result["出場時間"] for result in competition_result],
                                        "goal":[result["goal"] for result in competition_result],
                                        "assist":[result["assist"] for result in competition_result],
                                        "CS":[result["CS"] for result in competition_result],
                                        "評価点":[result["合計評価点"]/result["試合数"] if result["試合数"]>0 else 0 for result in competition_result],
                                        "MOM":[result["MOM"] for result in competition_result],
                                        "怪我欠場":[result["怪我欠場"] for result in competition_result],
                                        "怪我回数":[result["怪我回数"] for result in competition_result],
                                        "賞":["" for i in range(len(t.register_players))],
                                        "全ポジション回数":[json.dumps(result["ポジション"]) for result in competition_result],})
                all_output = pd.concat([all_output, output])
            
        # コンペティション最多得点
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[(all_output["分類"]=="カップ戦")]
        df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
        self.competition_result_top.loc[self.competition.name, "得点王"] = ""
        for index in df_search_index:
            all_output.loc[index, "賞"] += f"得点王({self.competition.name}),"
            self.competition_result_top.loc[self.competition.name, "得点王"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}({df_search.loc[index, 'リーグ']})), "  
        self.competition_result_top.loc[self.competition.name, "得点王"] += f"/  {df_search.loc[index, 'goal']}点"

        return all_output
