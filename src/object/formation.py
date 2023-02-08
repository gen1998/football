class Formation:
    def __init__(self, name, formation, formation_priority, 
                 formation_num, formation_shooting_rate, 
                 formation_assist_rate, formation_tired_vitality):
        # 固定値
        self.name = name
        self.formation = formation
        self.formation_priority = formation_priority
        self.formation_num = formation_num
        self.formation_shooting_rate = formation_shooting_rate
        self.formation_assist_rate = formation_assist_rate
        self.formation_tired_vitality = formation_tired_vitality
        self.formation_flat = self.__flat_formation()

        # 変化値
        self.players = None
        self.players_flat = []
        self.main_rate_formation = {}
        self.mean_rate = 0

        # 関数
        self.set_players_position()
    
    def __flat_formation(self):
        output = []
        for _, value in self.formation.items():
            output.extend(value)
        output.append("GK")
        return output
    
    def set_players_position(self):
        output = {}
        for ff in self.formation_flat:
            output[ff] = []
        output["GK"] = []
        self.players = output

    def set_main_rate_formation(self):
        self.main_rate_formation = {}

        for pos in self.formation_flat:
            self.main_rate_formation[pos] = []

    # チームレートの計算
    def cal_team_rate(self):
        # ポジション領域(place)ごとのレート
        place_list = ['ATT', 'MID', 'DEF']
        self.team_rate = {}
        sum_rate_all = 0

        for place in place_list:
            sum_rate_place = 0
            num = 0
            position = self.formation[place]
            for pos in position:
                pos_players = self.players[pos]
                for pp in pos_players:
                    sum_rate_place += pp.position_all_rate[pos]
                    sum_rate_all += pp.position_all_rate[pos]
                    num += 1
            sum_rate_place /= num
            self.team_rate[place] = sum_rate_place
        
        self.team_rate["GK"] = self.players["GK"][0].main_rate
        
        sum_rate_all += self.players["GK"][0].main_rate
        self.team_rate["ALL"] = sum_rate_all/11

"""   
    def print_formation(self):
        for pos in self.formation_flat:
            player = self.players[pos]
            if pos == "GK":
                player = player[0]
                print(player.name, '  Rate:', player.main_rate, '(', player.main_position, ')')
                print('-'*25)
                print('  DIV ', player.diving, '  REF ', player.reflexes)
                print('  HAN ', player.handling, '  SPE ', player.speed)
                print('  KIC ', player.kicking, '  POS ', player.positioning)
                print()
            else:
                for player_ in player:
                    print(player_.name, '  Rate:', player_.position_all_rate[player_.partification_position], '(', player_.partification_position, ')')
                    print('-'*25)
                    print('  PAC ', player_.pace, '  DRI ', player_.dribbling)
                    print('  SHO ', player_.shooting, '  DEF ', player_.defending)
                    print('  PAS ', player_.passing, '  PHY ', player_.physicality)
                    print()
    
    def print_formation_(self):
        for pos in self.formation_flat:
            player = self.main_rate_formation[pos]
            if len(player) < 1:
                print('配置なし  Rate:' '(', pos, ')')

            if pos == "GK":
                player = player[0]
                print(player.name, '  Rate:', player.main_rate, '(', player.main_position, ')')
            else:
                for player_ in player:
                    print(player_.name, '  Rate:', player_.position_all_rate[pos], '(', pos, ')')
"""