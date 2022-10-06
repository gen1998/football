import numpy as np
import pandas as pd

import random

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
