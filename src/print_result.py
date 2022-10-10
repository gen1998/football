import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import math

from src.object import FieldPlayer

from IPython.core.display import display

import uuid

def print_player(ProLeague, all_member, uuid_):
    member = all_member[all_member.uuid==uuid.UUID(f"{uuid_}")]
    display(member[['名前', '年齢', '生まれ年', '成長タイプ']])

    output = ProLeague.players_result
    output = output[output.uuid==uuid.UUID(f"{uuid_}")]
    #output = output[output["分類"]=="リーグ"]
    output = output.reset_index(drop=True)
    t_name_b = ""
    plt.figure(figsize = (12, 3)) # 図のサイズ指定
    plt.subplot(1, 4, 1)
    plt.axis([0,15,0,15]) 
    plt.axis("off")
    count = 0
    for i, row in output.iterrows():
        t_name = row["チーム"]
        if i==0:
            t_name_b = row["チーム"]
            t_s = row["年度"]
            t_i = 0
        if t_name!=t_name_b:
            result_txt = f'{output.loc[t_i:i, "試合数"].sum()}({output.loc[t_i:i, "goal"].sum()})'
            if t_s == row["年度"]-1:
                plt.text(0, 15-count, f"  {t_s}   {t_name_b.ljust(10)} {result_txt}")
            else:
                plt.text(0, 15-count, f"  {t_s}-{row['年度']-1}   {t_name_b.ljust(10)} {result_txt}")
            t_s = row["年度"]
            t_i = i
            count += 1
        if i==len(output)-1:
            result_txt = f'{output.loc[t_i:i, "試合数"].sum()}({output.loc[t_i:i, "goal"].sum()})'
            if t_s == row["年度"]:
                plt.text(0, 15-count, f"  {t_s}   {t_name.ljust(10)} {result_txt}")
            else:
                plt.text(0, 15-count, f"  {t_s}-{row['年度']}   {t_name.ljust(10)} {result_txt}")
        t_name_b = t_name

    plt.subplot(1, 4, 2)
    plt.axis([0,15,0,15]) 
    plt.axis("off")
    count=0
    for row in output["賞"]:
        if row != "":
            plt.text(0, 15-count, f"{row}")
            count += 1

    plt.subplot(1, 4, 3)
    plt.plot(output["年齢"], output["Rate"])
    plt.title("Rate変動")
    plt.xlim([output["年齢"].min()-2, output["年齢"].max()+2])
    plt.ylim([output["Rate"].min()-3, output["Rate"].max()+3])
    plt.xlabel("年齢")
    plt.ylabel("Rate")

    if all_member[all_member.uuid == uuid.UUID(uuid_)]["進退"].values[0] == "引退":
        player = [p for p in ProLeague.retire_players if p.uuid == uuid.UUID(uuid_)][0]
    else:
        l = [l for l in ProLeague.leagues if l.name==all_member[all_member.uuid == uuid.UUID(uuid_)]["リーグ"].values[0]][0]
        t = [t for t in l.teams if t.name==all_member[all_member.uuid == uuid.UUID(uuid_)]["チーム"].values[0]][0]
        player = [p for p in t.affilation_players if p.uuid == uuid.UUID(uuid_)][0]
    plt.subplot(1, 4, 4)
    print_rate(player)

    plt.show()

    output = ProLeague.players_result
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