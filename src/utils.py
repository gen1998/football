import numpy as np
import pandas as pd
import cv2

import random
import uuid

def create_sections(num=20, reverse=False):
    output = []

    for i in range(int(num/2)):
        if i==0:
            a = [[1, num-i] for i in range(num-1)]
            r = [[num-i, 1] for i in range(num-1)]
        else:
            a = []
            r = []
            for j in range(num-1):
                x = i+1-j
                y = num-j-i

                if x<2:
                    x = x+num-1
                if y<2:
                    y = y+num-1

                a.append([x, y])
                r.append([y, x])

        a.extend(r)
        output.append(a)

    return np.array(output)

def create_sections_calendar(league, calendar, period=300, interval=7):
    section_num = (league.num-1)*2
    rest_days = (period-interval*section_num)//interval
    rest_interval = section_num//rest_days
    
    rest = 1
    
    for s in range(section_num):
        if s==rest*rest_interval:
            #calendar[(s+rest-1)*interval][f"{league.uuid}_league"] = f" Rest_{rest}"
            rest += 1
        calendar[(s+rest-1)*interval][f"{league.uuid}_league"] = f"Section_{s+1}"
    
    league.sections = create_sections(num=league.num)

def create_cup_calendar(competition, con_games, calendar, period=300, interval=7):
    section_num = period//interval
    cup_interval = section_num//(competition.max_round+con_games)
    
    section = 0
    rest_section = 0
    interval_ = interval//2
    
    for s in range(section_num):
        if section>=competition.max_round:
            break
            
        if s==cup_interval*rest_section:
            if "CL" not in calendar[s*interval+interval_].keys():
                calendar[s*interval+interval_][f"{competition.uuid}_cup"] = f"Cup_{section+1}"
                section+=1
            rest_section += 1

def create_empty_position(dict_pos, players):
    for p in players:
        pos = p.main_position
        if pos == "LW":
            pos = "RW"
        elif pos == "LM":
            pos = "RM"
        elif pos == "CF":
            pos = "CAM"
        elif pos == "LB" or pos == "LWB" or pos == "RWB":
            pos = "RB"

        if pos not in dict_pos.keys():
            dict_pos[pos] = 1
        else:
            dict_pos[pos] += 1
    
    return dict_pos

def search_player(ProLeague, all_member, uuid_):
    if all_member[all_member.uuid == uuid.UUID(uuid_)]["進退"].values[0] == "引退":
        player = [p for p in ProLeague.retire_players if p.uuid == uuid.UUID(uuid_)][0]
    else:
        l = [l for l in ProLeague.leagues if l.name==all_member[all_member.uuid == uuid.UUID(uuid_)]["リーグ"].values[0]][0]
        t = [t for t in l.teams if t.name==all_member[all_member.uuid == uuid.UUID(uuid_)]["チーム"].values[0]][0]
        player = [p for p in t.affilation_players if p.uuid == uuid.UUID(uuid_)][0]
    return player

def set_rental_transfer(rental_players, t):
    for p in rental_players:
        p.rental = 1
        p.origin_team = t
        p.origin_team_name = t.name

def team_count(p):
    output = []

    for y, v in p.history.items():
        if y==min(p.history.keys()):
            output.append(v[0])
            v_b = v[0]
            
        elif len(v) ==1:
            if v_b != v[0]:
                output.append(v[0])
                v_b = v[0]
        else:
            output.append(v[0])
            if v_b != v[1]:
                output.append(v[1])
                v_b = v[1]
    
    return len((output))

def country_img(name, rental=False):
    img = cv2.imread(f"../../data/img/{name}.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    img = cv2.resize(img, (260, 173))
    img_ = img.copy()
    white = np.full_like(img, 255)

    for i in range(3):
        img_ = cv2.hconcat([white, img_])
    
    if rental==True:
        img_ = cv2.hconcat([white, img_])
    
    return img, img_

def cal_game_rating_rate(team):
    partification_rate = [p.position_all_rate[p.partification_position] for p in team.affilation_players if p.partification==1]
    min_rate = min(partification_rate)
    max_rate = max(partification_rate)
    return min_rate, max_rate

def create_all_member(ws, now_year):
    output = pd.DataFrame()
    for c in ws.country_leagues:
        for l in c.leagues:
            for t in l.teams:
                buff = pd.DataFrame({"名前":[p.name for p in t.affilation_players],
                                     "uuid":[p.uuid for p in t.affilation_players],
                                     "年齢":[p.age for p in t.affilation_players],
                                     "生まれ年":[p.born_year for p in t.affilation_players],
                                     "Rate":[p.main_rate for p in t.affilation_players],
                                     "成長タイプ":[p.grow_type for p in t.affilation_players],
                                     "リーグ":[l.name for p in t.affilation_players],
                                     "チーム":[t.name for p in t.affilation_players],
                                     "進退":["現役" for p in t.affilation_players],
                                    })
                
                output = pd.concat([output, buff])
    
    retire_output = pd.DataFrame({"名前":[p.name for p in ws.retire_players],
                                  "uuid":[p.uuid for p in ws.retire_players],
                                  "年齢":[now_year - p.born_year for p in ws.retire_players],
                                  "生まれ年":[p.born_year for p in ws.retire_players],
                                  "Rate":[p.main_rate for p in ws.retire_players],
                                  "成長タイプ":[p.grow_type for p in ws.retire_players],
                                  "リーグ":["引退" for p in ws.retire_players],
                                  "チーム":["引退" for p in ws.retire_players],
                                  "進退":["引退" for p in ws.retire_players],
                                 })
    
    output = pd.concat([output, retire_output])
    del retire_output

    free_output = pd.DataFrame({"名前":[p.name for p in ws.free_players],
                                "uuid":[p.uuid for p in ws.free_players],
                                "年齢":[now_year - p.born_year for p in ws.free_players],
                                "生まれ年":[p.born_year for p in ws.free_players],
                                "Rate":[p.main_rate for p in ws.free_players],
                                "成長タイプ":[p.grow_type for p in ws.free_players],
                                "リーグ":["フリー" for p in ws.free_players],
                                "チーム":["フリー" for p in ws.free_players],
                                "進退":["フリー" for p in ws.free_players],
                                })
    
    output = pd.concat([output, free_output])
    output = output.reset_index(drop=True)
    return output

def team_to_country(WorldLeague):
    team_list = [(t.name, c.name) for c in WorldLeague.country_leagues for l in c.leagues for t in l.teams]
    output = {}
    
    for (t,c) in team_list:
        output[t] = c
    
    output["free"] = "free"
    output["所属なし"] = "free"
    
    return output

def search_player_class(WorldLeague, uuid_):
    p = [p for c in WorldLeague.country_leagues for l in c.leagues for t in l.teams for p in t.affilation_players if p.uuid==uuid.UUID(f"{uuid_}")]
    
    if len(p)>0:
        return p[0]
    
    p = [p for p in WorldLeague.retire_players if p.uuid==uuid.UUID(f"{uuid_}")]
    
    if len(p)>0:
        return p[0]
    
    p = [p for p in WorldLeague.free_players if p.uuid==uuid.UUID(f"{uuid_}")]
    
    if len(p)>0:
        return p[0]

def rate_function(x, league_level):
    if league_level==1:
        #y = 1/30*(x**3)+3/10*(x**2)-11/15*x+73
        #y = 1/15*(x**3)+4/15*(x**2)-37/15*x+75+1/3
        y = 1*(x**3)-25/2*(x**2)+99/2*x+15
        y = max(min(y, 95), 70)
    elif league_level==2:
        #y = 7/30*(x**3)-29/10*(x**2)+208/15*x+47
        y = 8/15*(x**3)-61/10*(x**2)+707/30*x+35
        y = max(min(y, 85), 60)
    elif league_level==3:
        #y = 7/30*(x**3)-29/10*(x**2)+208/15*x+42
        y = 8/15*(x**3)-61/10*(x**2)+707/30*x+30
        y = max(min(y, 80), 50)
    elif league_level==4:
        #y = 7/30*(x**3)-29/10*(x**2)+208/15*x+38
        y = 8/15*(x**3)-61/10*(x**2)+707/30*x+26
        y = max(min(y, 75), 45)
    else:
        return 0
    return int(y)

"""
def create_calender(num=20, reverse=False):
    output = []
    output_r = []

    for i in range(int(num/2)):
        if i==0:
            a = [[1, num-i] for i in range(num-1)]
            r = [[num-i, 1] for i in range(num-1)]
        else:
            a = []
            r = []
            for j in range(num-1):
                x = i+1-j
                y = num-j-i

                if x<2:
                    x = x+num-1
                if y<2:
                    y = y+num-1

                a.append([x, y])
                r.append([y, x])

        output.append(a)
        output_r.append(r)
    output = pd.DataFrame(output).T
    output_r = pd.DataFrame(output_r).T

    output = pd.concat([output, output_r])
    output = output.reset_index(drop=True)
    
    return output
"""