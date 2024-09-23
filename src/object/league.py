import pandas as pd
import numpy as np
import json

import sys
sys.path.append("../")

from src.object.game import Game
from src.object.object import Object
from config.config import BEST_ELEVEN_LIST

def apply_points(row):
    return row.win*3+row.row

class League(Object):
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
        super().__init__()
        self.name = name
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
        
        # 接続
        self.country_uuid = None
        self.upperleague_uuid = None
        self.lowerleague_uuid = None

        # 結果
        self.team_result = {}
        self.player_result = {}
        self.teams_record = {}
        self.all_record = {}
        self.player_record = {}
        self.player_all_record = {}
        self.set_record_keys()
        self.champion = pd.DataFrame(columns=["優勝", "得点王", "MVP", "yMVP", "ベストGK"])
        
        # 昇格降格チーム
        self.relegation = {}
        self.relegation_num = relegation_num
        self.promotion = {}
        self.promotion_num = promotion_num

        self.df_name_list = df_name_list
        self.set_team_leaguename()
    
    def set_record_keys(self):
        self.teams_record["champions"] = {}
        self.teams_record["promotion"] = {}
        self.teams_record["relegation"] = {}

        record_name = ["最多タイトル", "最多連覇", "最多勝ち点", "最小勝ち点", "最多勝利", "最小勝利", "最多敗戦", "最小敗戦", "最多得点", "最小得点", "最多失点", "最小失点"]
        for n in record_name:
            if "最多" in n:
                self.all_record[n] = [-1, []]
            else:
                self.all_record[n] = [10000, []]
        
        self.player_record["MVP"] = {}
        self.player_record["yMVP"] = {}
        self.player_record["得点王"] = {}
        self.player_record["ベストイレブン"] = {}
        self.player_record["ベストGK"] = {}

        record_name = ["最多MVP", "最多yMVP", "最多得点王", "最多ベストイレブン", "最多ベストGK", "最多ゴール", "最多アシスト", "最多CS", "最多MOM", "最高評点"]

        for n in record_name:
            self.all_record[n] = [-1, []]

    
    def set_team_leaguename(self):
        for t in self.teams:
            t.league_name = self.name
    
    def set_player_result(self, competition_name, year, kind):
        for t in self.teams:
            for p in t.affilation_players:
                p.set_player_result(competition_name, year, kind)
                p.set_history(t.name, year)
                p.recovery_vitality(off=True)
    
    def set_team_result(self, season_name):
        all_team_name = [s.name for s in self.teams]
        output = pd.DataFrame(np.zeros((len(all_team_name), 5)), 
                              index=all_team_name, 
                              columns=["win", "lose", "row", "得点", "失点"], 
                              dtype=np.int8)
        self.team_result[season_name] = output
    
    def cal_team_rank(self, year):
        season_name = f'{self.name}_{year}'
        
        self.team_result[season_name]["得失点差"] = self.team_result[season_name]["得点"]-self.team_result[season_name]["失点"]
        self.team_result[season_name]["Points"] = self.team_result[season_name].apply(apply_points, axis=1)
        self.team_result[season_name] = self.team_result[season_name].sort_values("得失点差", ascending=False)
        self.team_result[season_name] = self.team_result[season_name].sort_values("Points", ascending=False)
        self.team_result[season_name]["順位"] = [i for i in range(1, self.num+1)]
        self.team_result[season_name]["リーグ名"] = [f"{self.name}" for _ in range(self.num)]
    
    def cal_1year_result(self, year):
        season_name = f'{self.name}_{year}'
        self.cal_team_rank(year)
        
        for team in self.teams:
            team.result.loc[season_name] = self.team_result[season_name].loc[team.name, :]
            team.rank_point += int(self.team_result[season_name].loc[team.name, "順位"]+(self.league_level-1)*20)
            team.rank_point_list.append(team.rank_point)
            team.before_rank = int(self.team_result[season_name].loc[team.name, "順位"])
        
        win_name = list(self.team_result[season_name].index)[0]
        self.champion.loc[season_name, "優勝"] = win_name
        if win_name in self.teams_record["champions"].keys():
            self.teams_record["champions"][win_name] += 1
        else:
            self.teams_record["champions"][win_name] = 1
        
        # 昇格決定
        if self.category!="top":
            promotion_teams = list(self.team_result[season_name][:self.promotion_num].index)
            self.promotion[season_name] = promotion_teams

            for t in promotion_teams:
                if t in self.teams_record["promotion"].keys():
                    self.teams_record["promotion"][t] += 1
                else:
                    self.teams_record["promotion"][t] = 1
        
        #降格決定
        if self.category!="lowest":
            relegation_teams = list(self.team_result[season_name][-self.relegation_num:].index)
            self.relegation[season_name] = relegation_teams

            for t in relegation_teams:
                if t in self.teams_record["relegation"].keys():
                    self.teams_record["relegation"][t] += 1
                else:
                    self.teams_record["relegation"][t] = 1
        
        self.cal_leagure_record(season_name, year)
        
    def play_1section(self, year, sections):
        season_name = f'{self.name}_{year}'
        
        for section in sections:            
            game = Game(home=self.teams[section[0]-1], 
                        away=self.teams[section[1]-1],
                        competition_name=season_name,
                        moment_num=24,
                        random_std=0.3)
            game.battle(year=year,
                        kind="リーグ",
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
    
    def cal_leagure_record(self, season_name, year):
        champions = [kv for kv in self.teams_record["champions"].items() if kv[1] == max(self.teams_record["champions"].values())]
        b_r = self.all_record["最多タイトル"][0]
        b_t = self.all_record["最多タイトル"][1]
        for c in champions:
            if c[1] == b_r:
                if c[0] not in b_t:
                    self.all_record["最多タイトル"][1].append(c[0])
            elif c[1] > b_r:
                self.all_record["最多タイトル"][0] = c[1]
                self.all_record["最多タイトル"][1] = [c[0]]
    
        record_names = ["最多勝ち点", "最小勝ち点", "最多勝利", "最小勝利", "最多敗戦", "最小敗戦", "最多得点", "最小得点", "最多失点", "最小失点"]
        result_names = ["Points", "Points", "win", "win", "lose", "lose", "得点", "得点", "失点", "失点",]

        for rec_n, res_n in zip(record_names, result_names):
            if "多" in rec_n:
                self.cal_1record_league(year, season_name, rec_n, res_n)
            else:
                self.cal_1record_league(year, season_name, rec_n, res_n, max_=False)

    def cal_1record_league(self, year, season_name, record_name, result_name, max_=True):
        df = self.team_result[season_name]

        if max_:
            d_r = df[result_name].max()
            d_t = df.loc[df[result_name] == df[result_name].max(), :].index.tolist() 
        else:
            d_r = df[result_name].min()
            d_t = df.loc[df[result_name] == df[result_name].min(), :].index.tolist() 

        b_r = self.all_record[record_name][0]
        b_t = self.all_record[record_name][1]
        for index, t in enumerate(d_t):
            if d_r == b_r:
                if d_t not in b_t:
                    self.all_record[record_name][1].append(f"{t}({year})")
            elif d_r > b_r and max_:
                if index == 0:
                    self.all_record[record_name][0] = d_r
                    self.all_record[record_name][1] = [f"{t}({year})"]
                else:
                    self.all_record[record_name][1].append(f"{t}({year})")
            elif d_r < b_r and not max_:
                if index == 0:
                    self.all_record[record_name][0] = d_r
                    self.all_record[record_name][1] = [f"{t}({year})"]
                else:
                    self.all_record[record_name][1].append(f"{t}({year})")
    
    def cal_1record_player(self, year, player_name, uuid_name, index, 
                           record_name="", record_name_max="", value=-1, value_record_name=""):
        # リーグ記録保存
        if record_name != "":
            if uuid_name in self.player_record[record_name].keys():
                self.player_record[record_name][uuid_name] += 1
            else:
                self.player_record[record_name][uuid_name] = 1
            
            champions = [kv for kv in self.player_record[record_name].items() if kv[1] == max(self.player_record[record_name].values())]
            b_r = self.all_record[record_name_max][0]
            b_t = self.all_record[record_name_max][1]
            for c in champions:
                if c[1] == b_r:
                    if c[0] not in b_t:
                        self.all_record[record_name_max][1].append(c[0])
                elif c[1] > b_r:
                    self.all_record[record_name_max][0] = c[1]
                    self.all_record[record_name_max][1] = [c[0]]
        
        if value > -1:
            b_r = self.all_record[value_record_name][0]
            if value == b_r:
                self.all_record[value_record_name][1].append(f"{player_name}({year})")
            elif value > b_r:
                if index == 0:
                    self.all_record[value_record_name][0] = value
                    self.all_record[value_record_name][1] = [f"{player_name}({year})"]
                else:
                    self.all_record[value_record_name][1].append(f"{player_name}({year})")
    
    def cal_players_result(self, year, country_name, competition_name):
        all_output = pd.DataFrame()
        season_name = f'{self.name}_{year}'
        league_rank = self.team_result[season_name].index.tolist()
        for t in self.teams:
            # リーグ途中参戦の選手の結果を追加する
            for p in t.register_players:
                if competition_name not in p.result.keys():
                    p.set_player_result(competition_name, year, "カップ戦")

            t.formation_rate[season_name] = t.formation.team_rate
            season_result = [p.result[season_name] for p in t.register_players]
            competition_result = [p.result[competition_name] for p in t.register_players]

            output = pd.DataFrame({"名前":[p.name for p in t.register_players],
                                    "uuid":[p.uuid for p in t.register_players],
                                    "年齢":[result["年齢"] for result in season_result],
                                    "Rate" : [p.main_rate for p in t.register_players],
                                    "E_Rate" : [p.evaluate_rate for p in t.register_players],
                                    "残契約":[p.contract-1 for p in t.register_players],
                                    "ポジション":[sorted(result["ポジション"].items(), key=lambda x:x[1], reverse=True)[0][0] for result in season_result],
                                    "国":[country_name for i in range(len(t.register_players))],
                                    "リーグ":[self.name for i in range(len(t.register_players))],
                                    "リーグレベル":[self.league_level for i in range(len(t.register_players))],
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

            for p in t.register_players:
                season_result = p.result[season_name]
                competition_result = p.result[competition_name]
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
                p.cal_evaluate_rate(season_name, competition_name, self.league_level)
                p.cal_all_rate()

                # offseason分怪我を経過させる
                p.injury = max(p.injury-10, 0)

                # 引退
                p.consider_retirement(year)

        #リーグ最多得点
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[all_output["分類"]=="リーグ"]
        df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
        self.champion.loc[season_name, "得点王"] = ""
        b_goal = df_search["goal"].max()
        for j, index in enumerate(df_search_index):
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{p_name}_{df_search.loc[index, 'uuid']}"
            all_output.loc[index, "賞"] += f"得点王({season_name}),"
            self.champion.loc[season_name, "得点王"] += f"{p_name}({df_search.loc[index, 'チーム']}), "

            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    record_name="得点王", record_name_max="最多得点王",
                                    value=b_goal, value_record_name="最多ゴール")

        self.champion.loc[season_name, "得点王"] += f"  /  {b_goal}点"

        #リーグ最多アシスト
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[all_output["分類"]=="リーグ"]
        df_search_index = df_search.loc[df_search["assist"]==df_search["assist"].max(), :].index.tolist()
        b_assist = df_search["assist"].max()
        for j, index in enumerate(df_search_index):
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{p_name}_{df_search.loc[index, 'uuid']}"

            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    value=b_assist, value_record_name="最多アシスト")
        
        #リーグ最多CS
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[all_output["分類"]=="リーグ"]
        df_search_index = df_search.loc[df_search["CS"]==df_search["CS"].max(), :].index.tolist()
        b_assist = df_search["CS"].max()
        for j, index in enumerate(df_search_index):
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{p_name}_{df_search.loc[index, 'uuid']}"

            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    value=b_assist, value_record_name="最多CS")
        
        #リーグ最多アシスト
        all_output = all_output.reset_index(drop=True)
        df_search = all_output[all_output["分類"]=="リーグ"]
        df_search_index = df_search.loc[df_search["MOM"]==df_search["MOM"].max(), :].index.tolist()
        b_assist = df_search["MOM"].max()
        for j, index in enumerate(df_search_index):
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{p_name}_{df_search.loc[index, 'uuid']}"

            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    value=b_assist, value_record_name="最多MOM")

        #リーグMVP
        df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["出場時間"]>(self.num-1)*2*90*0.8)&(all_output["試合数"]>(self.num-1)*2*0.85))]
        df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
        self.champion.loc[season_name, "MVP"] = ""
        b_value = df_search["評価点"].max()
        for index in df_search_index[:1]:
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{df_search.loc[index, '名前']}_{df_search.loc[index, 'uuid']}"
            all_output.loc[index, "賞"] += f"MVP({season_name}),"
            self.champion.loc[season_name, "MVP"] += f"{p_name}({df_search.loc[index, 'チーム']}), "

            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    record_name="MVP", record_name_max="最多MVP",
                                    value=b_value, value_record_name="最高評点")
        
        #若手MVP
        df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["出場時間"]>(self.num-1)*2*90*0.5)&(all_output["年齢"]<24))]
        df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
        self.champion.loc[season_name, "yMVP"] = ""
        for index in df_search_index[:1]:
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{df_search.loc[index, '名前']}_{df_search.loc[index, 'uuid']}"
            all_output.loc[index, "賞"] += f"yMVP({season_name}),"
            self.champion.loc[season_name, "yMVP"] += f"{p_name}({df_search.loc[index, 'チーム']}), "
            
            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    record_name="yMVP", record_name_max="最多yMVP")
        
        #GK_MVP
        df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["出場時間"]>(self.num-1)*2*90*0.8)&(all_output["試合数"]>(self.num-1)*2*0.9))]
        df_search = df_search[df_search["ポジション"]=="GK"]
        df_search_index = df_search.loc[df_search["評価点"]==df_search["評価点"].max(), :].index.tolist()
        self.champion.loc[season_name, "ベストGK"] = ""
        for index in df_search_index[:1]:
            p_name = df_search.loc[index, '名前']
            uuid_name = f"{df_search.loc[index, '名前']}_{df_search.loc[index, 'uuid']}"
            all_output.loc[index, "賞"] += f"ベストGK({season_name}),"
            self.champion.loc[season_name, "ベストGK"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}), "

            # リーグ記録保存
            self.cal_1record_player(year, p_name, uuid_name, j,
                                    record_name="ベストGK", record_name_max="最多ベストGK")
        
        #ベストイレブン
        df_search = all_output[((all_output["分類"]=="リーグ")&(all_output["出場時間"]>(self.num-1)*2*90*0.8)&(all_output["試合数"]>(self.num-1)*2*0.85))]
        for position, num in BEST_ELEVEN_LIST:
            df_search_index = df_search[df_search["ポジション"].isin(position)].sort_values("評価点", ascending=False).index.tolist()[:num]
            for index in df_search_index:
                p_name = df_search.loc[index, '名前']
                uuid_name = f"{df_search.loc[index, '名前']}_{df_search.loc[index, 'uuid']}"
                all_output.loc[index, "賞"] += f"ベストイレブン({season_name}),"

                # リーグ記録保存
                self.cal_1record_player(year, p_name, uuid_name, j,
                                        record_name="ベストイレブン", record_name_max="最多ベストイレブン")
        
        all_output = all_output.reset_index(drop=True)
        
        return all_output
    
    # コンペティション最多得点
    
    """
    df_search = all_output[(all_output["分類"]=="カップ戦")]
    df_search_index = df_search.loc[df_search["goal"]==df_search["goal"].max(), :].index.tolist()
    competition_result_top.loc[competition_name, "得点王"] = ""
    for index in df_search_index:
        all_output.loc[index, "賞"] += f"得点王({competition_name}),"
        competition_result_top.loc[competition_name, "得点王"] += f"{df_search.loc[index, '名前']}({df_search.loc[index, 'チーム']}({df_search.loc[index, 'リーグ']})), "  
    competition_result_top.loc[competition_name, "得点王"] += f"/  {df_search.loc[index, 'goal']}点"

    players_result = pd.concat([players_result, all_output])
    players_result = players_result.reset_index(drop=True)

    return players_result[((players_result["リーグレベル"]==1)&(players_result["出場時間"]>19*2*90*0.8)&(players_result["年度"]==year)&(players_result["試合数"]>(self.num-1)*2*0.85))]
    """
