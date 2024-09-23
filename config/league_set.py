import sys
sys.path.append("../")

from src.object.league import League
from src.object.proleague import ProLeague
from src.create import create_team
from config.setting import LEAGUE_LEVEL_DICT

def create_Proleague(name, name_competition,
                     league_name_list, league_display_name_list, 
                     tier_list, team_names, 
                     df_name_list, category_list):
    leagues = []
    for n, nd, tier, cat in zip(league_name_list, league_display_name_list, tier_list, category_list):
        LL = LEAGUE_LEVEL_DICT[tier]
        teams = create_team(20, 
                            team_names[n].values, 
                            df_name_list, 
                            mean_rate=LL["mean_newplayer_rate"], 
                            min_rate=LL["min_starting_rate"],
                            max_rate=LL["max_starting_rate"],
                            age_mean=LL["age_initial_mean"]
                            )
        relegation_num = 3
        promotion_num = 3
        if cat=='top':
            promotion_num = 0
        elif cat=='lowest':
            relegation_num = 0

        L_class = League(name=nd,
                    teams=teams,
                    num=20,
                    category=cat,
                    league_level=LL['league_level'],
                    df_name_list=df_name_list,
                    relegation_num=relegation_num,
                    promotion_num=promotion_num,
                    min_rate=LL["min_starting_rate"],
                    max_rate=LL["max_starting_rate"],
                    mean_rate=LL["mean_newplayer_rate"],
                    min_starting_mean_rate=LL["min_starting_rate_mean"],
                    max_starting_mean_rate=LL["max_starting_rate_mean"],
                    min_bench_mean_rate=LL["min_bench_rate_mean"],
                    max_bench_mean_rate=LL["max_bench_rate_mean"],
                    bench_num=9
                    )
        leagues.append(L_class)

    PL = ProLeague(name=name, leagues=leagues, df_name_list=df_name_list, competition_name=name_competition)
    
    for index, l in enumerate(PL.leagues):
        l.country_uuid = PL.uuid
        if l.category != "top":
            l.upperleague_uuid = PL.leagues[index-1].uuid
        if l.category != "lowest":
            l.lowerleague_uuid = PL.leagues[index+1].uuid
            
    return PL