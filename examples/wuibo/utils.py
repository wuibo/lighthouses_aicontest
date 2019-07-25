#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

class lighthouse(object):
    
    def __init__(self,pos,maxy,maxx,l_map):
        """Inicializar faro"""
        (self.posx,self.posy) = pos
        self.ocupied = 0
        self.maxy = maxy
        self.maxx = maxx
        self.map = l_map
        self.triangles = []

    def get_dist(self,pos):
        return self.map[pos[1]][pos[0]]

    def sum_ocupied(self):
        self.ocupied += 1

    def get_ocupied(self):
        return self.ocupied

    def add_triangle(self,tri):
        self.triangles = self.triangles + [tri]

    def get_triangles(self):
        return traingles

class triangle(object):
    
    def __init__(self,lighthouses,points,perimeter,energy):
        self.lighthouses = lighthouses
        self.points = points
        self.perimeter = perimeter
        self.energy = energy

    def get_lighthouses(self):
        return self.lighthouses

    def get_points(self):
        return self.points

    def get_perimeter(self):
        return self.perimeter

    def get_energy(self):
        return self.energy

class objetive(object):

    def __init__(self,nxt,conn,energy):
        self.nxt = nxt
        self.connect = conn
        self.energy = energy

    def get_next(self):
        return self.nxt

    def get_connect(self):
        return self.connect

    def get_energy(self):
        return self.energy

class move(object):

    def __init__(self,mx,my):
        self.my = my
        self.mx = mx
        self.ener1 = 0
        self.ener2 = 0
        self.dist = 0

    def get_move(self):
        return [self.mx,self.my]

    def set_ener(self,basic,second):
        self.ener1 = basic
        self.ener2 = second

    def get_basic_ener(self):
        return self.ener1

    def get_second_ener(self):
        return self.ener2

    def set_dist(self,dist):
        self.dist = dist

    def get_dist(self):
        return dist
