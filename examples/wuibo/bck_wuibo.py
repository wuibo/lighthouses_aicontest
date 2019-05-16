#!/usr/bin/python
# -*- coding: utf-8 -*-

import random, sys
import interface

class Wuibo(interface.Bot):
    """Bot de juego"""
    NAME = "Back"

    def __init__(self,init_state):
        """Inicializar el bot"""
	self.player_num = init_state["player_num"]
	self.player_count = init_state["player_count"]
	self.init_pos = init_state["position"]
	self.map = init_state["map"]
	self.maxy = len(self.map)
	self.maxx = len(self.map[0])
	self.t_faro = 0
	"""
	self.log("MAPA:")
	for tx in reversed(range(self.maxx)):
		self.log("%s",' '.join(str(e) for e in self.map[tx]))
	self.log("REVERSED")
	for ty in reversed(range(self.maxy)):
		arry = []
		for tx in range(self.maxx):
			arry.append(self.map[tx][ty])
		self.log("%s",''.join(str(e) for e in arry))
	"""
	self.maxdist = self.maxx * self.maxy
	self.lighthouses = map(tuple, init_state["lighthouses"])
	self.light_count = len(self.lighthouses)
	self.idlight = []
	#self.log("x: %s",' '.join(str(e) for e in array))
	#identificador del faro y sus coordenadas (x,y)
	for x in range(self.light_count):
		new = []
		for y in range(2):
			new.append(0)
		self.idlight.append(new)
	for lh in range(self.light_count):
		self.idlight[lh][0] = lh
		self.idlight[lh][1] = self.lighthouses[lh]

	#cargar distancia a faros
	self.light_dist = []
	for i in xrange(self.light_count):
		a_y = []
		for y in xrange(self.maxy):
			a_x = []
			for x in xrange(self.maxx):
				a_x.append(self.maxdist)
			a_y.append(a_x)
		self.light_dist.append(a_y)
		self.flood_dist(i)
		"""
		self.log("id: %s cord: %s",i,self.get_cord(i))
		for ty in reversed(range(self.maxy)):
			array = []
			for tx in range(self.maxx):
				array.append(self.light_dist[i][ty][tx])			
			self.log("%s",' '.join(str(e).zfill(3) for e in array))
		"""


    def get_id(self,x,y):
	"""Devuelve el id del light house desde las coordenadas"""
	for lh in range(self.light_count):
		if(self.idlight[lh][1] == (x,y)):
			return self.idlight[lh][0]

    def get_cord(self,i):
	"""Devuelve las coordenadas desde el id"""
	for lh in range(self.light_count):
		if(self.idlight[lh][0] == i):
			return self.idlight[lh][1]

    
	
    def area_triang(self,a,b,c):
	return (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1])

    def side_p_to_seg(self,v1,v2,p):
	area = self.area_triang(v1,v2,p)
	if area > 0:
		lado = "izq"
	elif area < 0:
		lado = "der"
	else:
		lado = "col"
	return lado

    def c_inter(self,u1,u2,v1,v2):
	self.log("INTER c1: %s %s c2: %s %s",u1,u2,v1,v2)
	if (self.side_p_to_seg(u1,u2,v1) == "col" or
	    self.side_p_to_seg(u1,u2,v2) == "col" or
	    self.side_p_to_seg(v1,v2,u1) == "col" or
	    self.side_p_to_seg(v1,v2,u2) == "col"):
		self.log("False1")
		return False
	elif (((self.side_p_to_seg(u1,u2,v1) == "izq" and
		self.side_p_to_seg(u1,u2,v2) == "der") or
		(self.side_p_to_seg(u1,u2,v1) == "der" and
		self.side_p_to_seg(u1,u2,v2) == "izq")) and
		((self.side_p_to_seg(v1,v2,u1) == "der" and
		self.side_p_to_seg(v1,v2,u2) == "izq") or
		(self.side_p_to_seg(v1,v2,u1) == "izq" and
		self.side_p_to_seg(v1,v2,u2) == "der"))):
			self.log("True")
			return True
	else:
		self.log("False2")
		return False
		
    def inter(self,c1,c2,lighthouses):
	count = len(lighthouses)
	for i in range(count):
		cord = self.get_cord(i)
		for con in lighthouses[cord]["connections"]:
			if self.c_inter(c1,c2,cord,con):
				return True
	return False	

    def flood_dist(self,ilight):
	"""Flood dist"""
	(ix,iy) = self.get_cord(ilight)
	self.light_dist[ilight][iy][ix] = 0
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
			"""dire 0"""
			act = [cell[0]-1,cell[1]-1]
			if cell[0]>0 and cell[1]>0:
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 1"""
			act = [cell[0]-1,cell[1]]
			if cell[0]>0:
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 2"""
			act = [cell[0]-1,cell[1]+1]
			if cell[0] > 0 and cell[1] < (self.maxy-1):
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 3"""
			act = [cell[0],cell[1]+1]
			if cell[1] < (self.maxy-1):
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 4"""
			act = [cell[0]+1,cell[1]+1]
			if cell[0] < (self.maxx-1) and cell[1] < (self.maxy-1):
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 5"""
			act = [cell[0]+1,cell[1]]
			if cell[0] < (self.maxx-1):
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 6"""
			act = [cell[0]+1,cell[1]-1]
			if cell[0] < (self.maxx-1) and cell[1] > 0:
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
			"""dire 7"""
			act = [cell[0],cell[1]-1]
			if cell[1] > 0:
				if self.map[act[1]][act[0]] == 1 and act not in checked:
					arr_nxt = arr_nxt + [act]
					self.light_dist[ilight][act[1]][act[0]] = loop
					checked = checked + [act]
		arr_act = arr_nxt
		loop += 1

    def play(self, state):
        """Jugar: llamado cada turno.
        Debe devolver una acción (jugada)."""
	#posición actual
        cx, cy = state["position"]
	#cargar la situación de los faros
        lighthouses = dict((tuple(lh["position"]), lh)
                            for lh in state["lighthouses"])

	#Identificar el faro del que tenemos la clave
	key_i = -1
	key_x = -1
	key_y = -1
	for i in range(self.light_count):
		(lx,ly) = self.get_cord(i)
		if(lighthouses[(lx,ly)]["have_key"] and lighthouses[(lx,ly)]["owner"] == self.player_num):
			self.log("Have key (%s,%s)",lx,ly)
			key_i = i
			key_x = lx
			key_y = ly
	self.log("energi: %s position: %s",state["energy"],state["position"])
	self.log("KEY: %s (%s,%s)",key_i,key_x,key_y)
	#tamaño de la view
	view = state["view"]
	view_y = len(view)
	view_x = len(view[0])

	view_cx = view_x/2
	view_cy = view_y/2	

	#buscar el faro al que vamos
	min_dist = self.maxdist
	by_dist = False
	light_id = 0
	#buscar el más cercano COMPROBAR QUE NO ES TUYO
	for i in range(self.light_count):
		(lx,ly) = self.get_cord(i)
		#distancia más corta...
		if(self.light_dist[i][cy][cx] < min_dist):
			#no en el que estamos
			if(lx!=cx or ly!=cy):
				#Si ya es mio no voy a por el
				if(lighthouses[(lx,ly)]["owner"]!=self.player_num):
					#comprobar si tengo energia
					if(state["energy"] > lighthouses[(lx,ly)]["energy"]):
						#comprobar si están unidos el destino y el que tienes
						if(key_i==-1):
							min_dist = self.light_dist[i][cy][cx]
							light_id = i
							by_dist = True
						else:
							if([lx,ly] not in lighthouses[(key_x,key_y)]["connections"]): 
								min_dist = self.light_dist[i][cy][cx]
								light_id = i
								by_dist = True
	#LOG
	dest_cord = self.get_cord(light_id)
	act_dist = self.light_dist[light_id][cy][cx]
	self.log("DIST DEST: id: %s cord: %s dist: %s owner: %s energy: %s",light_id,dest_cord,act_dist,lighthouses[dest_cord]["owner"],lighthouses[dest_cord]["energy"])

	triangle = False
	triangle1 = (-1,-1)
	traingle2 = (-1,-1)
	if(key_i!=-1):
		#comprobar si desde el que sales se puede hacer triangulo
		###Si el anterior tiene varias uniones al más cercano
		for con in lighthouses[(key_x,key_y)]["connections"]:
			if len(lighthouses[(con[0],con[1])]["connections"])>1:
				#Se puede hacer triángulo (distancia minima no yo)
				c_min_dist = self.maxdist
				for dest in lighthouses[(con[0],con[1])]["connections"]:
					if (dest[0]!= key_x or dest[1] != key_y):
						#no del que vengo
						tl_id = self.get_id(dest[0],dest[1])
						if(self.light_dist[tl_id][cy][cx] < c_min_dist):
							#menor distancia y no conectado
							if([dest[0],dest[1]] not in lighthouses[(key_x,key_y)]["connections"]):
								light_id = tl_id
								min_dist = self.light_dist[tl_id][cy][cx]
								c_min_dist = min_dist
								triangle1 = (con[0],con[1])
								triangle2 = (dest[0],dest[1])
								triangle = True
	#LOG
	dest_cord = self.get_cord(light_id)
	act_dist = self.light_dist[light_id][cy][cx]
	if(triangle):
		self.log("TRIANGLE T: id: %s cord: %s dist: %s owner: %s energy: %s",light_id,dest_cord,act_dist,lighthouses[dest_cord]["owner"],lighthouses[dest_cord]["energy"])
	else:
		self.log("TRIANGLE F")

        # Si estamos en un faro...
        if (cx, cy) in self.lighthouses:
	    self.t_faro += 1
            # Si eres el dueño se puede hacer conexión
            #if lighthouses[(cx, cy)]["owner"] == self.player_num:
	    if self.t_faro == 2:
                    possible_connections = []
                    for dest in self.lighthouses:
                        # No conectar con sigo mismo
                        # No conectar si no tenemos la clave
                        # No conectar si ya existe la conexión
                        # No conectar si no controlamos el destino
                        # Nota: no comprobamos si la conexión se cruza.
                        if (dest != (cx, cy) and
                            lighthouses[dest]["have_key"] and
                            [cx, cy] not in lighthouses[dest]["connections"] and
                            lighthouses[dest]["owner"] == self.player_num):
                            possible_connections.append(dest)

                    if possible_connections:
			self.log("Posible conections")
			#comprobar corte
			if not(self.inter((key_x,key_y),(cx,cy),lighthouses)):
			#if self.t_faro == 2 or self.t_faro == 1:
				self.log("CONNECT: %s",''.join(str(e) for e in possible_connections))
                       		return self.connect(random.choice(possible_connections))

            elif self.t_faro == 1:
		if(state["energy"] > 5):
			self.log("ATTACK: %s",state["energy"])
                	energy = state["energy"]
                	return self.attack(energy)
	self.t_faro = 0

	dist = []
	ener = []
	for mv in range(8):
		if(mv==0):
			arr = [self.maxdist,(-1,-1)]
			ena = [0,(-1,-1)]
		elif(mv==1):
			arr = [self.maxdist,(-1,0)]
			ena = [0,(-1,0)]
		elif(mv==2):
			arr = [self.maxdist,(-1,+1)]
			ena = [0,(-1,+1)]
		elif(mv==3):
			arr = [self.maxdist,(0,+1)]
			ena = [0,(0,+1)]
		elif(mv==4):
			arr = [self.maxdist,(+1,+1)]
			ena = [0,(+1,+1)]
		elif(mv==5):
			arr = [self.maxdist,(+1,0)]
			ena = [0,(+1,0)]
		elif(mv==6):
			arr = [self.maxdist,(+1,-1)]
			ena = [0,(+1,-1)]
		elif(mv==7):
			arr = [self.maxdist,(0,-1)]
			ena = [0,(0,-1)]
		dist.append(arr)
		ener.append(ena)

	if(cx==0 and cy==0):
		"""left-down"""
		dist[0][0] = self.maxdist		
		dist[1][0] = self.maxdist
		dist[2][0] = self.maxdist
		dist[3][0] = self.light_dist[light_id][cy+1][cx]
		dist[4][0] = self.light_dist[light_id][cy+1][cx+1]
		dist[5][0] = self.light_dist[light_id][cy][cx+1]
		dist[6][0] = self.maxdist
		dist[7][0] = self.maxdist
	elif(cy==0 and cx>0 and cx<(self.maxx-1)):
		"""down"""
		dist[0][0] = self.maxdist
		dist[1][0] = self.light_dist[light_id][cy][cx-1]
		dist[2][0] = self.light_dist[light_id][cy+1][cx-1]
		dist[3][0] = self.light_dist[light_id][cy+1][cx]
		dist[4][0] = self.light_dist[light_id][cy+1][cx+1]
		dist[5][0] = self.light_dist[light_id][cy][cx+1]
		dist[6][0] = self.maxdist
		dist[7][0] = self.maxdist
	elif(cy==0 and cx==(self.maxx-1)):
		"""right-down"""
		dist[0][0] = self.maxdist
		dist[1][0] = self.light_dist[light_id][cy][cx-1]
		dist[2][0] = self.light_dist[light_id][cy+1][cx-1]
		dist[3][0] = self.light_dist[light_id][cy+1][cx]
		dist[4][0] = self.maxdist
		dist[5][0] = self.maxdist
		dist[6][0] = self.maxdist
		dist[7][0] = self.maxdist
	elif(cx==(self.maxx-1) and cy>0 and cy<(self.maxy-1)):	
		"""right"""
		dist[0][0] = self.light_dist[light_id][cy-1][cx-1]
		dist[1][0] = self.light_dist[light_id][cy][cx-1]
		dist[2][0] = self.light_dist[light_id][cy+1][cx-1]
		dist[3][0] = self.light_dist[light_id][cy+1][cx]
		dist[4][0] = self.maxdist
		dist[5][0] = self.maxdist
		dist[6][0] = self.maxdist
		dist[7][0] = self.light_dist[light_id][cy-1][cx]
	elif(cx==(self.maxx-1) and cy==(self.maxy-1)):
		"""right-up"""
		dist[0][0] = self.light_dist[light_id][cy-1][cx-1]
		dist[1][0] = self.light_dist[light_id][cy][cx-1]
		dist[2][0] = self.maxdist
		dist[3][0] = self.maxdist
		dist[4][0] = self.maxdist
		dist[5][0] = self.maxdist
		dist[6][0] = self.maxdist
		dist[7][0] = self.light_dist[light_id][cy-1][cx]
	elif(cy==(self.maxy-1) and cx>0 and cx<(self.maxx-1)):
		"""up"""
		dist[0][0] = self.light_dist[light_id][cy-1][cx-1]
		dist[1][0] = self.light_dist[light_id][cy][cx-1]
		dist[2][0] = self.maxdist
		dist[3][0] = self.maxdist
		dist[4][0] = self.maxdist
		dist[5][0] = self.light_dist[light_id][cy][cx+1]
		dist[6][0] = self.light_dist[light_id][cy-1][cx+1]
		dist[7][0] = self.light_dist[light_id][cy-1][cx]
	elif(cy==(self.maxy-1) and cx==0):
		"""left-up"""
		dist[0][0] = self.maxdist
		dist[1][0] = self.maxdist
		dist[2][0] = self.maxdist
		dist[3][0] = self.maxdist
		dist[4][0] = self.maxdist
		dist[5][0] = self.light_dist[light_id][cy][cx+1]
		dist[6][0] = self.light_dist[light_id][cy-1][cx+1]
		dist[7][0] = self.light_dist[light_id][cy-1][cx]
	elif(cx==0 and cy>0 and cy<(self.maxy-1)):
		"""left"""
		dist[0][0] = self.maxdist
		dist[1][0] = self.maxdist
		dist[2][0] = self.maxdist
		dist[3][0] = self.light_dist[light_id][cy+1][cx]
		dist[4][0] = self.light_dist[light_id][cy+1][cx+1]
		dist[5][0] = self.light_dist[light_id][cy][cx+1]
		dist[6][0] = self.light_dist[light_id][cy-1][cx+1]
		dist[7][0] = self.light_dist[light_id][cy-1][cx]
	else:
		dist[0][0] = self.light_dist[light_id][cy-1][cx-1]
		dist[1][0] = self.light_dist[light_id][cy][cx-1]
		dist[2][0] = self.light_dist[light_id][cy+1][cx-1]
		dist[3][0] = self.light_dist[light_id][cy+1][cx]
		dist[4][0] = self.light_dist[light_id][cy+1][cx+1]
		dist[5][0] = self.light_dist[light_id][cy][cx+1]
		dist[6][0] = self.light_dist[light_id][cy-1][cx+1]
		dist[7][0] = self.light_dist[light_id][cy-1][cx]


	#Cargar energía
	ener[0][0] = view[view_cy-1][view_cx-1]
	ener[1][0] = view[view_cy][view_cx-1]
	ener[2][0] = view[view_cy+1][view_cx-1]
	ener[3][0] = view[view_cy+1][view_cx]
	ener[4][0] = view[view_cy+1][view_cx+1]
	ener[5][0] = view[view_cy][view_cx+1]
	ener[6][0] = view[view_cy-1][view_cx+1]
	ener[7][0] = view[view_cy-1][view_cx]
	
	#no está por distancia, coger energía
	if(by_dist==False):
		##buscar máximo de energía
		c_ener = 0
		m_ener = (0,0)
		for i in range(8):
			if(ener[i][0]>c_ener):
				#comprobar mapa
				if(self.map[cy+ener[i][1][1]][cx+ener[i][1][0]]==1):
					c_ener = ener[i][0]
					m_ener = ener[i][1]
		self.log("Energi(no dist) move: %s",m_ener)
		return self.move(m_ener[0],m_ener[1])
	


	##mirar la energia del destino para ver si ir o cargar energía
	own_count = 0
	for lh in range(self.light_count):
		second_cord = self.get_cord(lh)
		if(lighthouses[second_cord]["owner"] == self.player_num):
			own_count += 1
	if own_count == 0:
		##mirar que va a durar hasta el siguiente
		#1-cual al es el siguiente (más corto desde el faro)
		e_min_dist = self.maxdist
		for i in range(self.light_count):
			#no es el destino (primer salto)
			second_cord = self.get_cord(i)
			if(second_cord != dest_cord):
				if(self.light_dist[i][dest_cord[1]][dest_cord[0]]<e_min_dist):
					e_min_dist = self.light_dist[i][dest_cord[1]][dest_cord[0]]
		#2-ver si la energía que tengo es suficiente
		if(lighthouses[dest_cord]["energy"]==0):
			need_ener = e_min_dist*10
		else:
			need_ener=e_min_dist*10+lighthouses[dest_cord]["energy"]-act_dist*10
		if(state["energy"]<need_ener):
			##buscar máximo de energía
			c_ener = 0
			m_ener = (0,0)
			for i in range(8):
				if(ener[i][0]>c_ener):
					#comprobar mapa
					if(self.map[cy+ener[i][1][1]][cx+ener[i][1][0]]==1):
						c_ener = ener[i][0]
						m_ener = ener[i][1]
			self.log("Energi move: %s",m_ener)
			return self.move(m_ener[0],m_ener[1])
			
	elif triangle == True:
		##triangulo
		t = True
	else:
		##tengo pero no para triangulo
		a = True
		
	#comprobar si el destino cruzaría conexiones

	
	next_m_dist = self.maxdist
	next_m_ener = 0
	next_m = (0,0)
	for mv in range(8):
		if(dist[mv][0] < next_m_dist):
			next_m_dist = dist[mv][0]
			next_m = dist[mv][1]
			next_m_ener = view[view_cy+next_m[1]][view_cx+next_m[0]]
		elif(dist[mv][0] == next_m_dist):
			if(next_m_ener < view[view_cy+dist[mv][1][1]][view_cx+dist[mv][1][0]]):
				next_m_dist = dist[mv][0]
				next_m = dist[mv][1]
				next_m_ener = view[view_cy+next_m[1]][view_cx+next_m[0]]
	self.log("move_x: %s move_y: %s",next_m[0],next_m[1])		
        return self.move(next_m[0],next_m[1])

if __name__ == "__main__":
    iface = interface.Interface(Wuibo)
    iface.run()
