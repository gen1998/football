import pandas as pd
import random
import time
from tqdm import tqdm

import sys
sys.path.append("../")

from src.utils import set_rental_transfer, create_sections_calendar
from src.object.player import Create_player
from config.config import YOUNG_OLD, LEAGUE_LEVEL_MAX, ONE_YEAR_DAYS

class Worldsoccer:
    def __init__(self, country_leagues, continental_cups_dict={"CL":32}):
        self.country_leagues = country_leagues

        self.period = 300
        self.interval = 7
        self.international_games = 0 # CL, EL, ECL, ACLなど国際カップ戦の試合数

        self.continental_cups_dict = continental_cups_dict
        self.continental_cups = {}

        self.players_result = pd.DataFrame()

        self.all_countries = []
        self.all_leagues = []
        self.all_teams = []
        self.all_active_players = []
        self.all_competitions = []
        self.record_competitions = []
        self.free_players = []
        self.retire_players = []
        
        self.debug_calendar = None
        
        self._set()
    
    def _set(self):
        self.all_countries = self.country_leagues
        self.all_leagues = [l for c in self.all_countries for l in c.leagues]
        self.all_teams = [t for l in self.all_leagues for t in l.teams]
        for t in self.all_teams:
            for p in t.affilation_players:
                p.team_uuid = t.uuid
        self.all_active_players = [p for t in self.all_teams for p in t.affilation_players]
        
    def set_calendar(self):
        # カレンダーの作成
        CALENDAR = [{} for _ in range(ONE_YEAR_DAYS)]
        
        for league in self.all_leagues:
            league_teams = [t for t in self.all_teams if t.league_uuid==league.uuid]
            create_sections_calendar(league=league, teams=league_teams, 
                                     calendar=CALENDAR, 
                                     period=self.period)

        for com in self.all_competitions:
            com.create_1season_calendar(calendar=CALENDAR, now_day=0)
        
        return CALENDAR
    
    def check_duplication(self):
        if len(self.free_players) != len(set(self.free_players)):
            print(len(self.free_players), len(set(self.free_players)))
            raise("重複しています")
    
    def search_country(self, team):
        league = [l for l in self.all_leagues if l.uuid==team.league_uuid][0]
        country = [c for c in self.all_countries if c.uuid==league.country_uuid][0]
        return country.name
        
    def prepare_1season(self, year):
        for c in self.all_countries:
            leagues = [l.uuid for l in self.all_leagues if l.country_uuid==c.uuid]
            teams = [t for t in self.all_teams if t.league_uuid in leagues]
            teams_uuid = [t.uuid for t in teams]
            competition = c.prepare_competition(year)
            competition.set_competition(teams_uuid=teams_uuid)
            for t in teams:
                t.set_player_result(competition.name, year, "カップ戦")
            self.all_competitions.append(competition)
   
        for l in self.all_leagues:
            season_name = f'{l.name}_{year}'
            l_teams = [t.name for t in self.all_teams if t.league_uuid==l.uuid]
            l.set_team_result(season_name, all_team_name=l_teams)
        
        for t in self.all_teams:
            season_name = f'{t.league_name}_{year}'
            for p in t.affilation_players:
                p.partification = 0
                p.partification_position = None
            t.set_main_rate_position(injury_level=100)
            t.set_register_players(injury_level=100)
            t.set_player_result(season_name, year, "リーグ")
    
    def play_1season(self, year):
        # シーズン開始前の準備        
        self.prepare_1season(year)
        
        CALENDAR = self.set_calendar()

        for progress_day, plan in enumerate(tqdm(CALENDAR)):
            away_teams_uuid = []
            if len(plan.keys())!=0:
                for home_uuid, (away_uuid, _, kind, kind_uuid) in plan.items():
                    if home_uuid in away_teams_uuid:
                        continue
                    else:
                        away_teams_uuid.append(away_uuid)

                    if kind == "league":
                        league = [l for l in self.all_leagues if l.uuid==kind_uuid][0]
                        league.play_1section(year=year,
                                             home=[t for t in self.all_teams if t.uuid==home_uuid][0],
                                             away=[t for t in self.all_teams if t.uuid==away_uuid][0])

                    if kind == "competition":
                        competition = [com for com in self.all_competitions if com.uuid==kind_uuid][0]
                        t_result = competition.play_1section(home=[t for t in self.all_teams if t.uuid==home_uuid][0],
                                                             away=[t for t in self.all_teams if t.uuid==away_uuid][0])
                        if len(t_result)==1:
                            competition.create_1season_calendar(calendar=CALENDAR, now_day=progress_day)
                        elif len(t_result)>1:
                            country = [c for c in self.all_countries if c.uuid==competition.country_uuid][0]
                            country.competition_result_top.loc[competition.name, ["年度", "優勝", "準優勝"]] = t_result
                            tqdm.write(f"\nWin <{competition.name}> : {t_result[1]}\n")
                    
            self.debug_calendar = CALENDAR
            
            if progress_day!=0 and progress_day!=300 and (progress_day%100==0 or progress_day==ONE_YEAR_DAYS-1):
                tqdm.write("\n")
                for l in self.all_leagues:
                    l.cal_team_rank(year)
                    if l.league_level<10:
                        txt = f"{l.name} : "
                        buff = l.team_result[f'{l.name}_{year}'].iloc[:1][["Points"]]
                        txt += " >> ".join([f"{name} {rank+1}位({row.Points}PTS)" for rank, (name, row) in enumerate(buff.iterrows())])
                        txt += " // "
                        buff = l.team_result[f'{l.name}_{year}'].iloc[-1:][["Points"]]
                        txt += " >> ".join([f"{name} {rank+18}位({row.Points}PTS)" for rank, (name, row) in enumerate(buff.iterrows())])
                        tqdm.write(txt)
                tqdm.write("\n")
        
        # リーグ成績の計算
        for l in self.all_leagues:
            teams = [t for t in self.all_teams if t.league_uuid==l.uuid]
            l.cal_1year_result(year, teams)
        
        # アンダーの練習
        output = pd.DataFrame({"名前":[p.name for t in self.all_teams for p in t.not_register_players],
                               "uuid":[p.uuid for t in self.all_teams for p in t.not_register_players],
                               "年齢":[p.age for t in self.all_teams for p in t.not_register_players],
                               "Rate" : [p.main_rate for t in self.all_teams for p in t.not_register_players],
                               "E_Rate" : [p.evaluate_rate for t in self.all_teams for p in t.not_register_players],
                               "残契約":[p.contract-1 for t in self.all_teams for p in t.not_register_players],
                               "ポジション":[p.main_position for t in self.all_teams for p in t.not_register_players],
                               "リーグ":["Under League" for t in self.all_teams for p in t.not_register_players],
                               "リーグレベル":[10 for t in self.all_teams for p in t.not_register_players],
                               "年度":[year for t in self.all_teams for p in t.not_register_players],
                               "国":[self.search_country(team=t) for t in self.all_teams for p in t.not_register_players],
                               "チーム":[f"{t.name}_B" for t in self.all_teams for p in t.not_register_players],
                               "レンタル元":["" for t in self.all_teams for p in t.not_register_players],
                               "分類":["Bチーム" for t in self.all_teams  for p in t.not_register_players],
                               "順位" :  [f"記録なし" for t in self.all_teams  for p in t.not_register_players],
                               "試合数":[30 for t in self.all_teams  for p in t.not_register_players],
                               "出場時間":[1800 for t in self.all_teams  for p in t.not_register_players],
                               "goal":[0 for t in self.all_teams  for p in t.not_register_players],
                               "assist":[0 for t in self.all_teams  for p in t.not_register_players],
                               "CS":[0 for t in self.all_teams  for p in t.not_register_players],
                               "評価点":[0 for t in self.all_teams  for p in t.not_register_players],
                               "MOM":[0 for t in self.all_teams  for p in t.not_register_players],
                               "怪我欠場":[0 for t in self.all_teams  for p in t.not_register_players],
                               "怪我回数":[0 for t in self.all_teams  for p in t.not_register_players],
                               "賞":["" for t in self.all_teams  for p in t.not_register_players],
                               "全ポジション回数":["" for t in self.all_teams  for p in t.not_register_players],})
            
        self.players_result = pd.concat([self.players_result, output])
        self.players_result = self.players_result.reset_index(drop=True)

        for t in self.all_teams:
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
                p.evaluate_rate = p.main_rate
                p.consider_retirement(year)
                p.injury = 0
        
        # 選手の成績の計算
        temp_result = pd.DataFrame()
        for com in self.all_competitions:
            c_teams = [t for t in self.all_teams if t.uuid in com.origin_competition_teams_uuid]
            c_leagues = [l for l in self.all_leagues if l.country_uuid==com.country_uuid]
            country = [c for c in self.all_countries if c.uuid==com.country_uuid][0]
            competition_result, result_txt = com.cal_players_result(year, c_teams, c_leagues, country)
            temp_result = pd.concat([temp_result, competition_result])
            country.cal_players_result(com, result_txt)

        for l in self.all_leagues:
            country = [c for c in self.all_countries if c.uuid==l.country_uuid][0]
            country_name = country.name
            country_competition_name = f"{country.competition_name}_{year}"
            l_teams = [t for t in self.all_teams if t.league_uuid==l.uuid]
            league_result = l.cal_players_result(year, l_teams, country_name, country_competition_name)
            temp_result = pd.concat([temp_result, league_result])
        
        ballond_candiate = temp_result[((temp_result["リーグレベル"]==1)&(temp_result["出場時間"]>19*2*90*0.8)&(temp_result["年度"]==year)&(temp_result["試合数"]>19*2*0.85))]
        ballond_candiate = ballond_candiate.sort_values("評価点", ascending=False).iloc[:1]
        temp_result.loc[ballond_candiate.index, "賞"] += f"Ballon d'Or_{year}, "
        self.players_result = pd.concat([self.players_result, temp_result])

        # 昇格降格
        for t in self.all_teams:
            t.league_state = "stay"
        
        for l in self.all_leagues:
            season_name = f"{l.name}_{year}"
            if l.category!="top":
                promotion = l.promotion[season_name]
                promotion_team = [t for t in self.all_teams if t.uuid in promotion]
                for t in promotion_team:
                    t.league_state = "promotion"
                    t.league_uuid = l.upperleague_uuid
                    t.league_name = l.upperleague_name

            if l.category!="lowest":
                relegation =l.relegation[season_name]
                relegation_team = [t for t in self.all_teams if t.uuid in relegation]
                for t in relegation_team:
                    t.league_state = "relegation"
                    t.league_uuid = l.lowerleague_uuid
                    t.league_name = l.lowerleague_name
        
        self.all_competitions.extend(self.all_competitions)
        self.all_competitions = []
    
    def play_offseason(self, year):
        print("オフシーズン")
        print("-"*30)

        sum_retire_player = 0

        # フリー契約の人
        if len(self.free_players) > 0:
            for p in self.free_players:
                # TODO:ここ変えたい
                if p.age<=25:
                    p.grow_up(20)
                else:
                    p.grow_up(0)

                if p.main_position != "GK":
                    p.select_main_position()
                else:
                    p.main_rate = p.cal_rate()
                p.cal_all_rate()
                p.evaluate_rate = p.evaluate_rate-2

                p.set_history("free", year)
                p.injury = 0
                p.free_time += 1
                p.consider_retirement(year)

            output = pd.DataFrame({"名前":[p.name for p in self.free_players],
                                   "uuid":[p.uuid for p in self.free_players],
                                   "年齢":[p.age for p in self.free_players],
                                    "Rate":[p.main_rate for p in self.free_players],
                                    "E_Rate":[p.evaluate_rate for p in self.free_players],
                                    "残契約":[0 for p in self.free_players],
                                    "ポジション":[p.main_position for p in self.free_players],
                                    "リーグ":["free" for p in self.free_players],
                                    "リーグレベル":[-1 for p in self.free_players],
                                    "年度":[year for p in self.free_players],
                                    "国":["free" for p in self.free_players], 
                                    "チーム":["free" for p in self.free_players],
                                    "レンタル元":["" for p in self.free_players],
                                    "分類":["free" for p in self.free_players],
                                    "順位":["" for p in self.free_players],
                                    "試合数":[0 for p in self.free_players],
                                    "出場時間":[0 for p in self.free_players],
                                    "goal":[0 for p in self.free_players],
                                    "assist":[0 for p in self.free_players],
                                    "CS":[0 for p in self.free_players],
                                    "評価点":[0 for p in self.free_players],
                                    "MOM":[0 for p in self.free_players],
                                    "怪我欠場":[0 for p in self.free_players],
                                    "怪我回数":[0 for p in self.free_players],
                                    "賞":["" for p in self.free_players],
                                    "全ポジション回数":["" for p in self.free_players],
            })

            self.players_result = pd.concat([self.players_result, output])

            self.players_result = self.players_result.reset_index(drop=True)
            retire_player = [p for p in self.free_players if p.retire==1]
            self.retire_players.extend(retire_player)
            self.free_players = [p for p in self.free_players if p not in retire_player]

            sum_retire_player += len(retire_player)
        
        # レンタル選手を元のチームに戻す
        for t in self.all_teams:
            rental_players = [p for p in t.affilation_players if p.rental==1]
            t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
            for p in rental_players:
                origin_team_uuid = p.origin_team_uuid
                p.rental = 0
                p.origin_team_uuid = None
                p.origin_team_name = ""
                team = [t for t in self.all_teams if t.uuid==origin_team_uuid][0]
                team.affilation_players.append(p)

        # 引退と契約切れを行う
        for t in self.all_teams:
            league = [l for l in self.all_leagues if l.uuid==t.league_uuid][0]
            # 引退
            retire_player = [p for p in t.affilation_players if p.retire==1]
            sum_retire_player += len(retire_player)
            self.retire_players.extend(retire_player)
            t.affilation_players = [p for p in t.affilation_players if p not in retire_player]

            # 契約切れ
            expired_players = [p for p in t.affilation_players if p.contract==0]
            self.free_players.extend(expired_players)
            t.affilation_players = [p for p in t.affilation_players if p not in expired_players]

            # リーグのレベルにそぐわない選手を契約切れに
            out_players = [p for p in t.affilation_players if p.main_rate>league.max_rate]
            self.free_players.extend(out_players)
            t.affilation_players = [p for p in t.affilation_players if p not in out_players]

            # リーグのレベル以下の選手をレンタル選手に
            # TODO:のちのちレベル以下も試合に出場したりできるように、誰をレンタルにするかもっと考慮できるシステムを
            rental_players = [p for p in t.affilation_players if p.main_rate<league.min_rate and p.age<YOUNG_OLD]
            set_rental_transfer(rental_players, t.uuid, t.name)
            self.free_players.extend(rental_players)
            t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
            rental_players_ = rental_players.copy()
            t.rental_num = len(rental_players_)

            t.check_duplication()
            self.check_duplication()
        
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
                # 移籍市場からスタメン選手を入団させる
                for l in random.sample(self.all_leagues, k=len(self.all_leagues)):
                    if l.league_level==league_level:
                        l_teams = [t for t in self.all_teams if t.league_uuid==l.uuid]
                        for t in random.sample(l_teams, len(l_teams)):
                            #print(t.name)
                            t.check_duplication()
                            self.free_players = t.get_free_players_starting(self.free_players, l)
                            t.check_duplication()
            
                # 移籍市場からベンチ選手を入団させる
                for l in random.sample(self.all_leagues, k=len(self.all_leagues)):
                    if l.league_level==league_level:
                        l_teams = [t for t in self.all_teams if t.league_uuid==l.uuid]
                        for t in random.sample(l_teams, len(l_teams)):
                            self.free_players = t.get_free_players_bench(self.free_players, l)

                            young_player_num = max(0, t.member_num - len(t.affilation_players) - t.rental_num)
                            gk_num = min(3, len([p for p in t.affilation_players if p.main_position=="GK"]))
                            t.set_empty_position_random(young_player_num, 3-gk_num)

                            # 新しく選手を作成する
                            Cp = Create_player(position_num=t.empty_position, 
                                                min_rate=40, max_rate=80, 
                                                age_mean=19,
                                                now_year=year,
                                                mean_rate=l.mean_rate)
                            
                            Cp.create_teams(new=True)
                            t.check_duplication()
                            new_players = Cp.players
                            t.affilation_players.extend(new_players)

                            t.set_main_rate_position()
                            t.set_register_players(change_register=False)

                            # 登録外の選手でレンタルにもならない選手を外に出す
                            # TODO:のちの修正ポイント
                            t.check_duplication()
                            out_players = [p for p in t.affilation_players if p.register==0 and p.age>=YOUNG_OLD]
                            for p in out_players:
                                p.contract = 0
                            self.free_players.extend(out_players)
                            self.check_duplication()
                            t.affilation_players = [p for p in t.affilation_players if p not in out_players]

                            # メンバー外の若手をレンタルに
                            rental_players = [p for p in t.affilation_players if p.register==0 and p.age<YOUNG_OLD]
                            set_rental_transfer(rental_players, t.uuid, t.name)
                            self.free_players.extend(rental_players)
                            t.affilation_players = [p for p in t.affilation_players if p not in rental_players]
                            rental_players_ = rental_players.copy()
                            t.rental_num += len(rental_players_)
                            self.check_duplication()
            count += 1   
        
        # 移籍市場からレンタル選手を元のチームに戻す
        rental_players = [p for p in self.free_players if p.rental==1]
        self.free_players = [p for p in self.free_players if p not in rental_players]

        for p in rental_players:
            origin_team_uuid = p.origin_team_uuid
            p.rental = 0
            p.origin_team_uuid = None
            p.origin_team_name = ""
            team = [t for t in self.all_teams if t.uuid==origin_team_uuid][0]
            team.affilation_players.append(p)
        
        transfer_end = time.time()

        print(" 移籍市場経過時間 : {:.2f}秒".format(transfer_end-transfer_start))
        print(" 残留籍市場人数 : ", len(self.free_players))
        print()
    