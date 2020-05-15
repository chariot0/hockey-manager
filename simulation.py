''' The simulation class will simulate a hockey match betweeen two teams
through a series of tests.
'''

from collections import namedtuple
from pathlib import Path
from random import randint
from time import sleep

import logging


class Simulation:

    # length of time for the tests
    FACE_OFF_TIME = 2
    RECLAIMING_THE_PUCK_TIME = 3
    MOVING_THE_PUCK_TIME = 5
    SECURING_A_SHOT_TIME = 5
    TAKING_A_SHOT_TIME = 3

    # used in the contest method
    FUMBLE = (99, 100)
    CRITICAL = (1, 2)

    HOME = 0
    AWAY = 1

    DEFENDER = 0
    ATTACKER = 1

    SECURING_A_SHOT_BONUS = 10
    is_securing_a_shot_bonus = False

    # in seconds
    time_remaining =  3600

    # multiple states being managed
    current_zone = None  # None or 1-4
    in_play = False  # Only True of False
    is_breakaway = False  # Only True or False
    is_shooting = False  # Only True or False
    puck_possession = None # None, HOME or AWAY

    # game stats
    home_score = 0
    away_score = 0

    home_sog = 0
    away_sog = 0

    home_save = 0
    away_save = 0

    def __init__(self, home_stat, away_stat):
        """ This currently accepts only one stat per team.  This should
        eventually accept a team object for each team which will then
        serve the appropriate stat when asked.

        Arguments:
            home_stat {int} -- [stat used for home team]
            away_stat {int} -- [stat used for away team]
        """
        logfile = Path(__file__, '..', 'simulation.log').resolve()
        logging.basicConfig(
            level=logging.DEBUG,
            format=' %(asctime)s -  %(levelname) s -  %(message)s',
            filename=logfile,
            filemode="w"
        )
        # These will go away when we use Team objedts
        self.home_stat = home_stat
        self.away_stat = away_stat


    def __repr__(self):
        return f"Simulation({self.home_stat}, {self.away_stat})"

    def __str__(self):
        output = f"Time Remaining: {self.time_remaining}; {'Not i' if not self.in_play else 'I'}n play.  "
        if self.in_play:
            if self.puck_possession == None:
                puck_possession = "No one"
            elif self.puck_possession == self.HOME:
                puck_possession = "Home"
            elif self.puck_possession == self.AWAY:
                puck_possession = "Away"
            output += f"{puck_possession} in possession. "
        output += f"Zone: {self.current_zone} "
        # output += f"Time Remaining: {self.time_remaining}; Home: {self.home_score} Away: {self.away_score} "
        return(output)

    @property
    def attacking_zone(self):
        if self.puck_possession == self.HOME:
            return 4
        elif self.puck_possession == self.AWAY:
            return 1
        else:
            return None

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
        should only be called when someone is in posession of the puck 
        This will move the puck forward one zone
        if the team in possession is already in the attacking zone then
        they will get a securing a shot bonus
        '''

        if self.current_zone == 0:
            print(f"Move froward: {self.current_zone}")
            raise Exception  # This should never happen
        if self.puck_possession == None:
            print(f"Move froward - Possession: {self.current_zone}")
            print(self)
            raise Exception  # This should never happen

        if self.current_zone == self.attacking_zone:
            self.is_securing_a_shot_bonus = True
        elif self.puck_possession == self.HOME:
            self.current_zone += 1
        else:
            self.current_zone -= 1

    def contest(self, attack: int, defense: int) -> int:
        """ determines a winner between two sides
        both sides roll d100 under their stat
        if they roll under the stat it is a success
        additionally if a number in self.CRITICAL is rolled then it is
        considered a critical success.  If a number in self.FUMBLE is
        rolled it is considered a critical failure or loser fumble
        """
        logging.debug(f"contest({attack}, {defense})")

        result_type = namedtuple("result_type", "winner, winner_critical, loser_fumble")

        winner = None
        winner_critical = False
        loser_fumble = False

        attack_roll = randint(1, 100)
        defense_roll = 80  # randint(1, 100)
        attack_result = attack - attack_roll
        defense_result = defense - defense_roll

        logging.debug(f"Attack - Roll: {attack_roll}; Result: {attack_result}")
        logging.debug(f"Defense - Roll: {defense_roll}; Result: {defense_result}")

        if defense_result > 0 and defense_result >= attack_result:
            winner = self.DEFENDER
            if defense_roll in self.CRITICAL:
                winner_critical = True
            if attack_roll in self.FUMBLE:
                loser_fumble = True

        elif attack_result > 0 and attack_result > defense_result:
            winner = self.ATTACKER
            if attack_roll in self.CRITICAL:
                winner_critical = True
            if defense_roll in self.FUMBLE:
                loser_fumble = True

        results = result_type(winner, winner_critical, loser_fumble)
        logging.debug(results)
        return results

    def face_off(self):
        """ when puck is not in play, a face off is done to start play and
        try to determine who gets possession of the puck 
        """
        logging.debug("face_off()")

        # This should only be called when self.puck_possession = None
        if self.puck_possession is not None:
            logging.warning(f"FaceOff called while someone had possession of the puck: {self.puck_possession}")
            return

        results = self.contest(self.away_stat, self.home_stat)
        # results = self.contest(self.HomeTeam.FaceOff, self.AwayTeam.FaceOff)
        self.puck_possession = results.winner
        self.in_play = True
        if results.winner is not None:
            if self.current_zone == None:
                # Center-Ice FaceOff
                self.current_zone = self.defense_side_neutral
            if results.loser_fumble:
                self.current_zone = self.attacking_zone
                self.is_shooting = True  # breakaway!
            elif results.winner_critical:
                self.move_forward()
            else:
                if self.current_zone == 0:
                    self.current_zone = self.defense_side_neutral

        self.time_remaining -= self.FACE_OFF_TIME

    def reclaiming_the_puck(self):
        """ when the puck is in play, but the puck is loose """
        logging.debug("reclaiming_the_puck()")
        results = self.contest(self.away_stat, self.home_stat)
        # results = self.contest(self.AwayTeam.overall_offensive, self.HomeTeam.overall_offensive)
        self.puck_possession = results.winner
        if results.winner is not None:
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
        """ puck in play, puck is in possession by a team """
        logging.debug("moving_the_puck()")
        if self.puck_possession == self.HOME:
            attack = self.home_stat
            defense = self.away_stat
        else:
            attack = self.away_stat
            defense = self.home_stat

        results = self.contest(attack, defense)
        #results = self.contest(self.___.overall_offensive, self.___.overall_defensive)
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
        """ puck is in play, and team possessing the puck is in their
        attacking zone.  securing a shot will determine if the team can
        get a shot on goal
        """
        logging.debug("securing_a_shot()")
        if self.puck_possession == self.HOME:
            attack = self.home_stat
            defense = self.away_stat
        else:
            attack = self.away_stat
            defense = self.home_stat

        results = self.contest(attack, defense)
        #results = self.contest(self.___.overall_offensive, self.___.overall_defensive)

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
        logging.debug("take_a_shot()")
        self.is_shooting = False
        if self.puck_possession == self.HOME:
            attack = self.home_stat
            defense = self.away_stat
        else:
            attack = self.away_stat
            defense = self.home_stat

        """instead of calling a single contest this will be split up into two
        rolls.  First by the shooter to see if they can get the puck to the goal.
        If that succeeds a second roll will be done by the goalie to see if they
        block the shot."""
        results = self.contest(attack, defense)
        #results = self.contest(self.___.shooting, self.___.blocking)

        if results.winner == self.ATTACKER:
            # score
            if self.puck_possession == self.HOME:
                self.home_score += 1
                self.home_sog += 1
            else:
                self.away_score += 1
                self.away_sog += 1
            self.in_play = False
            self.puck_possession = None
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
                self.puck_possession = None

                if self.puck_possession == self.HOME:
                    self.home_sog += 1
                    self.away_save += 1
                else:
                    self.home_save += 1
                    self.away_sog += 1

        else:
            #puck is loose
            self.puck_possession = None

        self.time_remaining -= self.TAKING_A_SHOT_TIME

    def clearing_the_puck(self):
        pass

    def run(self):

        # game loop
        while self.time_remaining > 0:
            logging.debug(self)

            if self.in_play is False:
                self.face_off()

            elif self.puck_possession == None:
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
