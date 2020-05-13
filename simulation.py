from collections import namedtuple
from pathlib import Path
from random import randint
from time import sleep

import logging

class Simulation:

    # test time lengths
    FACE_OFF_TIME = 2
    RECLAIMING_THE_PUCK_TIME = 3
    MOVING_THE_PUCK_TIME = 5
    SECURING_A_SHOT_TIME = 5
    TAKING_A_SHOT_TIME = 3

    FUMBLE = (99, 100)
    CRITICAL = (1, 2)

    SECURING_A_SHOT_BONUS = 10

    # in seconds
    time_remaining = 600  # 3600

    in_play = False  # Only True of False
    is_breakaway = False  # Only True or False
    is_shooting = False  # Only True or False

    is_securing_a_shot_bonus = False

    current_zone = None  # None or 1-4
    puck_possession = -1  # -1, HOME or AWAY

    home_score = 0
    away_score = 0

    home_sog = 0
    away_sog = 0

    home_save = 0
    away_save = 0

    HOME = 0
    AWAY = 1

    ATTACKER = 1
    DEFENDER = 0

    # this is temporary, all contests will use these numbers
    home_stat = 70
    away_stat = 70

    def __init__(self, home_stat, away_stat):
        self.home_stat = home_stat
        self.away_stat = away_stat
        logfile = Path(__file__, '..', 'simulation.log').resolve()
        logging.basicConfig(
            level=logging.DEBUG,
            format=' %(asctime)s -  %(levelname) s -  %(message)s',
            filename=logfile
        )

    def __repr__(self):
        return f"Simulation({self.home_stat}, {self.away_stat})"

    def __str__(self):
        output = f"The puck is {'not ' if not self.in_play else ''}in play\n"
        if self.in_play:
            if self.puck_possession == -1:
                puck_possession = "No one"
            elif self.puck_possession == self.HOME:
                puck_possession = "Home"
            elif self.puck_possession == self.AWAY:
                puck_possession = "Away"
            output += f"{puck_possession} is in possession of the puck.\n"
        output += f"Zone: {self.current_zone}\n"
        output += f"Time Remaining: {self.time_remaining}; Home: {self.home_score} Away: {self.away_score}\n"
        return(output)

    @property
    def attacking_zone(self):
        if self.puck_possession == self.HOME:
            return 4
        elif self.puck_possession == self.AWAY:
            return 1
        else:
            return None  # this should probably be an error

    @property
    def defensive_zone(self):
        if self.puck_possession == self.HOME:
            return 1
        elif self.puck_possession == self.AWAY:
            return 4
        else:
            return None

    @property
    def defense_side_neutral(self):
        if self.puck_possession == self.HOME:
            return 2
        elif self.puck_possession == self.AWAY:
            return 3
        else:
            return None

    @property
    def attack_side_neutral(self):
        if self.puck_possession == self.HOME:
            return 3
        elif self.puck_possession == self.AWAY:
            return 2
        else:
            return None

    def puck_possession_flip(self):
        self.puck_possession = self.puck_possession * -1 + 1

    def move_forward(self):
        ''' 
        should only be called when someone is in posession of the puck and
        the puck is in a zone (1-4)
        This will move the forward one zone, either +1 for home team or -1
        for the away team
        if the team in possession is already in the attacking zone then
        they will get an automatic securing of the shot
        '''

        if self.current_zone == 0:
            print(f"Move froward: {self.current_zone}")
            raise Exception  # This should never happen
        if self.puck_possession == -1:
            print(f"Move froward - Possession: {self.current_zone}")
            print(self)
            raise Exception  # This should never happen

        if self.current_zone == self.attacking_zone:
            self.is_shooting = True
        else:
            self.puck_possession_flip

    def contest(self, attack: int, defense: int) -> int:
        '''
        determines a winner between two sides
        both sides roll d100 under their stat
        if they roll under the stat it is a success
        additionally if a number in self.CRITICAL is rolled then it is
        considered a critical success.  If a number in self.FUMBLE is
        rolled it is considered a critical failure or loser fumble
        '''
        result_type = namedtuple("result_type", "winner, winner_critical, loser_fumble")

        winner = -1
        winner_critical = False
        loser_fumble = False

        attack_roll = randint(1, 100)
        defense_roll = randint(1, 100)
        attack -= attack_roll
        defense -= defense_roll

        if defense > 0 and defense >= attack:
            winner = self.DEFENDER
            if defense_roll in self.CRITICAL:
                winner_critical = True
            if attack_roll in self.FUMBLE:
                loser_fumble = True

        elif attack > 0 and attack > defense:
            winner = self.ATTACKER
            if attack_roll in self.CRITICAL:
                winner_critical = True
            if defense_roll in self.FUMBLE:
                loser_fumble = True

        results = result_type(winner, winner_critical, loser_fumble)
        return results

    def face_off(self):
        logging.debug("FaceOff")
        # Center Face Off
        # Success - Take posession of the puck
        # Critical Success - move forward one zone
        # Opponent Fumbles - Breakaway

        # end zone face off
        # success - take possession of the puck
        # critical success
        #   attacker - +10 to next securing shot 
        #   defender - moves forward one zone
        # oponent fumbles
        #   attacker - is_shooting = True
        #   defender - breakaway

        results = self.contest(self.away_stat, self.home_stat)
        self.puck_possession = results.winner
        self.in_play = True
        if results.winner != -1:
            if self.current_zone == None:
                self.current_zone = self.defense_side_neutral
            if results.loser_fumble:
                self.current_zone = self.attacking_zone
                self.is_shooting = True
            elif results.winner_critical:
                if self.current_zone == 0:
                    self.current_zone = self.attack_side_neutral
                elif self.current_zone == self.attacking_zone:
                    self.is_securing_a_shot_bonus = True
                elif self.current_zone == self.defensive_zone:
                    self.current_zone = self.defense_side_neutral
                else:
                    print(self)
                    print(f"FaceOff: {self.current_zone}")
                    raise Exception  # this SHOULD never happen
            else:
                if self.current_zone == 0:
                    self.current_zone = self.defense_side_neutral

        self.time_remaining -= self.FACE_OFF_TIME

    def reclaiming_the_puck(self):
        logging.debug("reclaiming the puck!")
        results = self.contest(self.away_stat, self.home_stat)
        self.puck_possession = results.winner
        if results.winner != -1:
            if self.current_zone == None:
                self.current_zone = self.defense_side_neutral
            if results.loser_fumble:
                self.is_shooting == True
                if self.current_zone != self.attacking_zone:
                    self.current_zone = self.attacking_zone
            elif results.winner_critical:
                if self.current_zone == self.attacking_zone:
                    self.is_securing_a_shot_bonus = True
                else:
                    self.move_forward()
                            

    def moving_the_puck(self):
        logging.debug("moving the puck!")
        if self.puck_possession == self.HOME:
            attack = self.home_stat
            defense = self.away_stat
        else:
            attack = self.away_stat
            defense = self.home_stat

        results = self.contest(attack, defense)
        if results.winner == self.ATTACKER:
            # attacker moves puck
            self.move_forward()
            if results.loser_fumble:
                self.current_zone = self.attacking_zone
                self.is_shooting = True
            elif results.winner_critical:
                self.move_forward()
        elif results.winner == self.DEFENDER:
            # movement halted
            if results.loser_fumble:
                # defense has a breakaway
                self.puck_possession_flip()
                self.current_zone = self.attacking_zone
                self.is_shooting = True
            elif results.winner_critical:
                self.puck_possession_flip()

        self.time_remaining -= self.MOVING_THE_PUCK_TIME

    def securing_a_shot(self):
        logging.debug("securing a shot!")
        if self.puck_possession == self.HOME:
            attack = self.home_stat
            defense = self.away_stat
        else:
            attack = self.away_stat
            defense = self.home_stat

        results = self.contest(attack, defense)

        if results.winner == self.ATTACKER:
            self.is_shooting = True
            if results.loser_fumble:
                self.shot_bonus_multiplier = 1
            elif results.winner_critical:
                self.shot_bonus_multiplier = 2
                
        elif results.winner == self.DEFENDER:
            if results.loser_fumble:
                self.puck_possession_flip()
                self.move_forward()
            elif results.winner_critical:
                self.puck_possession_flip()

        self.time_remaining -= self.SECURING_A_SHOT_TIME

    def take_a_shot(self):
        logging.debug("take a shot!")
        self.is_shooting = False
        if self.puck_possession == self.HOME:
            attack = self.home_stat
            defense = self.away_stat
        else:
            attack = self.away_stat
            defense = self.home_stat

        results = self.contest(attack, defense)

        if results.winner == self.ATTACKER:
            # score
            if self.puck_possession == self.HOME:
                self.home_score += 1
                self.home_sog += 1
            else:
                self.away_score += 1
                self.away_sog += 1
            self.in_play = False
            self.puck_possession = -1
            self.current_zone = None
            '''TODO Might be fun to consider a winner_critical to be a
            highlight of the game'''

        elif results.winner == self.DEFENDER:
            if results.loser_fumble:
                self.puck_possession_flip()
                self.move_forward()
            elif results.winner_critical:
                self.puck_possession_flip()
            else:
                self.in_play = False
                self.puck_possession = -1

                if self.puck_possession == self.HOME:
                    self.home_sog += 1
                    self.away_save += 1
                else:
                    self.home_save += 1
                    self.away_sog += 1

        else:
            #puck is loose
            self.puck_possession = -1

        self.time_remaining -= self.TAKING_A_SHOT_TIME

    def run(self):

        # game loop
        while self.time_remaining > 0:
            logging.debug(self)

            if self.in_play is False:
                self.face_off()

            elif self.puck_possession == -1:
                self.reclaiming_the_puck()

            elif self.is_shooting is True:
                self.take_a_shot()

            elif (
                self.puck_possession == self.HOME and self.current_zone == 4
            ) or (
                self.puck_possession == self.AWAY and self.current_zone == 1
            ):
                self.securing_a_shot()

            else:
                self.moving_the_puck()

        self.print_results()

    def print_results(self):
        output = f"{' '*10}Home{' '*6}Away\n"
        output += f"Score{' '*5}{str(self.home_score):10s}{str(self.away_score):10s}\n"
        output += f"SOG{' '*7}{str(self.home_sog):10s}{str(self.away_sog):10s}\n"
        output += f"Saves{' '*5}{str(self.home_save):10s}{str(self.away_save):10s}\n"
       
        print(output)

if __name__ == "__main__":
    s = Simulation(75,75)
    s.run()
