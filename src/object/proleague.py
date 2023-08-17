import pandas as pd
import numpy as np
import json
import random

import sys
sys.path.append("../")

from config.config import BEST_ELEVEN_LIST
from src.object.game import Game
from src.object.competition import Competition

class ProLeague:
    def __init__(self, name, leagues, df_name_list, competition_name=None):
        self.name = name
        self.leagues = leagues

        self.players_result = pd.DataFrame()

        self.competition = None
        self.competition_name = competition_name
        #self.competition_teams = None
        self.competition_result = {}
        self.competition_result_top = pd.DataFrame(columns=["年度", "優勝", "準優勝"])

        self.df_name_list = df_name_list
    
    def set_competition(self, competition_name, year):
        self.competition.competition_teams=[]

        for l in self.leagues:
            self.competition.competition_teams.extend(l.teams)
            l.set_player_result(competition_name, year, "カップ戦")
        
        self.competition.set_max_round(len(self.competition.competition_teams))
        random.shuffle(self.competition.competition_teams)
        output = pd.DataFrame(columns=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
        self.competition_result[competition_name] = output
    
    def set_players_partification(self):
        for l in self.leagues:
            for t in l.teams:
                for p in t.affilation_players:
                    p.partification = 0
                    p.partification_position = None
    
    def set_register_member(self, injury_level=100):
        for l in self.leagues:
            for t in l.teams:
                t.set_main_rate_position(injury_level=injury_level)
                t.set_register_players(injury_level=injury_level)

    def play_holiday(self):
        for l in self.leagues:
            for t in l.teams:
                for p in t.register_players:
                    p.recovery_vitality(off=True)
    
    def prepare_1season(self, year):
        self.competition = Competition(name=f"{self.competition_name}_{year}",
                                       year=year,
                                       df_name_list=self.df_name_list)
        self.set_competition(self.competition.name, year)
        self.set_players_partification()
        self.set_register_member(injury_level=100)
        
        # 必要変数をセッティング
        for l in self.leagues:
            l.set_team_leaguename()
            season_name = f'{l.name}_{year}'
            l.set_player_result(season_name, year, "リーグ")
            l.set_team_result(season_name)
                    
    def play_1competition_section(self):
        self.competition_result, t_result = self.competition.play_1competition_section(competition_result=self.competition_result)
        
        if len(t_result)>0:
            self.competition_result_top.loc[self.competition.name, ["年度", "優勝", "準優勝"]] = t_result

    def cal_players_result(self, year):
        all_output = pd.DataFrame()
        for l in self.leagues:
            season_name = f'{l.name}_{year}'
            league_rank = l.team_result[season_name].index.tolist()
            for t in l.teams:
                # リーグ途中参戦の選手の結果を追加する
                for p in t.register_players:
                    if self.competition.name not in p.result.keys():
                        p.set_player_result(self.competition.name, year, "カップ戦")

                t.formation_rate[season_name] = t.formation.team_rate
                season_result = [p.result[season_name] for p in t.register_players]
                competition_result = [p.result[self.competition.name] for p in t.register_players]

                output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                        "uuid":[p.uuid for p in t.register_players],
                                        "年齢":[result["年齢"] for result in season_result],
                                        "Rate" : [p.main_rate for p in t.register_players],
                                        "残契約":[p.contract-1 for p in t.register_players],
                                        "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in season_result],
                                        "国":[self.name for i in range(len(t.register_players))],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "リーグレベル":[l.league_level for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in season_result],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":[p.origin_team_name for p in t.register_players],
                                        "分類":[result["分類"] for result in season_result],
                                        "順位" :  [f"{league_rank.index(t.name)+1}位" for i in range(len(t.register_players))],
                                        "試合数":[result["試合数"] for result in season_result],
                                        "出場時間":[result["出場時間"] for result in season_result],
                                        "goal":[result["goal"] for result in season_result],
                                        "assist":[result["assist"] for result in season_result],
                                        "CS":[result["CS"] for result in season_result],
                                        "評価点":[result["合計評価点"]/result["試合数"] if result["試合数"]>0 else 0 for result in season_result],
                                        "MOM":[result["MOM"] for result in season_result],
                                        "怪我欠場":[result["怪我欠場"] for result in season_result],
                                        "怪我回数":[result["怪我回数"] for result in season_result],
                                        "賞":["" for i in range(len(t.register_players))],
                                        "全ポジション回数":[json.dumps(result["ポジション"]) for result in season_result],})
                all_output = pd.concat([all_output, output])

                output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                        "uuid":[p.uuid for p in t.register_players],
                                        "年齢":[result["年齢"] for result in competition_result],
                                        "Rate" : [p.main_rate for p in t.register_players],
                                        "残契約":[p.contract-1 for p in t.register_players],
                                        "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in competition_result],
                                        "リーグ":[l.name for i in range(len(t.register_players))],
                                        "リーグレベル":[l.league_level for i in range(len(t.register_players))],
                                        "年度":[result["年度"] for result in competition_result],
                                        "国":[self.name for i in range(len(t.register_players))],
                                        "チーム":[t.name for i in range(len(t.register_players))],
                                        "レンタル元":[p.origin_team_name for p in t.register_players],
                                        "分類":[result["分類"] for result in competition_result],
                                        "順位" :  [f"{league_rank.index(t.name)+1}位" for i in range(len(t.register_players))],
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

                for p in t.register_players:
                    season_result = p.result[season_name]
                    competition_result = p.result[self.competition.name]
                    p.contract -= 1

                    # 再契約する処理
                    if p.contract == 0 and np.random.rand()<p.result[season_name]["出場時間"]*0.6/3420 and p.rental!=1:
                        p.set_contract()
                    
                    # 試合に出てない人を戦力外にする処理
                    if p.partification_position is None and p.rental!=1:
                        if p.main_position!="GK":
                            p.contract = 0
                        else:
                            if np.random.rand()<0.6:
                                p.contract = 0
                    
                    # 成長
                    #p.grow_up((season_result["出場時間"]+competition_result["出場時間"])/90)
                    p.grow_up((season_result["試合数"]+competition_result["試合数"]))
                    if p.main_position != "GK":
                        p.select_main_position()
                    else:
                        p.main_rate = p.cal_rate()
                    p.cal_all_rate()

                    # offseason分怪我を経過させる
                    p.injury = max(p.injury-10, 0)

                    # 引退
                    p.consider_retirement(year)

            #リーグ最多得点
            all_output = all_output.reset_index(drop=True)
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name))]
            df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
            l.champion.loc[season_name, "得点王"] = ""
            for index in df_search_index:
                all_output.loc[index, "賞"] += f"得点王({season_name}),"
                l.champion.loc[season_name, "得点王"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            l.champion.loc[season_name, "得点王"] += f"  /  {df_search.loc[index, 'goal']}点"

            #リーグMVP
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.7))]
            df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
            l.champion.loc[season_name, "MVP"] = ""
            for index in df_search_index[:1]:
                all_output.loc[index, "賞"] += f"MVP({season_name}),"
                l.champion.loc[season_name, "MVP"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            
            #若手MVP
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.5)&(all_output["年齢"]<24))]
            df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
            l.champion.loc[season_name, "yMVP"] = ""
            for index in df_search_index[:1]:
                all_output.loc[index, "賞"] += f"yMVP({season_name}),"
                l.champion.loc[season_name, "yMVP"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            
            #GK_MVP
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.7))]
            df_search = df_search[df_search["ポジション"]=="GK"]
            df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
            l.champion.loc[season_name, "ベストGK"] = ""
            for index in df_search_index[:1]:
                all_output.loc[index, "賞"] += f"ベストGK({season_name}),"
                l.champion.loc[season_name, "ベストGK"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "
            
            #ベストイレブン
            df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["リーグ"]==l.name)&(all_output["出場時間"]>(l.num-1)*2*90*0.7))]
            for position, num in BEST_ELEVEN_LIST:
                df_search_index = df_search[df_search["ポジション"].isin(position)].sort_values("評価点", ascending=False).index.tolist()[:num]
                for index in df_search_index:
                    all_output.loc[index, "賞"] += f"ベストイレブン({season_name}),"
        
        # コンペティション最多得点
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[(all_output["分類"]=="カップ戦")]
        df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
        self.competition_result_top.loc[self.competition.name, "得点王"] = ""
        for index in df_search_index:
            all_output.loc[index, "賞"] += f"得点王({self.competition.name}),"
            self.competition_result_top.loc[self.competition.name, "得点王"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}({df_search.loc[index, 'リーグ']})), "  
        self.competition_result_top.loc[self.competition.name, "得点王"] += f"/  {df_search.loc[index, 'goal']}点"

        self.players_result = pd.concat([self.players_result, all_output])
        self.players_result = self.players_result.reset_index(drop=True)

        return self.players_result[((self.players_result["リーグレベル"]==1)&(self.players_result["出場時間"]>(self.leagues[0].num-1)*2*90*0.7)&(self.players_result["年度"]==year))]
