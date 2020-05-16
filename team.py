""" This class will manage the team in a match.
A team is made up of 20 players: 12 forwards, 6 defensemen, a goalie and a 
back-up goalie.
The forwards are configured into 4 lines and the defensemen into 3 pairs
There is always 1 forward line, 1 defensive pairing and 1 goalie on the ice

Iteration 1: Just spit out a basic stat to make sure that the simulation class
can use this 
"""

class Team:
    
    def __init__(self, default_stat_score):
        """ constructor
        Arguments:
            default_stat_score {int} -- Default stat score to return, this is for
            development purposes and will be removed
        """
        self.default_stat_score = default_stat_score

    @property
    def face_off(self):
        return self.default_stat_score

    @property
    def overall_offensive(self):
        return self.default_stat_score

    @property
    def overall_defensive(self):
        return self.default_stat_score

    @property
    def shooting(self):
        return self.default_stat_score

    @property
    def blocking(self):
        return self.default_stat_score

if __name__ == "__main__":
    home_team = Team(63)
    print(f"face_off {home_team.face_off}")
    print(f"overall_defensive {home_team.overall_defensive}")
    print(f"overall_offensive {home_team.overall_offensive}")
    print(f"shooting {home_team.shooting}")
    print(f"blocking {home_team.blocking}")