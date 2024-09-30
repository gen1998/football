import pandas as pd
import os

PLAYER_NAMES = []

def load_names():
    global PLAYER_NAMES
    current_dir = os.path.dirname(__file__)
    df_name = pd.read_csv(os.path.join(current_dir, "../data/csv/NationalNames.csv"))
    PLAYER_NAMES = list(df_name[df_name.Gender=='M'].Name.sample(30000))