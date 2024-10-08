import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import math

from src.object.player import FieldPlayer
from src.utils import team_count, country_img, team_to_country, search_player_class

from IPython.core.display import display

import uuid

def print_player(WorldLeague, all_member, uuid_):
    member = all_member[all_member.uuid==uuid.UUID(f"{uuid_}")]
    display(member[['名前', '年齢', '生まれ年', '成長タイプ']])

    output = WorldLeague.players_result
    output = output[output.uuid==uuid.UUID(f"{uuid_}")]
    #output = output[output["分類"]=="リーグ"]
    output = output.reset_index(drop=True)
    #t_name_b = ""

    t_c_dict = team_to_country(WorldLeague)

    p = search_player_class(WorldLeague, uuid_)
    team_c = team_count(p)
    plt.figure(figsize = (12, team_c*0.3)) # 図のサイズ指定

    s_year = min(p.history.keys())
    e_year = max(p.history.keys())

    rental_team = []
    rental_year = []

    rental_team_b = []
    rental_year_b = []

    index = 0

    for year in range(s_year, e_year+1):
        if year == s_year:
            team_b = p.history[year]
            if len(team_b) > 1:
                rental_team_b.append(team_b[0])
                rental_year_b.append(year)
                team_b = team_b[1]
            else:
                team_b = team_b[0]
            s_year_b = s_year
        else:
            team = p.history[year]
            if len(team) > 1 and team!="Retire":
                rental_team_b.append(team[0])
                rental_year_b.append(year)
                team = team[1]
            else:
                team = team[0]
            
            if team_b!=team or year==e_year:
                pd_result = output[((output["年度"]>=s_year_b)&(output["年度"]<year)&(~output["年度"].isin(rental_year_b)))]
                result_txt = f'{pd_result["試合数"].sum()}({pd_result["goal"].sum()})'
                img, img_ = country_img(t_c_dict[team_b])

                plt.subplot(team_c, 1, index+1)
                plt.axis("off")
                plt.text(0, int(img.shape[0]*0.8), f"{s_year_b}-{year}", size=11)
                plt.imshow(img_)
                plt.text(int(4.3*img.shape[1]), int(img.shape[0]*0.8), f"{team_b}", size=11)
                plt.text(int(10.3*img.shape[1]), int(img.shape[0]*0.8), f"{result_txt}", size=11)
                #print(s_year_b, year, team_b, result_txt)

                index+=1
                
                if len(rental_team_b)>0:
                    for t, y in zip(rental_team_b, rental_year_b):
                        pd_result = output[output["年度"]==y]
                        result_txt = f'{pd_result["試合数"].sum()}({pd_result["goal"].sum()})'
                        
                        img, img_ = country_img(t_c_dict[t], rental=True)

                        plt.subplot(team_c, 1, index+1)
                        plt.axis("off")
                        plt.text(int(0.5*img.shape[1]), int(img.shape[0]*0.8), f"{y}-{y+1}", size=11)
                        plt.imshow(img_)
                        plt.text(int(3.3*img.shape[1]), int(img.shape[0]*0.8), f"→", size=11)
                        plt.text(int(5.3*img.shape[1]), int(img.shape[0]*0.8), f"{t}(loan)", size=11)
                        plt.text(int(10.8*img.shape[1]), int(img.shape[0]*0.8), f"{result_txt}", size=11)
                        #print("->", y, y+1, t, result_txt)
                        index += 1
                
                rental_team_b = rental_team
                rental_year_b = rental_year
                
                rental_team = []
                rental_year = []
                team_b = team
                s_year_b = year
            
    plt.show()

    """
        
    count = 0
    index = 0
    for i, row in output.iterrows():
        t_name = row["チーム"]
        c_name = row["国"]
        r_name = row["レンタル元"]
        if i==0:
            t_name_b = row["チーム"]
            c_name_b = row["国"]
            r_name_b = row["レンタル元"]
            t_s = row["年度"]
            t_i = 0
        if t_name!=t_name_b:
            result_txt = f'{output.loc[t_i:i-1, "試合数"].sum()}({output.loc[t_i:i-1, "goal"].sum()})'
            plt.subplot(team_c, 1, index+1)
            plt.axis("off")
            if r_name_b == "":
                img, img_ = country_img(c_name_b)
            else:
                img, img_ = country_img(c_name_b, rental=True)
            if t_s == row["年度"]-1:
                plt.text(0, int(img.shape[0]*0.8), f"{t_s}-{t_s+1}", size=11)
                #plt.text(0, 15-count, f"  {t_s}   {t_name_b.ljust(10)} {result_txt}")
            else:
                plt.text(0, int(img.shape[0]*0.8), f"{t_s}-{row['年度']}", size=11)
                #plt.text(0, 15-count, f"  {t_s}-{row['年度']-1}   {t_name_b.ljust(10)} {result_txt}")
            plt.imshow(img_)
            if r_name_b == "":
                plt.text(int(4.3*img.shape[1]), int(img.shape[0]*0.8), f"{t_name_b}", size=11)
                plt.text(int(10.3*img.shape[1]), int(img.shape[0]*0.8), f"{result_txt}", size=11)
            else:
                plt.text(int(3.3*img.shape[1]), int(img.shape[0]*0.8), f"→", size=11)
                plt.text(int(5.3*img.shape[1]), int(img.shape[0]*0.8), f"{t_name_b}", size=11)
                plt.text(int(10.8*img.shape[1]), int(img.shape[0]*0.8), f"{result_txt}", size=11)
            t_s = row["年度"]
            t_i = i
            count += 1
            index+=1
        if i==len(output)-1:
            result_txt = f'{output.loc[t_i:i, "試合数"].sum()}({output.loc[t_i:i, "goal"].sum()})'
            plt.subplot(team_c, 1, index+1)
            plt.axis("off")
            if r_name_b == "":
                img, img_ = country_img(c_name_b)
            else:
                img, img_ = country_img(c_name_b, rental=True)
            if t_s == row["年度"]:
                plt.text(0, int(img.shape[0]*0.8), f"{t_s}-{t_s+1}", size=11)
                #plt.text(0, 15-count, f"  {t_s}   {t_name.ljust(10)} {result_txt}")
            else:
                plt.text(0, int(img.shape[0]*0.8), f"{t_s}-{row['年度']+1}", size=11)
                #plt.text(0, 15-count, f"  {t_s}-{row['年度']}   {t_name.ljust(10)} {result_txt}")
            plt.imshow(img_)
            if r_name_b == "":
                plt.text(int(4.3*img.shape[1]), int(img.shape[0]*0.8), f"{t_name_b}", size=11)
                plt.text(int(10.3*img.shape[1]), int(img.shape[0]*0.8), f"{result_txt}", size=11)
            else:
                plt.text(int(3.3*img.shape[1]), int(img.shape[0]*0.8), f"→", size=11)
                plt.text(int(5.3*img.shape[1]), int(img.shape[0]*0.8), f"{t_name_b}", size=11)
                plt.text(int(10.8*img.shape[1]), int(img.shape[0]*0.8), f"{result_txt}", size=11)
            count+=3
            index+=1
        t_name_b = t_name
        c_name_b = c_name
        r_name_b = r_name

    for c in WorldLeague.country_leagues:
        for l in c.leagues:
            buff = output[output["リーグ"]==l.name]
            if len(buff)>0:
                result_txt = f'{buff["試合数"].sum()}({buff["goal"].sum()})'
                plt.text(0, 15-count, f"  {l.name}   {result_txt}")
                count+=1
    """
    
    plt.figure(figsize = (12, 3))
    plt.subplot(1, 3, 1)
    plt.axis([0,15,0,15]) 
    plt.axis("off")
    count=0
    text_list = []
    for row in output["賞"]:
        if row != "" or row != " ":
            for r in row.split(","):
                if r != "":
                    text_list.append(f"{r}")
    
    text_list = sorted(text_list)
    
    for txt in text_list:
        plt.text(0, 15-count, f"{txt}")
        count += 1

    plt.subplot(1, 3, 2)
    plt.plot(output["年齢"], output["Rate"])
    plt.title("Rate変動")
    plt.xlim([output["年齢"].min()-2, output["年齢"].max()+2])
    plt.ylim([output["Rate"].min()-3, output["Rate"].max()+3])
    plt.xlabel("年齢")
    plt.ylabel("Rate")

    if all_member[all_member.uuid == uuid.UUID(uuid_)]["進退"].values[0] == "引退":
        player = [p for p in WorldLeague.retire_players if p.uuid == uuid.UUID(uuid_)][0]
    else:
        l = [l for c in WorldLeague.country_leagues for l in c.leagues if l.name==all_member[all_member.uuid == uuid.UUID(uuid_)]["リーグ"].values[0]][0]
        t = [t for t in l.teams if t.name==all_member[all_member.uuid == uuid.UUID(uuid_)]["チーム"].values[0]][0]
        player = [p for p in t.affilation_players if p.uuid == uuid.UUID(uuid_)][0]

    if player.main_position!="GK":
        plt.subplot(1, 3, 3)
        print_rate(player)

    plt.show()

    output = WorldLeague.players_result
    output = output[output.uuid==uuid.UUID(f"{uuid_}")]
    output = output[output["分類"]!="カップ戦"]
    display(output)

def print_rate(player):
    pos = player.main_position
    
    # 最大値
    if "max" in player.grow_exp_dict.keys():
        cl = "max"
        color = "r"
        pace = np.int8(np.round(player.pace_initial + player.grow_exp_dict[cl][0]))/100
        sho = np.int8(np.round(player.shooting_initial + player.grow_exp_dict[cl][1]))/100
        pas = np.int8(np.round(player.passing_initial + player.grow_exp_dict[cl][2]))/100
        dri = np.int8(np.round(player.dribbling_initial + player.grow_exp_dict[cl][3]))/100
        de = np.int8(np.round(player.defending_initial + player.grow_exp_dict[cl][4]))/100
        phy = np.int8(np.round(player.physicality_initial + player.grow_exp_dict[cl][5]))/100

        plt_hexagon(pace, sho, pas, dri, de, phy, color, main_position=pos, text=False, label="最大値")
    
    # 初期値
    pace = np.int8(np.round(player.pace_initial))/100
    sho = np.int8(np.round(player.shooting_initial))/100
    pas = np.int8(np.round(player.passing_initial))/100
    dri = np.int8(np.round(player.dribbling_initial))/100
    de = np.int8(np.round(player.defending_initial))/100
    phy = np.int8(np.round(player.physicality_initial))/100

    plt_hexagon(pace, sho, pas, dri, de, phy, color="y", main_position=pos, text=False, label="入団値")
    
    # 現在値
    pace = np.int8(np.round(player.pace_initial + player.pace_exp))/100
    sho = np.int8(np.round(player.shooting_initial + player.shooting_exp))/100
    pas = np.int8(np.round(player.passing_initial + player.passing_exp))/100
    dri = np.int8(np.round(player.dribbling_initial + player.dribbling_exp))/100
    de = np.int8(np.round(player.defending_initial + player.defending_exp))/100
    phy = np.int8(np.round(player.physicality_initial + player.physicality_exp))/100
    
    plt_hexagon(pace, sho, pas, dri, de, phy, color="b", main_position=pos, text=False, label="現在値")
    
    for i in range(11):
        plt_hexagon(i/10, i/10, i/10, i/10, i/10, i/10, color="black", alpha=0.2, text=True)
    
    plt.legend(bbox_to_anchor=(0.5, 0), loc='lower right', fontsize=8)

def plt_hexagon(pace, sho, pas, dri, de, phy, color, main_position=None, alpha=1.0, text=True, label=None):
    cx = 1
    cy = 1
    x = 1
    
    if main_position is not None:
        rate = FieldPlayer(name="", age=20, now_year=1900, position=main_position, 
                           pace=pace*100, shooting=sho*100, passing=pas*100, dribbling=dri*100,
                           defending=de*100, physicality=phy*100,
                           injury_possibility=0)
        rate = rate.main_rate
    else:
        rate = ""
    
    if label is None:
        plt.plot([cx, cx+x*phy*math.sqrt(3)/2], [cy+x*pace, cy+x*phy/2], color, alpha=alpha)
        plt.plot([cx+x*de*math.sqrt(3)/2, cx+x*phy*math.sqrt(3)/2], [cy-x*de/2, cy+x*phy/2], color, alpha=alpha)
        plt.plot([cx+x*de*math.sqrt(3)/2, cx], [cy-x*de/2, cy-x*dri], color, alpha=alpha)
        plt.plot([cx-x*pas*math.sqrt(3)/2, cx], [cy-x*pas/2, cy-x*dri], color, alpha=alpha)
        plt.plot([cx-x*pas*math.sqrt(3)/2, cx-x*sho*math.sqrt(3)/2], [cy-x*pas/2, cy+x*sho/2], color, alpha=alpha)
        plt.plot([cx, cx-x*sho*math.sqrt(3)/2], [cy+x*pace, cy+x*sho/2], color, alpha=alpha)
    else:
        plt.plot([cx, cx+x*phy*math.sqrt(3)/2], [cy+x*pace, cy+x*phy/2], color, alpha=alpha, label=label+f" ({rate})")
        plt.plot([cx+x*de*math.sqrt(3)/2, cx+x*phy*math.sqrt(3)/2], [cy-x*de/2, cy+x*phy/2], color, alpha=alpha)
        plt.plot([cx+x*de*math.sqrt(3)/2, cx], [cy-x*de/2, cy-x*dri], color, alpha=alpha)
        plt.plot([cx-x*pas*math.sqrt(3)/2, cx], [cy-x*pas/2, cy-x*dri], color, alpha=alpha)
        plt.plot([cx-x*pas*math.sqrt(3)/2, cx-x*sho*math.sqrt(3)/2], [cy-x*pas/2, cy+x*sho/2], color, alpha=alpha)
        plt.plot([cx, cx-x*sho*math.sqrt(3)/2], [cy+x*pace, cy+x*sho/2], color, alpha=alpha)

    if text == True:
        plt.text(cx, cy+x+0.2, f"Pace", size=9, c=color)
        plt.text(cx+x*math.sqrt(3)/2+0.2, cy+x/2, f"Physical", size=9, c=color)
        plt.text(cx+x*math.sqrt(3)/2+0.2, cy-x/2, f"defence", size=9, c=color)
        plt.text(cx, cy-x-0.2, f"driblling", size=9, c=color)
        plt.text(cx-x*math.sqrt(3)/2-0.6, cy-x/2, f"pass", size=9, c=color)
        plt.text(cx-x*math.sqrt(3)/2-0.6, cy+x/2, f"shooting", size=9, c=color)

    plt.xlim([cx-x-0.3, cx+x])
    plt.ylim([cy-x, cy+x])
    plt.axis("off")