import sys
sys.path.append("../")

from src.object.league import League
from src.object.proleague import ProLeague
from src.create import create_team
from config.setting import LEAGUE_LEVEL_DICT

def create_Proleague(name, name_competition,
                     league_display_name_list, 
                     tier_list, team_names, league_num,
                     category_list):
    leagues = []
    team_names = team_names[name]
    for nd, tier, cat, l_num in zip(league_display_name_list, tier_list, category_list, league_num):
        LL = LEAGUE_LEVEL_DICT[tier]
        teams = create_team(l_num, 
                            team_names[:l_num], 
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
                    num=l_num,
                    category=cat,
                    league_level=LL['league_level'],
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
        for t in L_class.teams:
            t.league_uuid = L_class.uuid
            t.league_name = L_class.name
        leagues.append(L_class)
        team_names = team_names[l_num:]

    PL = ProLeague(name=name, leagues=leagues, competition_name=name_competition)
    
    for index, l in enumerate(PL.leagues):
        l.country_uuid = PL.uuid
        if l.category != "top":
            l.upperleague_uuid = PL.leagues[index-1].uuid
            l.upperleague_name = PL.leagues[index-1].name
        if l.category != "lowest":
            l.lowerleague_uuid = PL.leagues[index+1].uuid
            l.lowerleague_name = PL.leagues[index+1].name
            
    return PL