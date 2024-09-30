import pandas as pd
import random
import json

import sys
sys.path.append("../")

from config.config import N
from src.object.game import Game
from src.object.object import Object
from src.utils import search_empty_day

class Competition(Object):
    def __init__(self, name, year, country_uuid):
        super().__init__()
        self.name = name
        self.year = year
        self.country_uuid = country_uuid

        self.competition_teams_uuid = []
        self.origin_competition_teams_uuid = []
        self.competition_result = {}
        self.now_round = 1
        self.max_round = None
        self.before_day = 0
        self.interval = 0
    
    def set_max_round(self):
        num_teams = len(self.competition_teams_uuid)
        for max_round in range(N):
            if num_teams <= pow(2, max_round):
                break
        self.max_round = max_round
    
    def set_competition(self, teams_uuid, period=200):
        self.competition_teams_uuid = []
        self.competition_teams_uuid.extend(teams_uuid)
        self.set_max_round()
        self.interval = period//(self.max_round-1)
        random.shuffle(self.competition_teams_uuid)
        output = pd.DataFrame(columns=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
        self.competition_result[self.name] = output
    
    # 対戦日程作成
    def create_1season_calendar(self, calendar, now_day):
        if self.now_round == 1:
            game1_teams = self.competition_teams_uuid[:(len(self.competition_teams_uuid)-pow(2, self.max_round-1))*2]
            self.origin_competition_teams_uuid = self.competition_teams_uuid.copy()
        else:
            game1_teams = self.competition_teams_uuid.copy()
            now_day = self.before_day + self.interval

        random.shuffle(game1_teams)
        empty_days = []
        
        for index in range(0, len(game1_teams), 2):
            home = game1_teams[index]
            away = game1_teams[index+1]
            rest_interval = 3
            
            while True:
                empty_day = search_empty_day(calendar=calendar,
                                             home_uuid=home, away_uuid=away,
                                             now_day=now_day, rest_interval=rest_interval,
                                             deadline=20)
                if empty_day==-1:
                    rest_interval-=1
                else:
                    break
                
                if rest_interval == -1:
                    raise ValueError("日程生成ができません")

            calendar[empty_day][home] = [away, 1, "competition", self.uuid]
            calendar[empty_day][away] = [home, 1, "competition", self.uuid]
            empty_days.append(empty_day)
        
        # 今回戦の日にちを保存しておく
        self.before_day = int(min(empty_days))
        
        return calendar
    
    def play_1section(self, home, away):
        cup_game = Game(home=home, away=away, 
                        competition_name=self.name,
                        moment_num=24, random_std=0.3, pk=1)
        
        cup_game.battle(year=self.year,
                        kind="カップ戦")
        
        if cup_game.result=="home" or cup_game.result=="home-pk":
            win = home
            lose = away
        else:
            win = away
            lose = home

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

        output = pd.Series([f"{home.name}({home.league_name})", 
                            f"{away.name}({away.league_name})",
                            win.name, score, round_name], 
                            index=["チームA", "チームB", "勝利", "スコア", "ラウンド"])
        self.competition_result[self.name].loc[f"{home.name}-{away.name}"] = output
        lose.competition_result[self.name] = result_name
        self.competition_teams_uuid.remove(lose.uuid)
        
        if len(self.competition_teams_uuid) < 2:
            win.competition_result[self.name] = "優勝"
            t_result = [self.year, f"{win.name}({win.league_name})", f"{lose.name}({lose.league_name})"]
            return t_result
        elif len(self.competition_teams_uuid)==pow(2, self.max_round-self.now_round):
            self.now_round += 1
            return [0]
        else:
            return []
    
    def cal_players_result(self, year, teams, leagues, country):
        all_output = pd.DataFrame()
        for t in teams:
            # リーグ途中参戦の選手の結果を追加する
            for p in t.register_players:
                if self.name not in p.result.keys():
                    p.set_player_result(self.name, year, "カップ戦")

            league = [l for l in leagues if l.uuid==t.league_uuid][0]
            competition_result = [p.result[self.name] for p in t.register_players]
            team_competition_result = t.competition_result[self.name]

            output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                    "uuid":[p.uuid for p in t.register_players],
                                    "年齢":[result["年齢"] for result in competition_result],
                                    "Rate" : [p.main_rate for p in t.register_players],
                                    "E_Rate" : [p.evaluate_rate for p in t.register_players],
                                    "残契約":[p.contract-1 for p in t.register_players],
                                    "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in competition_result],
                                    "リーグ":[league.name for _ in range(len(t.register_players))],
                                    "リーグレベル":[league.league_level for _ in range(len(t.register_players))],
                                    "年度":[result["年度"] for result in competition_result],
                                    "国":[country.name for _ in range(len(t.register_players))],
                                    "チーム":[t.name for _ in range(len(t.register_players))],
                                    "レンタル元":[p.origin_team_name for p in t.register_players],
                                    "分類":[result["分類"] for result in competition_result],
                                    "順位" :[team_competition_result for _ in range(len(t.register_players))],
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

        result_txt = ""
        for index in df_search_index:
            all_output.loc[index, "賞"] += f"得点王({self.name}),"
            result_txt += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}({df_search.loc[index, 'リーグ']})), "  
        result_txt += f"/  {df_search.loc[index, 'goal']}点"

        return all_output, result_txt
