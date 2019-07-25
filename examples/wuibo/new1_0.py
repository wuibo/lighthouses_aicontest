#!/usr/bin/python
# -*- coding: utf-8 -*-

import random, sys, math, geom
import interface
import utils
import numpy as np

class RandBot(interface.Bot):
    """Bot que juega aleatoriamente."""
    NAME = "WuiboEE27_10"
    E_DIST = 5
    E_TURN = 6
    E_FRAC = 3
    E_LOSS = 10
    E_PROB = 0.1

    def __init__(self,init_state):
        """Inicializar el bot"""
        self.player_num = init_state["player_num"]
        self.map = init_state["map"]
        self.maxy = len(self.map)
        self.maxx = len(self.map[0])
        self.maxdist = self.maxx * self.maxy # * self.maxx * self.maxy
        self.lighthouses = map(tuple,init_state["lighthouses"])
        self.light_count = len(self.lighthouses)
        self.light_dict = dict()
        self.turn = 0
        self.f_turn = 0

        """rellenar los faros + energia"""
        self.energi = np.full((self.maxy,self.maxx),0)
        for pos in self.lighthouses:
            """turnos a faro"""
            self.light_dict[pos] = utils.lighthouse(pos,self.maxy,self.maxx,self.flood_dist(pos))
            """energia por turno"""
            for y in xrange(max(0,pos[1]-self.E_DIST+1),min(pos[1]+self.E_DIST,self.maxy-1)):
                for x in xrange(max(0,pos[0]-self.E_DIST+1),min(pos[0]+self.E_DIST,self.maxx-1)):
                    dist = geom.dist(pos, (x,y))
                    delta = int(math.floor(self.E_DIST-dist))
                    if delta > 0 and self.map[y][x] == 1:
                        self.energi[y][x] += delta


        # crear movimientos
        self.l_move = []
        self.l_move.append([-1,-1])
        self.l_move.append([-1,0])
        self.l_move.append([-1,+1])
        self.l_move.append([0,+1])
        self.l_move.append([+1,+1])
        self.l_move.append([+1,0])
        self.l_move.append([+1,-1])
        self.l_move.append([0,-1])

        """Cargar triangulos"""
        tri_total = int(math.factorial(self.light_count)/(math.factorial(3)*math.factorial(self.light_count-3)))
        self.tri = []
        tri_count = 0
        fst = 0
        snd = 1
        cnt = 2
        for i in xrange(tri_total):
            cord1 = self.lighthouses[fst]
            cord2 = self.lighthouses[snd]
            cord3 = self.lighthouses[cnt]
            points = self.triangle_points(cord1,cord2,cord3)
            if points > 0 and self.valid_triangle(cord1,cord2,cord3):
                d12 = self.light_dict[cord1].get_dist(cord2)
                d23 = self.light_dict[cord2].get_dist(cord3)
                d31 = self.light_dict[cord3].get_dist(cord1)
                perimeter = d12 + d23 +d31
                energy = (perimeter + self.E_TURN + perimeter/self.E_FRAC)*self.E_LOSS
                self.tri.append(utils.triangle((cord1,cord2,cord3),points,perimeter,energy))
                self.light_dict[cord1].add_triangle(tri_count)
                self.light_dict[cord2].add_triangle(tri_count)
                self.light_dict[cord3].add_triangle(tri_count)
                tri_count += 1
            """avanzar la cuenta"""
            cnt += 1
            if cnt >= self.light_count:
                snd += 1
                if snd >= self.light_count-1:
                    fst +=1
                    snd = fst +1
                cnt = snd +1

     


    def play(self, state):
        """Jugar: llamado cada turno.
        Debe devolver una acción (jugada)."""
        cx, cy = state["position"]
        lighthouses = dict((tuple(lh["position"]), lh)
                            for lh in state["lighthouses"])

        self.log("Posicion: %s",str((cx,cy)))
        self.turn += 1
        # Ocupación de los faros
        for pos,lh in lighthouses.iteritems():
            if lh["owner"] >= 0 and lh["owner"] != self.player_num:
                self.light_dict[pos].sum_ocupied()

        # Gestión de vista
        view = state["view"]
        view_y = len(view)
        view_x = len(view[0])
        view_cx = view_x/2
        view_cy = view_y/2

        # establecer objetivo
        obj = self.get_objetive(lighthouses,cx,cy)
        self.log("Objetivo: %s Conexion: %s", str(obj.get_next()),str(obj.get_connect()))

        # comprobar energia
        if state["energy"] < obj.get_energy():
            # movimiento por energia
            temp_move = [0,0]
            temp_ener = [0,0]
            for mov in self.l_move:
                ymov_view = view_cy + mov[1]
                xmov_view = view_cx + mov[0]
                t_ener0 = view[ymov_view -1][xmov_view -1]
                t_ener1 = view[ymov_view +0][xmov_view -1]
                t_ener2 = view[ymov_view +1][xmov_view -1]
                t_ener3 = view[ymov_view +1][xmov_view +0]
                t_ener4 = view[ymov_view +1][xmov_view +1]
                t_ener5 = view[ymov_view +0][xmov_view +1]
                t_ener6 = view[ymov_view -1][xmov_view +1]
                t_ener7 = view[ymov_view -1][xmov_view + 0]
                s_ener = max(t_ener0,t_ener1,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
                b_ener = view[ymov_view][xmov_view]
                if b_ener > temp_ener[0]:
                    # mejor energia, cambio
                    temp_move = mov
                    temp_ener = [b_ener,s_ener]
                elif b_ener == temp_ener[0]:
                    # igual comparar segunda
                    if s_ener > temp_ener[1]:
                        temp_move = mov
                        temp_ener = [b_ener,s_ener]
                    elif s_ener == temp_ener[1]:
                        # mirar cual nos acerca más al faro
                        temp_dist = self.light_dict[obj.get_next()].get_dist((cx+temp_move[0],cy+temp_move[1]))
                        act_dist = self.light_dict[obj.get_next()].get_dist((cx+mov[0],cy+mov[1]))
                        if act_dist < temp_dist:
                            temp_move = mov
                            temp_ener = [b_ener,s_ener]
                # en caso de que la temporal se mayor nada
            self.f_turn = 0
            self.log("Move energy. move_x: %s move_y: %s",temp_move[0],temp_move[1])
            return self.move(temp_move[0],temp_move[1])
        else:
            # movimiento al objetivo
            if (cx,cy) == obj.get_next():
                # estamos en el objetivo
                if obj.get_energy() > 0 and self.f_turn == 0:
                    # Atacar
                    self.f_turn = 1
                    a_energy = obj.get_energy() + (state["energy"] - obj.get_energy())/2
                    self.log("Attack: %s" ,a_energy)
                    return self.attack(a_energy)
                else:
                    # no es necesario atacar, conectar
                    self.f_turn = 1
                    self.log("Connect %s",str(obj.get_connect()))
                    return self.connect(obj.get_connect())
            else:
                # no estamos a moverse
                temp_dist = self.maxdist
                temp_ener = 0
                temp_move = (0,0)
                for mov in self.l_move:
                    ymov_view = mov[1] + view_cy
                    xmov_view = mov[0] + view_cx
                    ymov = mov[1] + cy
                    xmov = mov[0] + cx
                    dist = self.light_dict[obj.get_next()].get_dist((xmov,ymov))
                    temp_ener = view
                    if dist < temp_dist:
                        temp_ener = view[ymov_view][xmov_view]
                        temp_move = mov
                        temp_dist = dist
                    elif dist == temp_dist:
                        # comprobar energia
                        ener = view[ymov_view][xmov_view]
                        if ener > temp_ener:
                            temp_ener = ener
                            temp_dist = dist
                            temp_move = mov
                self.f_turn = 0
                self.log("Move objetive mov_x: %s move_y: %s",temp_move[0],temp_move[1])
                return self.move(temp_move[0],temp_move[1])
            

    def flood_dist(self,pos):
        """Devuelve el mapa de distancia (en turnos) a la posición dada"""
        temp_arr = np.full((self.maxy,self.maxx),self.maxdist)
        (ix,iy) = pos
        temp_arr[iy][ix] = 0
        loop = 1
        arr_act = [[ix,iy]]
        arr_nxt = [[-1,-1]]
        checked = arr_act
        while len(arr_nxt) != 0:
            arr_nxt = []
            for cell in arr_act:
                """234"""
                """1*5"""
                """076"""

                """Dir 0"""
                act = [cell[0]-1,cell[1]-1]
                if cell[0]>0 and cell[1]>0:
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 1"""
                act = [cell[0]-1,cell[1]]
                if cell[0]>0:
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 2"""
                act = [cell[0]-1,cell[1]+1]
                if cell[0]>0 and cell[1] < (self.maxy-1):
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 3"""
                act = [cell[0],cell[1]+1]
                if cell[1] < (self.maxy-1):
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 4"""
                act = [cell[0]+1,cell[1]+1]
                if cell[0] < (self.maxx-1) and cell[1] < (self.maxy -1):
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 5"""
                act = [cell[0]+1,cell[1]]
                if cell[0] < (self.maxx-1):
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 6"""
                act = [cell[0]+1,cell[1]-1]
                if cell[0] < (self.maxx-1) and cell[1] > 0:
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]

                """Dir 7"""
                act = [cell[0],cell[1]-1]
                if cell[1] > 0:
                    if self.map[act[1]][act[0]] == 1 and act not in checked:
                        arr_nxt = arr_nxt + [act]
                        temp_arr[act[1]][act[0]] = loop
                        checked = checked + [act]
            arr_act = arr_nxt
            loop += 1
        return temp_arr

    def triangle_points(self,p1,p2,p3):
        """celdas en el triangulo formado por los puntos dados"""
        cells = [j for j in geom.render((p1,p2,p3)) if self.map[j[1]][j[0]]==1]
        return len(cells)

    def valid_triangle(self,p1,p2,p3):
        # 1 con 2
        x10,x11 = sorted((p1[0],p2[0]))
        y10,y11 = sorted((p1[1],p2[1]))
        # 2 con 3
        x20,x21 = sorted((p2[0],p3[0]))
        y20,y21 = sorted((p2[1],p3[1]))
        # 3 con 1
        x30,x31 = sorted((p3[0],p1[0]))
        y30,y31 = sorted((p3[1],p1[1]))
        for lh in self.light_dict.keys():
            if (x10 <= lh[0] <= x11 and y10 <= lh[1] <= y11 and
                    lh not in (p1,p2) and
                    geom.colinear(p1,p2,lh)):
                return False
            if (x20 <= lh[0] <= x21 and y20 <= lh[1] <= y21 and
                    lh not in (p2,p3) and
                    geom.colinear(p2,p3,lh)):
                return False
            if (x30 <= lh[0] <= x31 and y30 <= lh[1] <= y31 and
                    lh not in (p3,p1) and
                    geom.colinear(p3,p1,lh)):
                return False
        return True

    def get_objetive(self,lhs,cx,cy):
        """seleccionar devuelve un objeto objetivo"""
        to = -1
        t_tri = -1 # triangulo temporal
        t_turn = -1 # turnos requeridos temporal
        f_min = self.maxdist
        f_d = -1
        # distancia la faro más cercano
        for pos,lh in lhs.iteritems():
            td = self.light_dict[pos].get_dist((cx,cy))
            if td < f_min and not lh["have_key"]:
                f_min = td
                f_d = pos
        # si no se puede nada por 
        t_obj = utils.objetive(f_d,[],0)

        # recorrer los triangulos
        for tr in self.tri:
            cnd = [] # los propios, con llave o si llave
            otros = [] # el resto
            for clh in tr.get_lighthouses():
                if lhs[clh]["owner"] == self.player_num:
                    if lhs[clh]["have_key"]:
                        cnd = cnd + [[clh,1]]
                    else:
                        cnd = cnd + [[clh,0]]
                else:
                    otros = otros + [clh]

            # self.log("cnd: %s",str(cnd))
            # self.log("otros: %s",str(otros))
            if len(cnd) == 0:
                # controlo 0
                df0 = self.light_dict[otros[0]].get_dist((cx,cy))
                df1 = self.light_dict[otros[1]].get_dist((cx,cy))
                df2 = self.light_dict[otros[2]].get_dist((cx,cy))
                d01 = self.light_dict[otros[0]].get_dist(otros[1])
                d12 = self.light_dict[otros[1]].get_dist(otros[2])
                d20 = self.light_dict[otros[2]].get_dist(otros[0])
                dt0p = df0 + tr.get_perimeter() + 6
                dt01 = df0 + (2*d01) + d20 + 7
                dt02 = df0 + (2*d20) + d01 + 7
                d0 = min(dt0p,dt01,dt02)
                dt1p = df1 + tr.get_perimeter() + 6
                dt10 = df1 + (2*d01) + d12 + 7
                dt12 = df1 + (2*d12) + d01 + 7
                d1 = min(dt1p,dt10,dt12)
                dt2p = df2 + tr.get_perimeter() + 6
                dt20 = df2 + (2*d20) + d12 + 7
                dt21 = df2 + (2*d12) + d20 + 7
                d2 = min(dt2p,dt20,dt21)
                n_turn = min(d0,d1,d2)
                n_connect = []
                if n_turn != d1 and n_turn != d2:
                    n_next = otros[0]
                elif n_turn != d0 and n_turn != d2:
                    n_next = otros[1]
                elif n_turn != d0 and n_turn != d1:
                    n_next = otros[2]
                elif n_turn != d0:
                    if lhs[otros[1]]["energy"] <= lhs[otros[2]]["energy"]:
                        n_next = otros[1]
                    else:
                        n_next = otros[2]
                elif n_turn != d1:
                    if lhs[otros[0]]["energy"] <= lhs[otros[2]]["energy"]:
                        n_next = otros[0]
                    else:
                        n_next = otros[2]
                elif n_turn != d2:
                    if lhs[otros[0]]["energy"] <= lhs[otros[1]]["energy"]:
                        n_next = otros[0]
                    else:
                        n_next = otros[1]
                else:
                    # todos = min
                    e0 = lhs[otros[0]]["energy"]
                    e1 = lhs[otros[1]]["energy"]
                    e2 = lhs[otros[2]]["energy"]
                    if e0 <= e1 and e0 <= e2:
                        n_next = otros[0]
                    elif e1 <= e2:
                        n_next = otros[1]
                    else:
                        n_next = otros[2]
            elif len(cnd) == 1:
                # controlo 1
                if cnd[0][1] == 1:
                    # tengo llave
                    df0 = self.light_dict[otros[0]].get_dist((cx,cy))
                    df1 = self.light_dict[otros[1]].get_dist((cx,cy))
                    dotros = self.light_dict[otros[0]].get_dist(otros[1])
                    dc0 = self.light_dict[otros[0]].get_dist(cnd[0][0])
                    dc1 = self.light_dict[otros[1]].get_dist(cnd[0][0])
                    dt0c = df0 + dc0 + dc1 + 6
                    dt0o = df0 + dotros + dc1 + 5
                    dt0 = min(dt0c,dt0o)
                    dt1c = df1 + dc1 + dc0 + 6
                    dt1o = df1 + dotros + dc0 + 5
                    dt1 = min(dt1c,dt1o)
                    n_connect = cnd[0][0]
                    if dt0 < dt1:
                        n_next = otros[0]
                        n_turn = dt0
                    elif dt1 < dt0:
                        n_next = otros[1]
                        n_turn = dt1
                    else:
                        n_turn = dt0
                        if lhs[otros[0]]["energy"] <= lhs[otros[1]]["energy"]:
                            n_next = otros[0]
                        else:
                            n_next = otros[1]
                else:
                    # no tengo llave, como 0
                    df0 = self.light_dict[otros[0]].get_dist((cx,cy))
                    df1 = self.light_dict[otros[1]].get_dist((cx,cy))
                    df2 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                    d01 = self.light_dict[otros[0]].get_dist(otros[1])
                    d12 = self.light_dict[otros[1]].get_dist(cnd[0][0])
                    d20 = self.light_dict[cnd[0][0]].get_dist(otros[0])
                    dt0p = df0 + tr.get_perimeter() + 6
                    dt01 = df0 + (2*d01) + d20 + 7
                    dt02 = df0 + (2*d20) + d01 + 7
                    d0 = min(dt0p,dt01,dt02)
                    dt1p = df1 + tr.get_perimeter() + 6
                    dt10 = df1 + (2*d01) + d12 + 7
                    dt12 = df1 + (2*d12) + d01 + 7
                    d1 = min(dt1p,dt10,dt12)
                    dt2p = df2 + tr.get_perimeter() + 6
                    dt20 = df2 + (2*d20) + d12 + 7
                    dt21 = df2 + (2*d12) + d20 + 7
                    d2 = min(dt2p,dt20,dt21)
                    n_turn = min(d0,d1,d2)
                    n_connect = []
                    if n_turn != d1 and n_turn != d2:
                        n_next = otros[0]
                    elif n_turn != d0 and n_turn != d2:
                        n_next = otros[1]
                    elif n_turn != d0 and n_turn != d1:
                        n_next = cnd[0][0]
                    elif n_turn != d0:
                        # priorizar el que no tenemos
                        n_next = otros[1]
                    elif n_turn != d1:
                        # priorizar el que no tenemos
                        n_next = otros[0]
                    else:
                        # empate entr otros o los 3 energia priorizando los que no tenemos
                        if lhs[otros[0]]["energy"] <= lhs[otros[1]]["energy"]:
                            n_next = otros[0]
                        else:
                            n_next = otros[1]
            elif len(cnd) == 2:
                # controlo 2
                if [cnd[0][0][0],cnd[0][0][1]] in lhs[cnd[1][0]]["connections"]:
                    # están conectados
                    if cnd[0][1] == 1 and cnd[1][1] == 1:
                        # tenemos las dos llaves
                        to0 = self.light_dict[otros[0]].get_dist(cnd[0][0])
                        to1 = self.light_dict[otros[0]].get_dist(cnd[1][0])
                        n_next = otros[0]
                        n_turn = self.light_dict[otros[0]].get_dist((cx,cy)) + 3
                        # primero la conexión más larga
                        if to0 < to1:
                            n_connect = cnd[1][0]
                        elif to1 < to0:
                            n_connect = cnd[0][0]
                        else: 
                            #  son iguales conectar al de menor energia primero
                            if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                n_connect = cnd[0][0]
                            else:
                                n_connect = cnd[1][0]
                    elif cnd[0][1] == 1:
                        # solo la llave del 0
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d12 = self.light_dict[cnd[1][0]].get_dist(otros[0])
                        dt1 = df1 + d12 + 4
                        dt2 = df2 + d12 + 4
                        if dt1 < dt2:
                            n_turn = dt1
                            n_next = cnd[1][0]
                            n_connect = []
                        else:
                            # en caso de igualdad priorizar el que no tenemos
                            n_next = otros[0]
                            n_connect = cnd[0][0]
                            n_turn = dt2
                    elif cnd[1][1] == 1:
                        # solo la lalve del 1
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d02 = self.light_dict[cnd[0][0]].get_dist(otros[0])
                        dt0 = df0 + d02 + 4
                        dt2 = df2 + d02 + 4
                        if dt0 < dt2:
                            n_turn = dt0
                            n_next = cnd[0][0]
                            n_connect = []
                        else:
                            # en caso de igualda priorizar el que no tenemos
                            n_next = otros[0]
                            n_connect = cnd[1][0]
                            n_turn = dt2
                    else:
                        # no tiene la llave de ninguno
                        n_connect = []
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d01 = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        d12 = self.light_dict[cnd[1][0]].get_dist(otros[0])
                        d20 = self.light_dict[otros[0]].get_dist(cnd[0][0])
                        dt01 = df0 + d01 + d12 + 5
                        dt02 = df0 + d20 + d12 + 5
                        d0 = min(dt01,dt02)
                        dt10 = df1 + d01 + d20 + 5
                        dt12 = df1 + d12 + d20 + 5
                        d1 = min(dt12,dt10)
                        dt2021 = df2 + d20 + d20 + d12 + 6
                        dt2012 = df2 + d20 + d01 + d12 + 6
                        dt2120 = df2 + d12 + d12 + d20 + 6
                        dt2102 = df2 + d12 + d01 + d20 + 6
                        d2 = min(dt2021,dt2012,dt2120,dt2102)
                        n_turn = min(d0,d1,d2)
                        if n_turn != d0 and n_turn != d1:
                            n_next = otros[0]
                        elif n_turn != d0 and n_turn != d2:
                            n_next = cnd[1][0]
                        elif n_turn != d1 and n_turn != d2:
                            n_next = cnd[0][0]
                        elif n_turn != d2:
                            # empate 0 y 1
                            if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                n_next = cnd[0][0]
                            else:
                                n_next = cnd[1][0]
                        else:
                            # empates con 2 o triples. priorizar el que no tenemos
                            n_next = otros[0]
                else:
                    # no están conectados
                    if cnd[0][1] == 1 and cnd[1][0] == 1:
                    #ambas llaves
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d01 = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        d12 = self.light_dict[cnd[1][0]].get_dist(otros[0])
                        d20 = self.light_dict[otros[0]].get_dist(cnd[0][0])
                        dt02 = df0 + d20 + d12 + 6
                        dt01 = df0 + d01 + d12 + 6
                        d0 = min(dt02,dt01)
                        dt10 = df1 + d01 + d20 + 6
                        dt12 = df1 + d12 + d20 + 6
                        d1 = min(dt10,dt12)
                        dt20 = df2 + d20 + d10 + 6
                        dt21 = df2 + d12 + d10 + 6
                        d2 = min(dt20,dt21)
                        n_turn = min(d0,d1,d2)
                        if n_turn != d0 and n_turn != d1:
                            n_next = otros[0]
                            if d12 < d20:
                                n_connect = cnd[0][0]
                            else:
                                n_connect = cnd[1][0]
                        elif n_turn != d0 and n_turn != d2:
                            n_next = cnd[1][0]
                            n_connect = cnd[0][0]
                        elif n_turn != d1 and n_turn != d2:
                            n_next = cnd[0][0]
                            n_connect = cnd[1][0]
                        elif n_turn != d2:
                            # empate entre 1 y 0 a por el de menor energia
                            if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                n_next = cnd[0][0]
                                n_connect = cnd[1][0]
                            else:
                                n_next = cnd[1][0]
                                n_connect = cnd[0][0]
                        else:
                            # empates con 2 o triple priorizar el que no tenemos
                            n_next = otros[0]
                            if d12 < d20:
                                n_connect = cnd[0][0]
                            else:
                                n_connect = cnd[1][0]
                    elif cnd[0][1] == 1:
                        # solo la llave del 0
                        n_connect = cnd[0][0]
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d12 = self.light_dict[otros[0]].get_dist(cnd[1][0])
                        d20 = self.light_dict[cnd[0][0]].get_dist(otros[0])
                        d01 = self.light_dict[cnd[1][0]].get_dist(cnd[0][0])
                        dt10 = df1 + d01 + d20 + 6
                        dt12 = df1 + d12 + d20 + 6
                        d1 = min(dt10,dt12)
                        dt20 = df2 + d20 + d01 + 6
                        dt21 = df2 + d12 + d01 + 6
                        d2 = min(dt20,dt21)
                        if d1 < d2:
                            n_turn = d1
                            n_next = cnd[1][0]
                        else:
                            # en caso de empate se prioriza el libre
                            n_next = otros[0]
                            n_turn = d2
                    elif cnd[1][1] == 1:
                        # solo la llave del 1
                        n_connect = cnd[1][0]
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d12 = self.light_dict[otros[0]].get_dist(cnd[1][0])
                        d20 = self.light_dict[cnd[0][0]].get_dist(otros[0])
                        d01 = self.light_dict[cnd[1][0]].get_dist(cnd[0][0])
                        dt01 = df0 + d01 + d12 + 6
                        dt02 = df0 + d20 + d12 + 6
                        d0 = min (dt01,dt02)
                        dt20 = df2 + d20 + d01 + 6
                        dt21 = df2 + d12 + d01 + 6
                        d2 = min(dt20,dt21)
                        if d0 < d2:
                            n_turn = d0
                            n_next = cnd[0][0]
                        else:
                            # en caso de empate se prioriza el libre
                            n_next = otros[0]
                            n_turn = d2
                    else:
                        # ninguna llave como si 0
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[otros[0]].get_dist((cx,cy))
                        d01 = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        d12 = self.light_dict[cnd[1][0]].get_dist(otros[0])
                        d20 = self.light_dict[otros[0]].get_dist(cnd[0][0])
                        dt0p = df0 + tr.get_perimeter() + 6
                        dt0c1 = df0 + (2*d01) + d20 + 7
                        dt0c2 = df0 + (2*d20) + d01 + 7
                        d0 = min(dt0p,dt0c1,dt0c2)
                        dt1p = df1 + tr.get_perimeter() + 6
                        dt1c0 = df1 + (2*d01) + d12 + 7
                        dt1c2 = df1 + (2*d12) + d01 + 7
                        d1 = min(dt1p,dt1c0,dt1c2)
                        dt2p = df2 + tr.get_perimeter() + 6
                        dt2c0 = df2 + (2*d20) + d12 + 7
                        dt2c1 = df2 + (2*d12) + d20 + 7
                        d2 = min(dt2p,dt2c0,dt2c1)
                        n_turn = min(d0,d1,d2)
                        n_connect = []
                        if n_turn != d0 and n_turn != d1:
                            n_next = otros[0]
                        elif n_turn != d0 and n_turn != d2:
                            n_next = cnd[1][0]
                        elif n_turn != d1 and n_turn != d2:
                            n_next = cnd[0][0]
                        elif n_turn != d2:
                            # empate 0 y 1 a por el de menor energia
                            if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                n_next = cnd[0][0]
                            else:
                                n_next = cnd[1][0]
                        else:
                            # empate triple o con el 2. priorizar el suelto
                            n_next = otros[0]
            else:
                # controlo 3
                cord0 = [cnd[0][0][0],cnd[0][0][1]]
                cord1 = [cnd[1][0][0],cnd[1][0][1]]
                cord2 = [cnd[2][0][0],cnd[2][0][1]]
                # self.log("con0: %s", str(lhs[cnd[0][0]]["connections"]))
                # self.log("con1: %s", str(lhs[cnd[1][0]]["connections"]))
                # self.log("con2: %s", str(lhs[cnd[2][0]]["connections"]))
                if not(cord0 in lhs[cnd[1][0]]["connections"] and cord1 in lhs[cnd[2][0]]["connections"] and cord2 in lhs[cnd[0][0]]["connections"]):
                    # falta alguna conexion
                    if cord0 in lhs[cnd[2][0]]["connections"] and cord1 in lhs[cnd[2][0]]["connections"]:
                        # Falta la 0-1
                        d0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        d1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        dt = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        if cnd[0][1] == 1 and cnd[1][1] == 1:
                            # tenemos la llave de las dos
                            if d0 < d1:
                                n_next = cnd[0][0]
                                n_turn = d0 + 2
                                n_connect = cnd[1][0]
                            elif d1 < d0:
                                n_next = cnd[1][0]
                                n_turn = d1 + 2
                                n_connect = cnd[0][0]
                            else:
                                # iguales atacar al de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_turn = d0 + 2
                                    n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[1][0]
                                    n_turn = d1 + 2
                                    n_connect = cnd[0][0]
                        elif cnd[0][1] == 1:
                            # solo tenemos la llave del 0
                            n_next = cnd[1][0]
                            n_turn = d1 + 2
                            n_connect = cnd[0][0]
                        elif cnd[1][1] == 1:
                            # solo tenemos la llave del 1
                            n_next = cnd[0][0]
                            n_turn = d0 + 2
                            n_connect = cnd[1][0]
                        else:
                            # ninguna llave
                            n_connect = []
                            if d0 < d1:
                                n_next = cnd[0][0]
                                n_turn = d0 + dt + 3
                            elif d1 < d0:
                                n_next = cnd[1][0]
                                n_turn = d1 + dt + 3
                            else:
                                # iguales atacar al de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_turn = d0 + dt + 3
                                else:
                                    n_next = cnd[1][0]
                                    n_turn = d1 + dt + 3
                    elif cord1 in lhs[cnd[0][0]]["connections"] and cord2 in lhs[cnd[0][0]]["connections"]:
                        # Falta la 1-2
                        d1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        d2 = self.light_dict[cnd[2][0]].get_dist((cx,cy))
                        dt = self.light_dict[cnd[1][0]].get_dist(cnd[2][0])
                        if cnd[1][1] ==1 and cnd[2][1] == 1:
                            # tenemos ambas llaves
                            if d1 < d2:
                                n_next = cnd[1][0]
                                n_turn = d1 + 2
                                n_connect = cnd[2][0]
                            elif d2 < d1:
                                n_next = cnd[2][0]
                                n_turn = d2 + 2
                                n_connect = cnd[1][0]
                            else:
                                # iguales atacar al de menor energia
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    n_turn = d1 + 2
                                    n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_turn = d2 + 2
                                    n_connect = cnd[1][0]
                        elif cnd[1][1] == 1:
                            # solo la llave del 1
                            n_next = cnd[2][0]
                            n_turn = d2 + 2
                            n_connect = cnd[1][0]
                        elif cnd[2][1] == 1:
                            # solo la llave del 2
                            n_next = cnd[1][0]
                            n_turn = d1 + 2
                            n_connect = cnd[2][0]
                        else:
                            # ninguna llave
                            n_connect = []
                            if d1 < d2:
                                n_next = cnd[1][0]
                                n_turn = d1 + dt + 3
                            elif d2 < d1:
                                n_next = cnd[2][0]
                                n_turn = d2 + dt + 3
                            else:
                                # iguales atacar al de menor energia
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    n_turn = d1 + dt + 3
                                else:
                                    n_next = cnd[2][0]
                                    n_turn = d2 + dt + 3
                    elif cord0 in lhs[cnd[1][0]]["connections"] and cord2 in lhs[cnd[1][0]]["connections"]:
                        # Falta la 0-2
                        d0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        d2 = self.light_dict[cnd[2][0]].get_dist((cx,cy))
                        dt = self.light_dict[cnd[0][0]].get_dist(cnd[2][0])
                        if cnd[0][1] == 1 and cnd[2][1] == 1:
                            # ambas llaves
                            if d0 < d2:
                                n_next = cnd[0][0]
                                n_turn = d0 + 2
                                n_connect = cnd[2][0]
                            elif d2 < d0:
                                n_next = cnd[2][0]
                                n_turn = d2 + 2
                                n_connect = cnd[0][0]
                            else:
                                # iguales atacar al de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_turn = d0 + 2
                                    n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_turn = d2 + 2
                                    n_connect = cnd[0][0]
                        elif cnd[0][1] == 1:
                            # solo la llave de 0
                            n_next = cnd[2][0]
                            n_turn = d2 + 2
                            n_connect = cnd[0][0]
                        elif cnd[2][1] == 1:
                            # solo la llave dle 2
                            n_next = cnd[0][0]
                            n_turn = d0 + 2
                            n_connect = cnd[2][0]
                        else:
                            # ninguna llave
                            n_connect = []
                            if d0 < d2:
                                n_next = cnd[0][0]
                                n_turn = d0 + dt + 3
                            elif d2 < d0:
                                n_next = cnd[2][0]
                                n_turn = d2 + dt + 3
                            else:
                                # igual atacar al de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_turn = d0 + dt + 3
                                else:
                                    n_next = cnd[2][0]
                                    n_turn = d2 + dt + 3
                    elif cord0 in lhs[cnd[2][0]]["connections"]:
                        # Faltan 0-1 y 1-2
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[cnd[2][0]].get_dist((cx,cy))
                        d10 = self.light_dict[cnd[1][0]].get_dist(cnd[0][0])
                        d12 = self.light_dict[cnd[1][0]].get_dist(cnd[2][0])
                        dfc = self.light_dict[cnd[0][0]].get_dist(cnd[2][0])
                        if cnd[0][1] == 1 and cnd[2][1] == 1:
                            # tenemos las dos llaves
                            n_next = cnd[1][0]
                            n_turn = df1 + 3
                            # conectamos primero el mas largo
                            if d10 < d12:
                                n_connect = cnd[2][0]
                            elif d12 < d10:
                                n_connect = cnd[0][0]
                            else:
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_connect = cnd[0][0]
                                else:
                                    n_connect = cnd[2][0]
                        elif cnd[0][1] == 1:
                            # solo la llave del 0
                            d1 = df1 + d12 + 4
                            d2 = df2 + d12 + 4
                            if d1 <= d2:
                                # priorizamos conexión rápida en empate
                                n_turn = d1
                                n_next = cnd[1][0]
                                n_connect = cnd[0][0]
                            elif d2 < d1:
                                n_turn = d2
                                n_next = cnd[2][0]
                                n_connect = []
                        elif cnd[2][1] == 1:
                            # solo la llave del 2
                            d1 = df1 + d10 + 4
                            d0 = df0 + d10 + 4
                            if d1 <= d0:
                                # priorizamos conexión rápida en empate
                                n_turn = d1
                                n_next = cnd[1][0]
                                n_connect = cnd[2][0]
                            else:
                                n_turn = d0
                                n_next = cnd[0][0]
                                n_connect = []
                        else:
                            # ninguna llave de los dos
                            if cnd[1][1] == 1:
                                # llave del 1 si
                                d021 = df0 + dfc + d12 + 5
                                d012 = df0 + d10 + d12 + 5
                                d201 = df2 + dfc + d10 + 5
                                d210 = df2 + d12 + d10 + 5
                                n_turn = min(d021,d012,d201,d210)
                                n_connect = cnd[1][0]
                                if n_turn != d021 and n_turn != d012:
                                    # uno de conexión al 2
                                    n_next = cnd[2][0]
                                elif n_turn != d201 and n_turn != d210:
                                    # uno de conexión al 0
                                    n_next = cnd[0][0]
                                else:
                                    # hay igualdades. atacar al de menro energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[2][0]
                            else:
                                # no hay llave del 1 como sin llave
                                n_connect = []
                                d21 = df2 + d12 + d10 + 5
                                d20 = df2 + dfc + d10 + 5
                                d2 = min(d21,d20)
                                d01 = df0 + d10 + d12 + 5
                                d02 = df0 + dfc + d12 + 5
                                d0 = min(d01,d02)
                                d1021 = df1 + d10 + dfc + d12 + 6
                                d1012 = df1 + d10 + d10 + d12 + 6
                                d1201 = df1 + d12 + dfc + d10 + 6
                                d1210 = df1 + d12 + d12 + d10 + 6
                                d1 = min(d1021,d1012,d1201,d1210)
                                n_turn = min(d0,d1,d2)
                                if n_turn != d2 and n_turn != d0:
                                    # alguno de siguiente 1
                                    n_next = cnd[1][0]
                                elif n_turn != d2 and n_turn != d1:
                                    # a por el 0
                                    n_next = cnd[0][0]
                                elif n_turn != d0 and n_turn != d1:
                                    # a por el 2
                                    n_next = cnd[2][0]
                                elif n_turn != d1:
                                    # empate entre 2 y 0 a por el de menor energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[2][0]
                                elif n_turn != d0:
                                    # empate entre 2 y 1 a por el de menor energia
                                    if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[1][0]
                                    else:
                                        n_next = cnd[2][0]
                                elif n_turn != d2:
                                    # empate entre 0 y 1 a por el de menor energia
                                    if lhs[cnd[1][0]]["energy"] <= lhs[cnd[0][0]]["energy"]:
                                        n_next = cnd[1][0]
                                    else:
                                        n_next = cnd[0][0]
                                else:
                                    # triple empate a por el de menor energia
                                    if lhs[cnd[1][0]]["energy"] <= lhs[cnd[0][0]]["energy"] and lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[1][0]
                                    elif lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[2][0]
                    elif cord0 in lhs[cnd[1][0]]["connections"]:
                        # Faltan 1-2 y 0-2
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[cnd[2][0]].get_dist((cx,cy))
                        d20 = self.light_dict[cnd[2][0]].get_dist(cnd[0][0])
                        d21 = self.light_dict[cnd[2][0]].get_dist(cnd[1][0])
                        dfc = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        if cnd[0][1] == 1 and cnd[1][1] == 1:
                            # ambas llaves
                            n_next = cnd[2][0]
                            n_turn = df2 + 3
                            # conectar primero la más lejana
                            if d20 < d21:                               
                                n_connect = cnd[1][0]
                            elif d21 < d20:
                                n_connect = cnd[0][0]
                            else:
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_connect = cnd[0][0]
                                else:
                                    n_connect = cnd[1][0]
                        elif cnd[0][1] == 1:
                            # llave del 0
                            d1 = df1 + d21 + 4
                            d2 = df2 + d21 + 4
                            if d1 < d2:
                                n_turn = d1
                                n_connect = []
                                n_next = cnd[1][0]
                            else:
                                # priorizar la primera conexion rapida
                                n_turn = d2
                                n_connect = cnd[0][0]
                                n_next = cnd[2][0]
                        elif cnd[1][1] == 1:
                            # llave del 1
                            d0 = df0 + d20 + 4
                            d2 = df2 + d20 + 4
                            if d0 < d2:
                                n_turn = d0
                                n_connect = []
                                n_next = cnd[0][0]
                            else:
                                # prioriza la primera conexion rapida
                                n_turn = d2
                                n_connect = cnd[1][0]
                                n_next = cnd[2][0]
                        else:
                            # ninguna llave de las dos
                            if cnd[2][1] == 1:
                                # llave del 2 si
                                d012 = df0 + dfc + d21 + 5
                                d021 = df0 + d20 + d21 + 5 
                                d102 = df1 + dfc + d20 + 5
                                d120 = df1 + d21 + d20 + 5
                                n_turn = min(d012,d021,d102,d120)
                                n_connect = cnd[2][0]
                                if n_turn != d012 and n_turn != d021:
                                    # uno de conexion al 1
                                    n_next = cnd[1][0]
                                elif n_turn != d102 and n_turn != d120:
                                    # uno de conexion al 0
                                    n_next = cnd[0][0]
                                else:
                                    # hay igualdades. atacar al de menor energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[1][0]
                            else:
                                # no tengo ninguna llave
                                n_connect = []
                                d02 = df0 + d20 + d21 + 5
                                d01 = df0 + dfc + d21 + 5
                                d0 = min(d02,d01)
                                d12 = df1 + d21 + d20 + 5
                                d10 = df1 + dfc + d20 + 5
                                d1 = min(d12,d10)
                                d2012 = df2 + d20 + dfc + d21 + 6
                                d2021 = df2 + d20 + d20 + d21 + 6
                                d2102 = df2 + d21 + dfc + d20 + 6
                                d2120 = df2 + d21 + d21 + d20 + 6
                                d2 = min(d2012,d2021,d2102,d2120)
                                n_turn = min(d0,d1,d2)
                                if n_turn != d0 and n_turn != d1:
                                    # alguno del siguiente 2
                                    n_next = cnd[2][0]
                                elif n_turn != d0 and n_turn != d2:
                                    # siguiente 1
                                    n_next = cnd[1][0]
                                elif n_turn != d1 and n_turn != d2:
                                    # siguente 0
                                    n_next = cnd[0][0]
                                elif n_turn != d0:
                                    # empate 2 y 1 a por el de menor energia
                                    if lhs[cnd[2][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                        n_next = cnd[2][0]
                                    else:
                                        n_next = cnd[1][0]
                                elif n_turn != d1:
                                    # empate 0 y 2 a por el de menor energia
                                    if lhs[cnd[2][0]]["energy"] <= lhs[cnd[0][0]]["energy"]:
                                        n_next = cnd[2][0]
                                    else:
                                        n_next = cnd[0][0]
                                elif n_turn != d2:
                                    # empate 0 y 1 a por el de menor energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[1][0]
                                else:
                                    # tripe empate a por el de menor energia
                                    if lhs[cnd[2][0]]["energy"] <= lhs[cnd[0][0]]["energy"] and lhs[cnd[2][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                        n_next = cnd[2][0]
                                    elif lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[1][0]
                    elif cord1 in lhs[cnd[2][0]]["connections"]:
                        # Faltan 0-1 y 0-2
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[cnd[2][0]].get_dist((cx,cy))
                        d01 = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        d02 = self.light_dict[cnd[0][0]].get_dist(cnd[2][0])
                        dfc = self.light_dict[cnd[1][0]].get_dist(cnd[2][0])
                        if cnd[1][1] == 1 and cnd[2][1] == 1:
                            # tenemos las dos llaves
                            n_next = cnd[0][0]
                            n_turn = df0 + 3
                            # primero la conexion mas larga
                            if d01 < d02:
                                n_connect = cnd[2][0]
                            elif d02 < d01:
                                n_connect = cnd[1][0]
                            else:
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_connect = cnd[1][0]
                                else:
                                    n_connect = cnd[2][0]
                        elif cnd[1][1] == 1:
                            # solo la llave del 1
                            d0 = df0 + d02 + 4
                            d2 = df2 + d02 + 4
                            if d0 <= d2:
                                # priorizar la conexion rapida
                                n_next = cnd[0][0]
                                n_turn = d0
                                n_connect = cnd[1][0]
                            else:
                                n_next = cnd[2][0]
                                n_turn = d2
                                n_connect = []
                        elif cnd[2][1] == 1:
                            # solo la llave del 2
                            d0 = df0 + d01 + 4
                            d1 = df1 + d01 + 4
                            if d0 <= d1:
                                # priorizar la conexion rapida
                                n_next = cnd[0][0]
                                n_turn = d0
                                n_connect = cnd[2][0]
                            else:
                                n_next = cnd[1][0]
                                n_turn = d1
                                n_connect = []
                        else:
                            # ninguna de las dos llaves
                            if cnd[0][1] == 1:
                                # tenemos llave del 0
                                d102 = df1 + d01 + d02 + 5
                                d120 = df1 + dfc + d02 + 5
                                d201 = df2 + d02 + d01 + 5
                                d210 = df2 + dfc + d01 + 5
                                n_turn = min(d102,d120,d201,d210)
                                n_connect = cnd[0][0]
                                if n_turn != d102 and n_turn != d120:
                                    # alguno de los del 2
                                    n_next = cnd[2][0]
                                elif n_turn != d201 and n_turn != d210:
                                    # alguno de lso del 1
                                    n_next = cnd[1][0]
                                else:
                                    # hay igualdades. atacar al de menor energia
                                    if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[1][0]
                                    else:
                                        n_next = cnd[2][0]
                            else:
                                # no tenemos ninguna lalve
                                n_connect = []
                                d10 = df1 + d01 + d02 + 5
                                d12 = df1 + dfc + d02 + 5
                                d1 = min(d10,d12)
                                d20 = df2 + d02 + d01 + 5
                                d21 = df2 + dfc + d01 + 5
                                d2 = min(d20,d21)
                                d0102 = df0 + d01 + d01 + d02 + 6
                                d0120 = df0 + d01 + dfc + d02 + 6
                                d0201 = df0 + d02 + d02 + d01 + 6
                                d0210 = df0 + d02 + dfc + d01 + 6
                                d0 = min(d0102,d0120,d0201,d0210)
                                n_turn = min(d1,d2,d0)
                                if n_turn != d1 and n_turn != d2:
                                    # alguno del 0
                                    n_next = cnd[0][0]
                                elif n_turn != d1 and n_turn != d0:
                                    # apor el 2
                                    n_next = cnd[2][0]
                                elif n_turn != d2 and n_turn != d0:
                                    # apor el 1
                                    n_next = cnd[1][0]
                                elif n_turn != d0:
                                    # empate 1 y 2 a por el de menor energia
                                    if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[1][0]
                                    else:
                                        n_next = cnd[2][0]
                                elif n_turn != d1:
                                    # empate 0 y 2 a por el de menor energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[2][0]
                                elif n_turn != d2:
                                    # empate 0 y 1 a por el de menor energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    else:
                                        n_next = cnd[1][0]
                                else:
                                    # triple empate a por el de menor energia
                                    if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]] and lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[0][0]
                                    elif lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                        n_next = cnd[1][0]
                                    else:
                                        n_next = cnd[2][0]
                    else:
                        # Faltan todas las conexiones
                        df0 = self.light_dict[cnd[0][0]].get_dist((cx,cy))
                        df1 = self.light_dict[cnd[1][0]].get_dist((cx,cy))
                        df2 = self.light_dict[cnd[2][0]].get_dist((cx,cy))
                        d01 = self.light_dict[cnd[0][0]].get_dist(cnd[1][0])
                        d12 = self.light_dict[cnd[1][0]].get_dist(cnd[2][0])
                        d20 = self.light_dict[cnd[2][0]].get_dist(cnd[0][0])
                        dt012 = df0 + d01 + d12 + 6
                        dt021 = df0 + d20 + d12 + 6
                        d0 = min(dt012,dt021)
                        dt102 = df1 + d01 + d20 + 6
                        dt120 = df1 + d12 + d20 + 6
                        d1 = min(dt102, dt120)
                        dt201 = df2 + d20 + d01 + 6
                        dt210 = df2 + d12 + d01 + 6
                        d2 = min(dt201,dt210)
                        n_turn = min(d0,d1,d2)
                        if cnd[0][1] == 1 and cnd[1][1] == 1 and cnd[2][1] == 1:
                            # todas las llaves
                            if n_turn != d0 and n_turn != d1:
                                n_next = cnd[2][0]
                                if d12 <= d20:
                                    n_connect = cnd[0][0]
                                else:
                                    n_connect = cnd[1][0]
                            elif n_turn != d0 and n_turn != d2:
                                n_next = cnd[1][0]
                                if d01 <= d12:
                                    n_connect = cnd[2][0]
                                else:
                                    n_connect = cnd[0][0]
                            elif n_turn != d1 and n_turn != d2:
                                n_next = cnd[0][0]
                                if d01 <= d20:
                                    n_connect = cnd[2][0]
                                else:
                                    n_connect = cnd[1][0]
                            elif n_turn != d0:
                                # empate 1 y 2 a por el menor energia
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    if d01 <= d12:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[0][0]
                                else:
                                    n_next = cnd[2][0]
                                    if d12 <= d20:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[1][0]
                            elif n_turn != d1:
                                # empate 0 y 2 a por el de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    if d01 <= d20:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[2][0]
                                    if d12 <= d20:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[1][0]
                            elif n_turn != d2:
                                # empate 0 y 1 a por el de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    if d01 <= d20:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[1][0]
                                    if d01 <= d12:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[0][0]
                            else:
                                # tripe emapte a por el de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"] and lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    if d01 <= d20:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[1][0]
                                elif lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    if d01 <= d12:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[0][0]
                                else:
                                    n_next = cnd[2][0]
                                    if d12 <= d20:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[1][0]
                        elif cnd[0][1] == 1 and cnd[1][1] == 1:
                            # llaves 0 y 1
                            if n_turn != d0 and n_turn != d1:
                                n_next = cnd[2][0]
                                if d12 < d20:
                                    n_connect = cnd[0][0]
                                else:
                                    n_connect = cnd[1][0]
                            elif n_turn != d0 and n_turn != d2:
                                n_next = cnd[1][0]
                                n_connect = cnd[0][0]
                            elif n_turn != d1 and n_turn != d2:
                                n_next = cnd[0][0]
                                n_connect = cnd[1][0]
                            elif n_turn != d0:
                                # empate 1 y 2
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    n_connect = cnd[0][0]
                                else:
                                    n_next = cnd[2][0]
                                    if d12 < d20:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[1][0]
                            elif n_turn != d1:
                                # empate 0 y 2
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[2][0]
                                    if d12 < d20:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[1][0]
                            elif n_turn != d2:
                                # empate 0 y 1
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[1][0]
                                    n_connect = cnd[0][0]
                            else:
                                # triple emapte a por el de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"] and lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_connect = cnd[1][0]
                                elif lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    n_connect = cnd[0][0]
                                else:
                                    n_next = cnd[2][0]
                                    if d12 < d20:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[1][0]
                        elif cnd[0][1] == 1 and cnd[2][1] == 1:
                            # llaves 0 y 2
                            if n_turn != d2 and n_turn != d1:
                                n_next = cnd[0][0]
                                n_connect = cnd[2][0]
                            elif n_turn != d2 and n_turn != d0:
                                n_next = cnd[1][0]
                                if d12 < d01:
                                    n_connect = cnd[0][0]
                                else:
                                    n_connect = cnd[2][0]
                            elif n_turn != d0 and n_turn != d1:
                                n_next = cnd[2][0]
                                n_connect = cnd[0][0]
                            elif n_turn != d0:
                                # empate 1 y 2
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    if d12 < d01:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_connect = cnd[0][0]
                            elif n_turn != d1:
                                # empate 0 y 2
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_connect = cnd[0][0]
                            elif n_turn != d2:
                                # empate 1 y 0
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[0][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    if d12 < d01:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[0][0]
                                    n_connect = cnd[2][0]
                            else:
                                # triple empate
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[0][0]]["energy"] and lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    if d12 < d01:
                                        n_connect = cnd[0][0]
                                    else:
                                        n_connect = cnd[2][0]
                                elif lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_connect = cnd[0][0]
                        elif cnd[1][1] == 1 and cnd[2][1] == 1:
                            # llaves 1 y 2
                            if n_turn != d1 and n_turn != d2:
                                n_next = cnd[0][0]
                                if d01 < d20:
                                    n_connect = cnd[2][0]
                                else:
                                    n_connect = cnd[1][0]
                            elif n_turn != d0 and n_turn != d2:
                                n_next = cnd[1][0]
                                n_connect = cnd[2][0]
                            elif n_turn != d0 and n_turn != d1:
                                n_next = cnd[2][0]
                                n_connect = cnd[1][0]
                            elif n_turn != d0:
                                # emapte 1 y 2
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_connect = cnd[1][0]
                            elif n_turn != d1:
                                # empate 0 y 2
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    if d01 < d20:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_connect =cnd[1][0]
                            elif n_turn != d2:
                                # empate 0 y 1
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    if d01 < d20:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[1][0]
                                else:
                                    n_next = cnd[1][0]
                                    n_connect = cnd[2][0]
                            else:
                                # triple empate
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"] and lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                    if d01 < d20:
                                        n_connect = cnd[2][0]
                                    else:
                                        n_connect = cnd[1][0]
                                elif lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                    n_connect = cnd[2][0]
                                else:
                                    n_next = cnd[2][0]
                                    n_connect = cnd[1][0]
                        elif cnd[0][1] == 1:
                            # solo llave 0
                            n_connect = cnd[0][0]
                            if d1 < d2:
                                n_turn = d1
                                n_next = cnd[1][0]
                            elif d2 < d1:
                                n_turn = d2
                                n_next = cnd[2][0]
                            else:
                                # empate
                                n_turn = d1
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                else:
                                    n_next = cnd[2][0]
                        elif cnd[1][1] == 1:
                            # solo llave 1
                            n_connect = cnd[1][0]
                            if d0 < d2:
                                n_turn = d0
                                n_next = cnd[0][0]
                            elif d2 < d0:
                                n_turn = d2
                                n_next = cnd[2][0]
                            else:
                                # empate
                                n_turn = d0
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                else:
                                    n_next = cnd[2][0]
                        elif cnd[2][1] == 1:
                            # solo llave 2
                            n_connect = cnd[2][0]
                            if d0 < d1:
                                n_turn = d0
                                n_next = cnd[0][0]
                            elif d1 < d0:
                                n_turn = d1
                                n_next = cnd[1][0]
                            else:
                                # empate
                                n_turn = d0
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                else:
                                    n_next = cnd[1][0]
                        else:
                            # ninguna llave
                            dt01 = df0 + (2*d01) + d20 + 7
                            dt02 = df0 + (2*d20) + d01 + 7
                            dt0p = df0 + tr.get_perimeter() + 6
                            d0 = min(dt01,dt02,dt0p)
                            dt10 = df1 + (2*d01) + d12 + 7
                            dt12 = df1 + (2*d12) + d01 + 7
                            dt1p = df1 + tr.get_perimeter() + 6
                            d1 = min(dt10,dt12,dt1p)
                            dt20 = df2 + (2*d20) + d12 + 7
                            dt21 = df2 + (2*d12) + d20 + 7
                            dt2p = df2 + tr.get_perimeter() + 6
                            d2 = min(dt20,dt21,dt2p)
                            n_turn = min(d0,d1,d2)
                            n_connect = []
                            if n_turn != d1 and n_turn != d2:
                                n_next = cnd[0][0]
                            elif n_turn != d0 and n_turn != d2:
                                n_next = cnd[1][0]
                            elif n_turn != d1 and n_turn != d0:
                                n_next = cnd[2][0]
                            elif n_turn != d0:
                                # empate 1 y 2 a por el de menor energia
                                if lhs[cnd[1][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[1][0]
                                else:
                                    n_next = cnd[2][0]
                            elif n_turn != d1:
                                # empate 0 y 2 a por el de menor energia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[2][0]]["energy"]:
                                    n_next = cnd[0][0]
                                else:
                                    n_next = cnd[2][0]
                            elif n_turn != d2:
                                # empate 0 y 1 a por el de menor enrgia
                                if lhs[cnd[0][0]]["energy"] <= lhs[cnd[1][0]]["energy"]:
                                    n_next = cnd[0][0]
                                else:
                                    n_next = cnd[1][0]
                else:
                    # ya está el triangulo entero
                    n_turn = self.maxdist
            # llega con n_turn n_next n_connect
            if n_turn != self.maxdist:
                if not(self.check_tri_cross(lhs,tr)):
                    #no hay cruces
                    if to == -1:
                        t_tri = tr
                        t_turn = n_turn
                        to = 0
                        # calcular energia
                        nxt_dist = self.light_dict[n_next].get_dist((cx,cy))
                        light_ener = lhs[n_next]["energy"]
                        if nxt_dist*self.E_LOSS >= light_ener:
                            ener = tr.get_energy()
                        else:
                            if lhs[n_next]["owner"] == self.player_num:
                                # ya es nuetro
                                ener = tr.get_energy() - light_ener + (nxt_dist*self.E_LOSS)
                            else:
                                ener = tr.get_energy() + light_ener - (nxt_dist*self.E_LOSS)
                        t_obj = utils.objetive(n_next,n_connect,ener)
                    else:
                        if self.check_tri(t_turn,n_turn,t_tri,tr):
                            t_tri = tr
                            t_turn = n_turn
                            # calcular energia
                            nxt_dist = self.light_dict[n_next].get_dist((cx,cy))
                            light_ener = lhs[n_next]["energy"]
                            if nxt_dist*self.E_LOSS >= light_ener:
                                ener = tr.get_energy()
                            else:
                                if lhs[n_next]["owner"] == self.player_num:
                                    # ya es nuestro
                                    ener = tr.get_energy() - light_ener + (nxt_dist*self.E_LOSS)
                                else:
                                    ener = tr.get_energy() + light_ener - (nxt_dist*self.E_LOSS)
                            t_obj = utils.objetive(n_next,n_connect,ener)
        self.log("Tri: %s",str(t_tri.get_lighthouses()))
        return t_obj



    def check_tri(self,o_turn,n_turn,o_tri,n_tri):
        n_points = n_tri.get_points()
        o_points = o_tri.get_points()
        n_prob = 1.0-self.tri_prob(n_tri)
        nt_prob = math.pow(n_prob,n_turn)
        if nt_prob < self.E_PROB:
            return False
        if n_points > o_points:
            # el nuevo más puntos
            if n_turn <= o_turn:
                # el nuevo menos o los mismos turnos
                return True
            else:
                # el viejo menos turnos
                dt = n_turn - o_turn
                dp = dt*o_points
                if dp >= n_points:
                    return False
                else:
                    return True
        elif o_points > n_points:
            # el viejo más puntos
            if o_turn <= n_turn:
                # el viejo menos o los mismo turnos
                return False
            else:
                # el nuevo menos turnos
                dt = o_turn - n_turn
                dp = dt*n_points
                if dp >= o_points:
                    return True
                else:
                    return False
        else:
            # los mismos puntos
            if o_turn > n_turn:
                # el nuevo menos turnos
                return True
            elif n_turn > o_turn:
                # el viejo menos turnos
                return False
            else:
                # los dos los mismo turnos
                if n_tri.get_energy() > o_tri.get_energy():
                    # el viejo menos energia
                    return False
                elif o_tri.get_energy() > n_tri.get_energy():
                    # el nuevo menos energia
                    return True
                else:
                    # los dos la misma (probabilidad)
                    o_prob = self.tri_prob(o_tri)
                    n_prob = self.tri_prob(n_tri)
                    if o_prob <= n_prob:
                        # viejo menor o igual probabilidad de estar ocupado
                        return False
                    else:
                        # el nuevo menor probabilidad de estar ocupado
                        return True



    def tri_prob(self,tri):
        lh = tri.get_lighthouses()
        ocupied = max(self.light_dict[lh[0]].get_ocupied(),self.light_dict[lh[1]].get_ocupied(),self.light_dict[lh[2]].get_ocupied())
        return (ocupied*1.0)/(self.turn*1.0)

    def check_tri_cross(self,light,tri):
        """comprobar que no haya cruces con el triangulo"""
        t_lh = tri.get_lighthouses()
        if  (self.check_croses(light,t_lh[0],t_lh[1]) or self.check_croses(light,t_lh[1],t_lh[2]) or self.check_croses(light,t_lh[2],t_lh[0])):
            return True
        else:
            return False
        
    def check_croses(self,light,f1,f2):
        """comprobar si conectar 2 faros haria cruces"""
        for pos,l in light.iteritems():
            for c in l["connections"]:
                # if self.crosing([f1,f2],[pos,(c[0],c[1])]):
                if geom.intersect((c,pos), (f1,f2)):
                    return True
        return False

    def crosing(self,l1,l2):
        """comprobar el cruce entre 2 línea"""
        if(l1[0] == l2[0] or l1[0] == l2[1] or l1[1] == l2[0] or l1[1] == l2[1]):
            # no es cruce es solape (punto en común)
            return False
        if max(l1[0][0],l1[1][0]) < min(l2[0][0],l2[1][0]):
            # distinta proyeción x
            return False

        A1 = self.gradient(l1)
        A2 = self.gradient(l2)
        if (A1 == A2):
            # son paralelas
            return False
        if l1[0][0] == l1[1][0]:
            # linea 1 vertical
            Xa = l1[0][0]
            b2 = l2[0][1] - l2[0][0]*A2
            y2 = Xa*A2+b2
            if(y2 > max(l1[0][1],l1[1][1]) or y2 < min(l1[0][1],l1[1][1])):
                return False
            else:
                return True

        elif l2[0][0] == l2[1][0]:
            # linea 2 vertical
            Xa = l2[0][0]
            b1 = l1[0][1] - l1[0][0]*A1
            y1 = Xa*A1+b1
            if(y1 > max(l2[0][1],l2[1][1]) or y1 < min(l2[0][1],l2[1][1])):
                return False
            else:
                return True

        else:
            b1 = l1[0][1] - l1[0][0]*A1
            b2 = l2[0][1] - l2[0][0]*A2
            Xa = (b2 - b1)/(A1-A2)
            if ((Xa < max(min(l1[0][0],l1[1][0]),min(l2[0][0],l2[1][0]))) or \
                    (Xa > min(max(l1[0][0],l1[1][0]),max(l2[0][0],l2[1][0])))):
                return False
            else:
                return True

    def gradient(self,l):
        """ Devuelve el gradiente m de una linea"""
        m = None
        # asegurar que la línea no es vertical
        if l[0][0] != l[1][0]:
            m = (1./(l[0][0]-l[1][0]))*(l[0][1] - l[1][1])
        return m




if __name__ == "__main__":
    iface = interface.Interface(RandBot)
    iface.run()
