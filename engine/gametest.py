#!/usr/bin/python

import sys, time
import engine, botplayer
import view
import csv

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

viewg = view.GameView(game)

with open('pruebas.csv', mode='w') as pruebas:
    w_pruebas = csv.writer(pruebas, delimiter=',',quotechar='"', quoting = csv.QUOTE_MINIMAL)
    
    cabecera = []
    cabecera.append('ronda')
    for act in range(len(bots)):
        cabecera.append(game.players[act].name)

    w_pruebas.writerow(cabecera)

    for iteration in range(len(bots)):
        config = engine.GameConfig(cfg_file)
        game = engine.Game(config, len(bots))
        order = []
        for o in range(len(bots)):
            new_o = iteration + o
            if new_o > (len(bots)-1):
                new_o = new_o - len(bots)
            order.append([o,new_o])
            actors[new_o] = botplayer.BotPlayer(game, new_o, bots[o], debug=DEBUG)
            actors[new_o].initialize()
        viewg = view.GameView(game)
        round = 0
        while round < 501:
            game.pre_round()
            viewg.update()
            for actor in actors:
                actor.turn()
                viewg.update()
            game.post_round()
            print "########### ROUND %d SCORE:" % round,
            for i in range(len(bots)):
                # print "P%d: %d" % (i, game.players[i].score),
                print "%s: %d" % (game.players[i].name, game.players[i].score),
            print
            time.sleep(0.5)
            round += 1
            viewg.update()
        linea = []
        linea.append(iteration)
        for bot in range(len(bots)):
            linea.append(game.players[order[bot][1]].score)
        w_pruebas.writerow(linea)



viewg.update()
