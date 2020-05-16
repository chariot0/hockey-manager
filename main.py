from simulation import Simulation
from team import Team

home_team = Team(77)
away_team = Team(73)

# print(f"face_off {home_team.face_off}")
# print(f"overall_defensive {home_team.overall_defensive}")
# print(f"overall_offensive {home_team.overall_offensive}")
# print(f"shooting {home_team.shooting}")
# print(f"blocking {home_team.blocking}")

s = Simulation(home_team, away_team)
# s.in_play = True
# s.puck_possession = s.HOME
# s.current_zone = s.attacking_zone
# s.securing_a_shot()
# s.face_off()
# s.moving_the_puck()
print(s)
s.run()
