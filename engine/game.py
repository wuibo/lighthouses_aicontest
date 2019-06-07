#!/usr/bin/python

import sys, time
import engine, botplayer
import view

cfg_file = sys.argv[1]
bots = sys.argv[2:]
DEBUG = False

##se le pasa el mapa como fichero de configuracion
config = engine.GameConfig(cfg_file)
##la configuracion y la cantidad de jugadores
game = engine.Game(config, len(bots))
##Bots que ejecutan la IA del jugador y se comunican
actors = [botplayer.BotPlayer(game, i, cmdline, debug=DEBUG) for i, cmdline in enumerate(bots)]

for actor in actors:
    actor.initialize()

view = view.GameView(game)

round = 0
while True:
    game.pre_round()
    view.update()
    for actor in actors:
        actor.turn()
        view.update()
    game.post_round()
    print "########### ROUND %d SCORE:" % round,
    for i in range(len(bots)):
        print "P%d: %d" % (i, game.players[i].score),
    print
    round += 1

view.update()
