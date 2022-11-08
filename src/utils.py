import numpy as np
import pandas as pd
import cv2

import random
import uuid

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

def parctice_player_result(player, year):
    output = pd.DataFrame({"名前":[player.name],
                           "uuid":[player.uuid],
                           "年齢":[player.age],
                           "Rate":[player.main_rate],
                           "残契約":[0],
                           "ポジション":[player.main_position],
                           "リーグ":["practice_league"],
                           "年度":[year],
                           "国":["rental"], 
                           "チーム":["practice_team"],
                           "レンタル元":[""],
                           "分類":["練習リーグ"],
                           "順位":["記録なし"],
                           "試合数":[20],
                           "出場時間":[1800],
                           "goal":[0],
                           "assist":[0],
                           "CS":[0],
                           "怪我欠場":[0],
                           "怪我回数":[0],
                           "賞":[""],
                           "全ポジション回数":[""],
    })
    return output

def rental_player_result(player, year, team_name):
    output = pd.DataFrame({"名前":[player.name],
                           "uuid":[player.uuid],
                           "年齢":[player.age],
                           "Rate":[player.main_rate],
                           "残契約":[player.contract],
                           "ポジション":[player.main_position],
                           "リーグ":["rental_league"],
                           "年度":[year],
                           "国":["rental"], 
                           "チーム":["rental_team"],
                           "レンタル元":[team_name],
                           "分類":["レンタルリーグ"],
                           "順位":["記録なし"],
                           "試合数":[30],
                           "出場時間":[1800],
                           "goal":[0],
                           "assist":[0],
                           "CS":[0],
                           "怪我欠場":[0],
                           "怪我回数":[0],
                           "賞":[""],
                           "全ポジション回数":[""],
    })
    return output

def self_study_player_result(player, year):
    output = pd.DataFrame({"名前":[player.name],
                           "uuid":[player.uuid],
                           "年齢":[player.age],
                           "Rate":[player.main_rate],
                           "残契約":[0],
                           "ポジション":[player.main_position],
                           "国":["rental"], 
                           "リーグ":["所属なし"],
                           "年度":[year],
                           "チーム":["所属なし"],
                           "分類":["自主練"],
                           "順位":["記録なし"],
                           "試合数":[0],
                           "出場時間":[0],
                           "goal":[0],
                           "assist":[0],
                           "CS":[0],
                           "怪我欠場":[0],
                           "怪我回数":[0],
                           "賞":[""],
                           "全ポジション回数":[""],
    })
    return output

def team_count(output):
    result = output[output["分類"]!="カップ戦"]["チーム"].values

    count = 1
    c = result[0]

    for r in result:
        if c!=r:
            count+=1
            c=r
    
    return count

def country_img(name):
    img = cv2.imread(f"../../data/img/{name}.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    img = cv2.resize(img, (260, 173))
    img_ = img.copy()
    white = np.full_like(img, 255)

    for i in range(3):
        img_ = cv2.hconcat([white, img_])
    
    return img, img_
