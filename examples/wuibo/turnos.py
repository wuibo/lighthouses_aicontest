#!/usr/bin/python
# -*- coding: utf-8 -*-

import random, sys
import interface
import math

class Wuibo(interface.Bot):
    """Bot de juego"""
    NAME = "Turnos"

    def __init__(self,init_state):
        """Inicializar el bot"""
    	self.log("prueba")
    	self.m_energy = False
    	self.player_num = init_state["player_num"]
    	self.player_count = init_state["player_count"]
    	self.init_pos = init_state["position"]
    	self.map = init_state["map"]
    	self.maxy = len(self.map)
    	self.maxx = len(self.map[0])
    	self.t_faro = 0
    	self.maxdist = self.maxx * self.maxy*self.maxx*self.maxy
    	self.lighthouses = map(tuple, init_state["lighthouses"])
    	self.light_count = len(self.lighthouses)
    	self.idlight = []
    	self.conect_o = []
    	self.f_mind = -1
	self.t_turn = 0
    	#self.log("x: %s",' '.join(str(e) for e in array))
    	#el indice es el id y el valor (x,y) las coordenadas
    	#identificador del faro y sus coordenadas (x,y)
    
    	#cargar array de movimiento
    	self.movd = [[self.maxdist,(-1,-1)],[self.maxdist,(-1,0)],[self.maxdist,(-1,+1)],[self.maxdist,(0,+1)],[self.maxdist,(+1,+1)],[self.maxdist,(+1,0)],[self.maxdist,(+1,-1)],[self.maxdist,(0,-1)]]
    	self.ener = [[0,0,(-1,-1)],[0,0,(-1,0)],[0,0,(-1,+1)],[0,0,(0,+1)],[0,0,(+1,+1)],[0,0,(+1,0)],[0,0,(+1,-1)],[0,0,(0,-1)]]
    			
    
    	for x in xrange(self.light_count):
    		new = [self.lighthouses[x],[]]
    		self.idlight.append(new)
    	"""for lh in range(self.light_count):
    		self.idlight[lh] =self.lighthouses[lh]"""
    
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
    
    	"""
    	#Energia por turno
    	self.energi = []
    	for ey in range(self.maxy):
    		e_x = []
    		for ex in range(self.maxx):
    			i_energi = 0
    			for lh in  range(self.light_count):
    				i_dist = self.light_dist[lh][ey][ex]
    				if(i_dist < 5):
    					i_energi += 5-self.light_dist[lh][ey][ex]
    			e_x.append(i_energi)
    		self.energi.append(e_x)
    	"""
    	"""for ty in reversed(range(self.maxy)):
    		arry = []
    		for tx in range(self.maxx):
    			arry.append(self.energi[ty][tx])
    		self.log("%s",' '.join(str(e).zfill(3) for e in arry))
    	"""
    	#carga de triangulos
    	self.tri_total = int(math.factorial(self.light_count)/(math.factorial(3)*math.factorial(self.light_count-3)))
    	self.tri_count = 0
    	self.tri=[]
    	fst = 0
    	snd = 1
    	cnt = 2
    	for i in xrange(self.tri_total):
    		new = [[fst,snd,cnt],0,0,0,0]
    		
    		#puntos
    		new[2]=self.TrianglePoints(self.get_cord(fst),self.get_cord(snd),self.get_cord(cnt))
    		#perimetro
    		cord1 = self.get_cord(new[0][0])
    		cord2 = self.get_cord(new[0][1])
    		cord3 = self.get_cord(new[0][2])
    		d12 = self.light_dist[new[0][0]][cord2[1]][cord2[0]]
    		d23 = self.light_dist[new[0][1]][cord3[1]][cord3[0]]
    		d31 = self.light_dist[new[0][2]][cord1[1]][cord1[0]]
    		new[3] = d12 + d23 + d31
    		#energía
    		new[4] = (new[3] + 6+new[3]/3) * 10
    		#self.log("(%s): %s",str(new[0]),str(new[2]))
    		#solo tener en cuenta los triangulos con puntos
    		if(new[2] > 0):
    			#self.log("tri(%s): points %s perimetro: %s triangulos: %s coordenadas: %s,%s,%s",str(self.tri_count),str(new[2]),str(new[3]),str(new[0]),str(cord1),str(cord2),str(cord3))
    			#self.log("%s",str(new))
    			self.tri.append(new)
    			self.idlight[fst][1] = self.idlight[fst][1] + [self.tri_count]
    			self.idlight[snd][1] = self.idlight[snd][1] + [self.tri_count]
    			self.idlight[cnt][1] = self.idlight[cnt][1] + [self.tri_count]
    			self.tri_count += 1
    		#avanzar en la cuenta
    		cnt += 1
    		if cnt >= self.light_count:
    			snd +=1
    			if snd >= self.light_count-1:
    				fst +=1
    				snd = fst +1
    			cnt = snd +1
    		
    		
    	#inicializar parametros de control e cambios en trinagulo elegido
    	self.o1 = [-1,-1,-1,-1,-1,-1]
    	self.o2 = [-1,-1,-1,-1,-1,-1]
    	self.ee = [-1,-1,-1]	
	
    def get_id(self,x,y):
    	"""Devuelve el id del light house desde las coordenadas"""
    	for lh in range(self.light_count):
    		if(self.idlight[lh][0] == (x,y)):
    			return lh

    def get_cord(self,i):
    	"""Devuelve las coordenadas desde el id"""
    	return self.idlight[i][0]

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
	
    def sign(self,p1,p2,p3):
	    return (p1[0] - p3[0]) * (p2[1]-p3[1]) - (p2[0]-p3[0]) * (p1[1] - p3[1])

    def PointInAABB(self,pt, c1,c2):
	    return c2[0] <= pt[0] <= c1[0] and c2[1] <= pt[1] <= c1[1]

    def PointInTriangle(self,pt,t1,t2,t3):
    	b1 = self.sign(pt,t1,t2) <= 0
    	b2 = self.sign(pt,t2,t3) <= 0
    	b3 = self.sign(pt,t3,t1) <= 0
    	return  ((b1 == b2) and (b2 == b3)) and \
    		self.PointInAABB(pt,map(max,t1,t2,t3),map(min,t1,t2,t3))

    def TrianglePoints(self,t1,t2,t3):
    	cnt = 0
    	max_x = max(t1[0],t2[0],t3[0])
    	min_x = min(t1[0],t2[0],t3[0])
    	max_y = max(t1[1],t2[1],t3[1])
    	min_y = min(t1[1],t2[1],t3[1])
    	for i_x in xrange(min_x,max_x+1):
    		for i_y in xrange(min_y,max_y+1):
    			if self.PointInTriangle((i_x,i_y),t1,t2,t3) and self.map[i_y][i_x] == 1:
    				cnt += 1
    	return cnt

    def gradient(self,l):
    	#Devuelve el gradiente m de una linea
    	m = None
    	#asegurar que la línea no es vertical
    	if l[0][0] != l[1][0]:
    		m = (1./(l[0][0]-l[1][0]))*(l[0][1] - l[1][1])
    	return m

    def parallel(self,l1,l2):
	    return self.gradient(l1) == self.gradient(l2)

    def crosing(self,l1,l2):
    	if(l1[0] == l2[0] or l1[0] == l2[1] or l1[1] == l2[0] or l1[1] == l2[1]):
    		return False
    	if max(l1[0][0],l1[1][0]) < min(l2[0][0],l2[1][0]):
    		#Distinta proyección X
    		return False
    	A1 = self.gradient(l1)
    	A2 = self.gradient(l2)
    	if(A1 == A2):
    		#son paralelas
    		return False
    	if l1[0][0] == l1[1][0]:
    		#lina 1 vertical
    		Xa = l1[0][0]
    		b2 = l2[0][1] - l2[0][0]*A2
    		y2 = Xa*A2+b2
    		if(y2 > max(l1[0][1],l1[1][1]) or y2 < min(l1[0][1],l1[1][1])):
    			return False
    		else:
    			return True
    	elif l2[0][0] == l2[1][0]:
    		#linea 2 vertical
    		Xa = l2[0][0]
    		b1 = l1[0][1] - l1[0][0]*A1
    		y1 = Xa*A1+b1
    		if(y1 > max(l2[0][1],l2[1][1]) or y1 < max(l2[0][1],l2[1][1])):
    			return False
    		else:
    			return True
    	else:
    		b1 = l1[0][1]-l1[0][0]*A1
    		b2 = l2[0][1]-l2[0][0]*A2
    		Xa = (b2 - b1)/(A1-A2)
    		if ((Xa < max(min(l1[0][0],l1[1][0]),min(l2[0][0],l2[1][0]))) or \
    			(Xa > min(max(l1[0][0],l1[1][0]),max(l2[0][0],l2[1][0])))):
    			return False
    		else:
    			return True	


    def play(self, state):
        """Jugar: llamado cada turno.
        Debe devolver una acción (jugada)."""
    	#posición actual
        cx, cy = state["position"]
    	#cargar la situación de los faros
        lighthouses = dict((tuple(lh["position"]), lh)
                                for lh in state["lighthouses"])
    
    	#Identificar los faros de los que tenemos la clave y somos dueños (sino no se peude unir)
	#incluir gestión de prob
	done_tri = []
    	key_id = []
	self.t_turn += 1
    	for i in xrange(self.light_count):
    		(lx,ly) = self.get_cord(i)
    		if(lighthouses[(lx,ly)]["have_key"] and lighthouses[(lx,ly)]["owner"] == self.player_num):
    			key_id = key_id + [i]
    			self.log("option key: = %s (%s,%s)",str(i),str(lx),str(ly))
		for lt in self.idlight[i][1]:
			#no tratado
			if lt not in done_tri:
				done_tri = done_tri + [lt]
				for ti in self.tri[lt][0]:
					t_cord = self.get_cord(ti)
					if lighthouses[(t_cord[0],t_cord[1])]["owner"] >= 0 and lighthouses[(t_cord[0],t_cord[1])]["owner"] != self.player_num:
						self.tri[lt][1] += 1
						break
    	self.log("key_id: %s",str(key_id))
    	self.log("energi: %s position: %s t_faro: %s",state["energy"],state["position"],self.t_faro)
    	
    	#Gestión de vista
    	view = state["view"]
    	view_y = len(view)
    	view_x = len(view[0])
    	view_cx = view_x/2
    	view_cy = view_y/2
    
    	self.log("PreObjetive: %s, %s",str(self.o1[4]),str(self.o1[5]))
    	#nuevo objetivo
    	self.get_objetive(lighthouses,key_id,cx,cy)
	self.log("PostObjetive: %s, %s",str(self.o1[4]),str(self.o1[5]))
    	"""
    	if(self.o1[0] >= 0):
    		if(self.m_energy):
    			#el anterior movimiento ha sido para energia
    			self.log("Anterior por energia: %s",str(self.m_energy))
    			self.get_objetive(lighthouses,key_id,cx,cy)
    		else:	
    			#ya ha un objetivo elegido y el anterior no fue por movimiento
    			if not(self.ee[0]==lighthouses[self.get_cord(self.tri[self.o1[0]][0][0])]["energy"] and \
    			self.ee[1]==lighthouses[self.get_cord(self.tri[self.o1[0]][0][1])]["energy"] and \
    			self.ee[2]==lighthouses[self.get_cord(self.tri[self.o1[0]][0][2])]["energy"]):
    					
    				#a cambiado elegir o1
    				self.log("Cambio de energia")
    				self.get_objetive(lighthouses,key_id,cx,cy)
    	else:
    		#elegir o1
    		self.log("No había selección")
    		self.get_objetive(lighthouses,key_id,cx,cy)	
    	"""
    	self.log("triangulo: %s faros [%s %s,%s %s,%s %s]",str(self.o1[0]),
    	str(self.tri[self.o1[0]][0][0]),str(self.get_cord(self.tri[self.o1[0]][0][0])),
    	str(self.tri[self.o1[0]][0][1]),str(self.get_cord(self.tri[self.o1[0]][0][1])),
    	str(self.tri[self.o1[0]][0][2]),str(self.get_cord(self.tri[self.o1[0]][0][2])))
    
    	(nx,ny) = self.get_cord(self.o1[4])
    	#comprobar si movimiento por energía
    	if lighthouses[(nx,ny)]["owner"] == self.player_num:
			#si es propio a por el
    		a_energy = self.tri[self.o1[0]][4] - lighthouses[(nx,ny)]["energy"]
    		if(state["energy"]>a_energy):
    		    a_energy += (state["energy"]-a_energy)/2
    		self.m_energy = False
    	else:
			#no es propi
    		f_cnt = 0
    		for f in self.tri[self.o1[0]][0]:
    			(fx,fy) = self.get_cord(f)
    			if lighthouses[(fx,fy)]["owner"] == self.player_num:
    				f_cnt += 1
    		if f_cnt > 0:
				#si ya tenemos alguno y tenemos más energía que el faro
				if lighthouses[(nx,ny)]["energy"] < state["energy"]:
					n_ener = self.tri[self.o1[0]][4] - self.tri[self.o1[0]][4]*f_cnt/3 + lighthouses[(nx,ny)]["energy"]
					y_ener = state["energy"] + self.light_dist[self.o1[4]][cy][cx]*10
					if n_ener > y_ener:
						self.m_energy = True
					else:
						a_energy = n_ener + (state["energy"]-n_ener)/2
						self.m_energy = False
				else:
				    self.m_energy = True
    		else:
				#no tenemos ninguno, mirar energía
        	    n_ener = lighthouses[(nx,ny)]["energy"] + self.tri[self.o1[0]][4]
        	    y_ener = state["energy"] + self.light_dist[self.o1[4]][cy][cx]*10
        	    self.log("need: %s yo: %s",str(n_ener),str(y_ener))
        	    if n_ener > y_ener:
        	    	self.m_energy = True
        	    else:
        	    	a_energy = n_ener + (state["energy"]-n_ener)/2
        	    	self.m_energy = False
    
    	#si estamos en el faro vamos a por el (atack,connect)
    	self.log("yo: (%s,%s) dest: %s (%s,%s) cnd: %s",str(cx),str(cy),str(self.o1[4]),str(nx),str(ny),str(self.o1[5]))
    	#acciones par ir a por el faro
    	temp_id = self.get_id(cx,cy)
    	#if (cx, cy) in lighthouses and temp_id in self.tri[self.o1[0]][0] and self.m_energy == False:
	if ((cx, cy) in lighthouses and temp_id == self.o1[4] and self.m_energy == False) or self.t_faro == 1:
    		my_id = self.get_id(cx,cy)
    		#estamos en el faro
    		if self.t_faro == 1:
    			possible_connections = []
    			for dest in lighthouses:
    				#no conectar con sigo mismo
    				#no conectar si no tenemos llave
    				#no conectar si ya estań conectardos
    				#no conectar si hay cruces
    				#no conectar si no controlamos el destino
    				did = self.get_id(dest[0],dest[1])
    				if (dest != (cx,cy) and
    				    lighthouses[dest]["have_key"] and
    				    [cx,cy] not in lighthouses[dest]["connections"] and
    				    not(self.check_croses(lighthouses,did,my_id)) and
    				    lighthouses[dest]["owner"] == self.player_num):
    				    possible_connections.append(dest)
    			if possible_connections:
    				self.t_faro = 2
    				self.log("CONNECT: %s",''.join(str(e) for e in possible_connections))
    				if len(possible_connections) > 1:
    					pc_td = 0
    					pc_i = -1
    					for pc in possible_connections:
    						pc_id = self.get_id(pc[0],pc[1])
    						pc_d = self.light_dist[pc_id][cy][cx]
    						if pc_d > pc_td:
    							pc_td = pc_d
    							pc_i = pc
    					return self.connect(pc_i)
    				else:
    					return self.connect(random.choice(possible_connections))
    		elif self.t_faro == 0:
    			if(state["energy"] >= 5):
    				self.t_faro = 1
    				self.log("ATTACK: %s",a_energy)
    				return self.attack(a_energy)
    	self.t_faro = 0	
    
    	#no estamos en el faro o ya hemos realizado las acciones
    	#buscar el siguiente faro
    	at = self.tri[self.o1[0]]
    	#comprobar si ya tengo el siguiente
    	if(cx == nx and cy == ny):
    		self.log("Ya lo tenemos siguiente (%s,%s), %s",str(nx),str(ny),str(lighthouses[(nx,ny)]["have_key"]))
    		#buscar siguiente destino
    		#comprobar si tiene conexión con alguno
    		ncon = [] #id de los que no están conectados
    		otros = [] #coordenadas del resto de faros
    		self.log("ya conectados: %s", ''.join(str(e) for e in lighthouses[(nx,ny)]["connections"]))
    		for ll in at[0]:
    			if ll != self.o1[4]:
    				#no es el propio
    				cordn = self.get_cord(ll)
    				otros = otros + [cordn]
    				if ([cordn[0],cordn[1]] not in lighthouses[(nx,ny)]["connections"]):
    					self.log("cord no: %s",str(cordn))
    					ncon = ncon + [ll]
    		self.log("No conectados: %s",' '.join(str(e) for e in ncon))
    		self.log("Otros: %s",' '.join(str(e) for e in otros))
    		if len(ncon) == 0:
    			#comprobar la conexión entre los otros dos
    			if ([otros[0][0],otros[0][1]] not in lighthouses[otros[1]]["connections"]):
    				#no están conectados
    				#buscar el cercano
    				id1 = self.get_id(otros[0][0],otros[0][1])
    				id2 = self.get_id(otros[1][0],otros[1][1])
    				td1 = self.light_dist[id1][cy][cx]
    				td2 = self.light_dist[id2][cy][cx]
    				if(td1 < td2):
    					self.o1[4] = id1
    				else:
    					self.o1[4] = id2
    				self.o1[5] = -1
    			else:
    				#ya lo tenemos, buscar otro
    				self.log("Triangulo completo")
    				self.get_objetive(lighthouses,key_id,cx,cy)
    		elif len(ncon) == 2:
    			#ninguna conexión
    			#ir a por el más cercano
    			id1 = self.get_id(otros[0][0],otros[0][1])
    			id2 = self.get_id(otros[1][0],otros[1][1])
    			td1 = self.light_dist[id1][cy][cx]
    			td2 = self.light_dist[id2][cy][cx]
    			self.o1[5] = self.o1[4]
    			if(td1 < td2):
    				self.o1[4] = id1
    			else:
    				self.o1[4] = id2
    		else:
    			#hay uno al siguiente
    			self.o1[5] = self.o1[4]
    			self.o1[4] = ncon[0]
    
    	
    	self.log("PreMover: %s,%s",str(self.o1[4]),str(self.o1[5]))
    	#nos vamos a mover
    	for i in xrange(3):
    		cordl = self.get_cord(self.tri[self.o1[0]][0][i])
    		if(lighthouses[cordl]["energy"] <= 10):
    			self.ee[i] = 0
    		else:
    			self.ee[i] = lighthouses[cordl]["energy"]-10
    	
    	#comprobar energía, ir o cargar
    	if not(self.m_energy):		
    		#energía suficiente, a por el
    		if self.check_croses(lighthouses,self.o1[4],self.o1[5]):
    			if not(lighthouses[(self.conect_o[0][0],self.conect_o[0][1])]["owner"] == self.player_num):
    				t_id1 = self.get_id(self.conect_o[0][0],self.conect_o[0][1])
    				t_id2 = self.get_id(self.conect_o[1][0],self.conect_o[1][1])
    				td1 = self.light_dist[t_id1][cy][cx]
    				td2 = self.light_dist[t_id2][cy][cx]
    				if td1 < td2:
    					temp_des = t_id1
    				else:
    					temp_des = t_id2
    			else:
    				#el más cercano no mio
    				temp_des = self.f_mind
    		else:
    			temp_des = self.o1[4]
    		#No estamos en el faro o ya esta conectado
    		if(cx==0 and cy==0):
    			"""left-down"""
    			self.movd[0][0] = self.maxdist
    			self.movd[1][0] = self.maxdist
    			self.movd[2][0] = self.maxdist
    			self.movd[3][0] = self.light_dist[temp_des][cy+1][cx]
    			self.movd[4][0] = self.light_dist[temp_des][cy+1][cx+1]
    			self.movd[5][0] = self.light_dsit[temp_des][cy][cx+1]
    			self.movd[6][0] = self.maxdist
    			self.movd[7][0] = self.maxdist
    		elif(cy==0 and cx>0 and cx<(self.maxx-1)):
    			"""down"""
    			self.movd[0][0] = self.maxdist
    			self.movd[1][0] = self.light_dist[temp_des][cy][cx-1]
    			self.movd[2][0] = self.light_dist[temp_des][cy+1][cx-1]
    			self.movd[3][0] = self.light_dist[temp_des][cy+1][cx]
    			self.movd[4][0] = self.light_dist[temp_des][cy+1][cx+1]
    			self.movd[5][0] = self.light_dist[temp_des][cy][cx+1]
    			self.movd[6][0] = self.maxdist
    			self.movd[7][0] = self.maxdist
    		elif(cy==0 and cx==(self.maxx-1)):
    			"""right-down"""
    			self.movd[0][0] = self.maxdist
    			self.movd[1][0] = self.light_dist[temp_des][cy][cx-1]
    			self.movd[2][0] = self.light_dist[temp_des][cy+1][cx-1]
    			self.movd[3][0] = self.light_dist[temp_des][cy+1][cx]
    			self.movd[4][0] = self.maxdist
    			self.movd[5][0] = self.maxdist
    			self.movd[6][0] = self.maxdist
    			self.movd[7][0] = self.maxdist
    		elif(cx==(self.maxx-1) and cy>0 and cy<(self.maxy-1)):
    			"""right"""
    			self.movd[0][0] = self.light_dist[temp_des][cy-1][cx-1]
    			self.movd[1][0] = self.light_dist[temp_des][cy][cx-1]
    			self.movd[2][0] = self.light_dist[temp_des][cy+1][cx-1]
    			self.movd[3][0] = self.light_dist[temp_des][cy+1][cx]
    			self.movd[4][0] = self.maxdist
    			self.movd[5][0] = self.maxdist
    			self.movd[6][0] = self.maxdist
    			self.movd[7][0] = self.light_dist[temp_des][cy-1][cx] 
    		elif(cx==(self.maxx-1) and cy==(self.maxy-1)):
    			"""right-up"""
    			self.movd[0][0] = self.light_dist[temp_des][cy-1][cx-1]
    			self.movd[1][0] = self.light_dist[temp_des][cy][cx-1]
    			self.movd[2][0] = self.maxdist
    			self.movd[3][0] = self.maxdist
    			self.movd[4][0] = self.maxdist
    			self.movd[5][0] = self.maxdist
    			self.movd[6][0] = self.maxdist
    			self.movd[7][0] = self.light_dist[temp_des][cy-1][cx]
    		elif(cy==(self.maxy-1) and cx>0 and cx<(self.maxx-1)):
    			"""up""" 
    			self.movd[0][0] = self.light_dist[temp_des][cy-1][cx-1]
    			self.movd[1][0] = self.light_dist[temp_des][cy][cx-1]
    			self.movd[2][0] = self.maxdist
    			self.movd[3][0] = self.maxdist
    			self.movd[4][0] = self.maxdist
    			self.movd[5][0] = self.light_dist[temp_des][cy][cx+1]
    			self.movd[6][0] = self.light_dist[temp_des][cy-1][cx+1]
    			self.movd[7][0] = self.light_dist[temp_des][cy-1][cx]
    		elif(cy==(self.maxy-1) and cx==0):
    			"""left-up""" 
    			self.movd[0][0] = self.maxdist
    			self.movd[1][0] = self.maxdist
    			self.movd[2][0] = self.maxdist
    			self.movd[3][0] = self.maxdist
    			self.movd[4][0] = self.maxdist
    			self.movd[5][0] = self.light_dist[temp_des][cy][cx+1]
    			self.movd[6][0] = self.light_dist[temp_des][cy-1][cx+1]
    			self.movd[7][0] = self.light_dist[temp_des][cy-1][cx]
    		elif(cx==0 and cy>0 and cy<(self.maxy-1)):
    			"""left""" 
    			self.movd[0][0] = self.maxdist
    			self.movd[1][0] = self.maxdist
    			self.movd[2][0] = self.maxdist
    			self.movd[3][0] = self.light_dist[temp_des][cy+1][cx]
    			self.movd[4][0] = self.light_dist[temp_des][cy+1][cx+1]
    			self.movd[5][0] = self.light_dist[temp_des][cy][cx+1]
    			self.movd[6][0] = self.light_dist[temp_des][cy-1][cx+1]
    			self.movd[7][0] = self.light_dist[temp_des][cy-1][cx] 
    		else:
    			self.movd[0][0] = self.light_dist[temp_des][cy-1][cx-1]
    			self.movd[1][0] = self.light_dist[temp_des][cy][cx-1]
    			self.movd[2][0] = self.light_dist[temp_des][cy+1][cx-1]
    			self.movd[3][0] = self.light_dist[temp_des][cy+1][cx]
    			self.movd[4][0] = self.light_dist[temp_des][cy+1][cx+1]
    			self.movd[5][0] = self.light_dist[temp_des][cy][cx+1]
    			self.movd[6][0] = self.light_dist[temp_des][cy-1][cx+1]
    			self.movd[7][0] = self.light_dist[temp_des][cy-1][cx] 
    	
    
    		#cargar energia
    		self.ener[0][0] = view[view_cy-1][view_cx-1]
    		self.ener[1][0] = view[view_cy][view_cx-1]
    		self.ener[2][0] = view[view_cy+1][view_cx-1]
    		self.ener[3][0] = view[view_cy+1][view_cx]
    		self.ener[4][0] = view[view_cy+1][view_cx+1]
    		self.ener[5][0] = view[view_cy][view_cx+1]
    		self.ener[6][0] = view[view_cy-1][view_cx+1]
    		self.ener[7][0] = view[view_cy-1][view_cx]
    
    		next_m_dist = self.maxdist
    		next_m_ener = 0
    		next_m = (0,0)
    		for mv in xrange(8):
    			if(self.movd[mv][0] < next_m_dist):
    				next_m_dist = self.movd[mv][0]
    				next_m = self.movd[mv][1]
    				next_m_ener = self.ener[mv][0]
    			elif(self.movd[mv][0] == next_m_dist):
    				if(next_m_ener < self.ener[mv][0]):
    					next_m_dist = self.movd[mv][0]
    					next_m = self.movd[mv][1]
    					next_m_ener = self.ener[mv][0]
    		self.log("Destino: %s [%s]",str(temp_des),str(self.get_cord(temp_des)))
    		self.log("Move objetive. move_x: %s move_y: %s",next_m[0],next_m[1])
    		return self.move(next_m[0],next_m[1])
    
    	else:
    		#no hay energia suficiente, cargar
    		#cargar energia
    		t_ener0 = view[view_cy-2][view_cx-2]
    		t_ener1 = view[view_cy-1][view_cx-2]
    		t_ener2 = view[view_cy][view_cx-2]
    		t_ener3 = view[view_cy][view_cx-1]
    		t_ener4 = view[view_cy][view_cx]
    		t_ener5 = view[view_cy-1][view_cx]
    		t_ener6 = view[view_cy-2][view_cx]
    		t_ener7 = view[view_cy-2][view_cx-1]
    		self.ener[0][0] = view[view_cy-1][view_cx-1]
    		self.ener[0][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    		
    		t_ener0 = view[view_cy-1][view_cx-2]
    		t_ener1 = view[view_cy][view_cx-2]
    		t_ener2 = view[view_cy+1][view_cx-2]
    		t_ener3 = view[view_cy+1][view_cx-1]
    		t_ener4 = view[view_cy+1][view_cx]
    		t_ener5 = view[view_cy][view_cx]
    		t_ener6 = view[view_cy-1][view_cx]
    		t_ener7 = view[view_cy-1][view_cx-1]
    		self.ener[1][0] = view[view_cy][view_cx-1] 
    		self.ener[1][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    	
    		t_ener0 = view[view_cy][view_cx-2]
    		t_ener1 = view[view_cy+1][view_cx-2]
    		t_ener2 = view[view_cy+2][view_cx-2]
    		t_ener3 = view[view_cy+2][view_cx-1]
    		t_ener4 = view[view_cy+2][view_cx]
    		t_ener5 = view[view_cy+1][view_cx]
    		t_ener6 = view[view_cy][view_cx]
    		t_ener7 = view[view_cy][view_cx-1]
    		self.ener[2][0] = view[view_cy+1][view_cx-1] 
    		self.ener[2][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    
    		t_ener0 = view[view_cy][view_cx-1]
    		t_ener1 = view[view_cy+1][view_cx-1]
    		t_ener2 = view[view_cy+2][view_cx-1]
    		t_ener3 = view[view_cy+2][view_cx]
    		t_ener4 = view[view_cy+2][view_cx+1]
    		t_ener5 = view[view_cy+1][view_cx+1]
    		t_ener6 = view[view_cy][view_cx+1]
    		t_ener7 = view[view_cy][view_cx]
    		self.ener[3][0] = view[view_cy+1][view_cx] 
    		self.ener[3][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    
    		t_ener0 = view[view_cy][view_cx]
    		t_ener1 = view[view_cy+1][view_cx]
    		t_ener2 = view[view_cy+2][view_cx]
    		t_ener3 = view[view_cy+2][view_cx+1]
    		t_ener4 = view[view_cy+2][view_cx+2]
    		t_ener5 = view[view_cy+1][view_cx+2]
    		t_ener6 = view[view_cy][view_cx+2]
    		t_ener7 = view[view_cy][view_cx+1]
    		self.ener[4][0] = view[view_cy+1][view_cx+1] 
    		self.ener[4][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    
    		t_ener0 = view[view_cy-1][view_cx]
    		t_ener1 = view[view_cy][view_cx]
    		t_ener2 = view[view_cy+1][view_cx]
    		t_ener3 = view[view_cy+1][view_cx+1]
    		t_ener4 = view[view_cy+1][view_cx+2]
    		t_ener5 = view[view_cy][view_cx+2]
    		t_ener6 = view[view_cy-1][view_cx+2]
    		t_ener7 = view[view_cy-1][view_cx+1]
    		self.ener[5][0] = view[view_cy][view_cx+1] 
    		self.ener[5][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    
    		t_ener0 = view[view_cy-2][view_cx]
    		t_ener1 = view[view_cy-1][view_cx]
    		t_ener2 = view[view_cy][view_cx]
    		t_ener3 = view[view_cy][view_cx+1]
    		t_ener4 = view[view_cy][view_cx+2]
    		t_ener5 = view[view_cy-1][view_cx+2]
    		t_ener6 = view[view_cy-2][view_cx+2]
    		t_ener7 = view[view_cy-2][view_cx+1]
    		self.ener[6][0] = view[view_cy-1][view_cx+1]
    		self.ener[6][1] = max(t_ener0,t_ener1,t_ener2,t_ener3,t_ener4,t_ener5,t_ener6,t_ener7)
    
    		t_ener0 = view[view_cy-2][view_cx-1]
    		t_ener1 = view[view_cy-1][view_cx-1]
    		t_ener2 = view[view_cy][view_cx-1]
    		t_ener3 = view[view_cy][view_cx]
    		t_ener4 = view[view_cy][view_cx+1]
    		t_ener5 = view[view_cy-1][view_cx+1]
    		t_ener6 = view[view_cy-2][view_cx+1]
    		t_ener7 = view[view_cy-2][view_cx]
    		self.ener[7][0] = view[view_cy-1][view_cx]
    		self.ener[7][1] = max(t_ener0,t_ener1,t_ener2,t_ener4,t_ener5,t_ener6,t_ener7)
    
    		"""234"""
    		"""1*5"""
    		"""076"""
    		next_m_ener = 0
    		next_m = (0,0)
    		next_m_e2 = 0
    		for mv in xrange(8):
    		    if ((cy+self.ener[mv][2][1]) >= 0 and (cy+self.ener[mv][2][1]) < self.maxy and (cx+self.ener[mv][2][0]) >= 0 and (cx+self.ener[mv][2][0]) < self.maxx):
        			if(next_m_ener < self.ener[mv][0] and self.map[cy+self.ener[mv][2][1]][cx+self.ener[mv][2][0]] ==1):
        				next_m_ener = self.ener[mv][0]
        				next_m = self.ener[mv][2]
        				next_m_e2 = self.ener[mv][1]
        			elif (next_m_ener == self.ener[mv][0]):
        			    if next_m_e2 < self.ener:
        			    	next_m_ener = self.ener[mv][0]
        			    	next_m = self.ener[mv][2]
        			    	next_m_e2 = self.ener[mv][1]
    		self.log("Move ener: move_x: %s move_y: %s",next_m[0],next_m[1])
    		return self.move(next_m[0],next_m[1])

    def check_croses(self,light,f1,f2):
    	self.conect_o = []
    	if f1 == -1 or f2 == -1:
    		return False
    	cord1 = self.get_cord(f1)
    	cord2 = self.get_cord(f2)
    	for l in light:
    		for c in light[l]["connections"]:
    			if self.crosing([cord1,cord2],[l,(c[0],c[1])]):
    				self.conect_o = self.conect_o + [l]
    				self.conect_o = self.conect_o + [c]
    				return True
    	return False
		
		

    def get_objetive(self,lhs,key_id,cx,cy):
    	self.log("CAMBIO OBJETIVO (%s)",str(self.o1[0]))
    	self.o2 = [-1,-1,(self.maxdist * 4),-1,-1,-1]
    	to = -1 #temporal objetive
    	f_min = self.maxdist
    	f_d = -1
    	for il in xrange(self.light_count):
    		td = self.light_dist[il][cy][cx]
    		#del que no tengamos llave
    		if td < f_min and il not in key_id:
    			f_min = td
    			f_d = il
    	for tr in xrange(self.tri_count):
		cnd = []
		otros = []
		cord = self.get_cord(self.tri[tr][0][0])
		if lhs[(cord[0],cord[1])]["owner"] == self.player_num:
			if self.tri[tr][0][0] in key_id:
				cnd = cnd + [[self.tri[tr][0][0],1]]
			else:
				cnd = cnd + [[self.tri[tr][0][0],0]]
		else:
			otros = otros + [self.tri[tr][0][0]]

		cord = self.get_cord(self.tri[tr][0][1])
		if lhs[(cord[0],cord[1])]["owner"] == self.player_num:
			if self.tri[tr][0][1] in key_id:
				cnd = cnd + [[self.tri[tr][0][1],1]]
			else:
				cnd = cnd + [[self.tri[tr][0][1],0]]
		else:
			otros = otros + [self.tri[tr][0][1]]

		cord = self.get_cord(self.tri[tr][0][2])
		if lhs[(cord[0],cord[1])]["owner"] == self.player_num:
			if self.tri[tr][0][2] in key_id:
				cnd = cnd + [[self.tri[tr][0][2],1]]
			else:
				cnd = cnd + [[self.tri[tr][0][2],0]]
		else:
			otros = otros + [self.tri[tr][0][2]]
		#mirar cuantos
		if len(cnd) == 0:
			#controlo 0
			td1 = self.light_dist[self.tri[tr][0][0]][cy][cx]
			td2 = self.light_dist[self.tri[tr][0][1]][cy][cx]
			td3 = self.light_dist[self.tri[tr][0][2]][cy][cx]
			if td1 < td2 and td1 < td3:
				t1 = td1 + self.tri[tr][3]
				nxt = self.tri[tr][0][0]
			elif td2 < td3:
				t1 = td2 + self.tri[tr][3]
				nxt = self.tri[tr][0][1]
			else:
				t1 = td3 + self.tri[tr][3]
				nxt = self.tri[tr][0][2]
			#check
			if to == -1:
				#comprobar si hay cruces
				if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
					continue
				self.o2 = [tr,self.tri[tr][2],t1,0,nxt,-1]
				to = 0
			else:
				if self.check_tri(t1,self.tri[tr][2],tr):
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					self.o2 = [tr,self.tri[tr][2],t1,0,nxt,-1]
		elif len(cnd) == 1:
			#controlo 1
			if cnd[0][1] == 1:
				#tengo llave
				n_cnd = cnd[0][0]
				tdo1 = self.light_dist[otros[0]][cy][cx]
				tdo2 = self.light_dist[otros[1]][cy][cx]
				cord1 = self.get_cord(otros[0])
				cord2 = self.get_cord(otros[1])
				dotros = self.light_dist[otros[1]][cord1[1]][cord1[0]]
				dc1 = self.light_dist[cnd[0][0]][cord1[1]][cord1[0]]
				dc2 = self.light_dist[cnd[0][0]][cord2[1]][cord2[0]]
	
				dt1 = tdo1 + dotros + dc1
				dt2 = tdo2 + dotros + dc2
				if dt1 < dt2:
					nxt = otros[0]
					t1 = dt1
				else:		
					nxt = otros[1]
					t1 = dt2
				#check
				if to == -1:
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
					to = 0
				else:
					if self.check_tri(t1,self.tri[tr][2],tr):
						#comprobar si hay cruces
						if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
							continue
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
			
			else:
				#no tengo llave, como sin controlar
				td1 = self.light_dist[self.tri[tr][0][0]][cy][cx]
				td2 = self.light_dist[self.tri[tr][0][1]][cy][cx]
				td3 = self.light_dist[self.tri[tr][0][2]][cy][cx]
				if td1 < td2 and td1 < td3:
					t1 = td1 + self.tri[tr][3]
					nxt = self.tri[tr][0][0]
				elif td2 < td3:
					t1 = td2 + self.tri[tr][3]
					nxt = self.tri[tr][0][1]
				else:
					t1 = td3 + self.tri[tr][3]
					nxt = self.tri[tr][0][2]
				#check
				if to == -1:
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					self.o2 = [tr,self.tri[tr][2],t1,0,nxt,-1]
					to = 0
				else:
					if self.check_tri(t1,self.tri[tr][2],tr):
						#comprobar si hay cruces
						if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
							continue
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,-1]		

		elif len(cnd) == 2:
			#controlo 2
			cordc1 = self.get_cord(cnd[0][0])
			cordc2 = self.get_cord(cnd[1][0])
			if [cordc2[0],cordc2[1]] in lhs[(cordc1[0],cordc1[1])]["connections"]:
				#estan conectados
				if cnd[0][1] == 1 and cnd[1][1] == 1:
					#tenemos las 2 llaves
					to1 = self.light_dist[otros[0]][cordc1[1]][cordc1[0]]
					to2 = self.light_dist[otros[0]][cordc2[1]][cordc2[0]]
					dt = self.light_dist[otros[0]][cy][cx]
					#haremos la conexión más lejana
					nxt = otros[0]
					if to1 < to2:
						#unimos con el 2 y vamos luego al 1
						n_cnd = cnd[1][0]
						t1 = to1 + dt
					else:
						#unicos con el 1 y vamos luego al 2
						n_cnd = cnd[0][0]
						t1 = to2 + dt
				
				elif cnd[0][1] == 1:
					#solo la llave del primero
					to = self.light_dist[otros[0]][cordc2[1]][cordc2[0]]
					dt = self.light_dist[otros[0]][cy][cx]
					nxt = otros[0]
					n_cnd = cnd[0][0]
					t1 = to + nxt
				elif cnd[1][1] == 1:
					#solo la llave del segundo
					to = self.light_dist[otros[0]][cordc1[1]][cordc1[0]]
					dt = self.light_dist[otros[0]][cy][cx]
					nxt = otros[0]
					n_cnd = cnd[1][0]
					t1 = to + nxt
				else:
					#ninguna llave
					to1 = self.light_dist[cnd[0][0]][cy][cx]
					to2 = self.light_dist[cnd[1][0]][cy][cx]
					dt = self.light_dist[otros[0]][cordc1[1]][cordc1[0]]+self.light_dist[otros[0]][cordc2[1]][cordc2[0]]
					if to1 < to2:
						nxt = cnd[0][0]
						n_cnd = -1
						t1 = to1 + dt
					else:
						nxt = cnd[1][0]
						n_cnd = -1
						t1 = to2 + dt
				#check
				if to == -1:
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
					to = 0
				else:
					if self.check_tri(t1,self.tri[tr][2],tr):
						#comprobar si hay cruces
						if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
							continue
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
			else:
				#no están conectados
				if cnd[0][1] == 1 and cnd[1][1] == 1:
					#tenemos las 2 llaves
					tl1 = self.light_dist[otros[0]][cordc1[1]][cordc1[0]]
					tl2 = self.light_dist[otros[0]][cordc2[1]][cordc2[0]]
					dtc = self.light_dist[cnd[0][0]][cordc2[1]][cordc2[0]]
					tc1 = self.light_dist[cnd[0][0]][cy][cx]
					tc2 = self.light_dist[cnd[1][0]][cy][cx]
					tl = self.light_dist[otros[0]][cy][cx]

					#calcular si vamos primero al libre
					if tl1 < tl2:
						t1l = tl + tl1 + dtc
						cnl = cnd[1][0]
					else:
						t1l = tl + tl2 + dtc
						cnl = cnd[0][0]

					#calcluar si vamos primero al 1
					t1c1 = tc1 + tl1 + tl2
					#calcular si vamos primero al 2
					t1c2 = tc2 + tl1 + tl2

					if t1l < t1c1 and t1l < t1c2:
						#primero al libre
						nxt = otros[0]
						t1 = t1l
						n_cnd = cnl
					elif t1c1 < t1c2:
						#primero al 1 control
						nxt = cnd[0][0]
						t1 = t1c1
						n_cnd = cnd[1][0]
					else:
						#primero al 2 control
						nxt = cnd[1][0]
						t1 = t1c2
						n_cnd = cnd[0][0]
				elif cnd[0][1] == 1:
					#solo la llave del primero
					td1 = self.light_dist[cnd[1][0]][cy][cx]
					td2 = self.light_dist[otros[0]][cy][cx]
					dnc = self.light_dist[otros[0]][cordc2[1]][cordc2[0]]
					tk1 = self.light_dist[cnd[1][0]][cordc1[1]][cordc1[0]]
					tk2 = self.light_dist[otros[0]][cordc1[1]][cordc1[0]]

					dt1 = td1 + dnc + tk2
					dt2 = td2 + dnc + tk1
					if dt1 < dt2:
						#primero al otro que controlo
						t1 = dt1
						nxt = cnd[1][0]
						n_cnd = cnd[0][0]
					else:
						#primero al libre
						t1 = dt2
						nxt = otros[0]
						n_cnd = cnd[0][0]
				elif cnd[1][1] == 1:
					#solo la llave del segundo
					td1 = self.light_dist[cnd[0][0]][cy][cx]
					td2 = self.light_dist[otros[0]][cy][cx]
					dnc = self.light_dist[otros[0]][cordc1[1]][cordc1[0]]
					tk1 = self.light_dist[cnd[1][0]][cordc2[1]][cordc2[0]]
					tk2 = self.light_dist[otros[0]][cordc2[1]][cordc2[0]]

					dt1 = td1 + dnc + tk2
					dt2 = td2 + dnc + tk1
					if dt1 < dt2:
						#primero al otro que controlo
						t1 = dt1
						nxt = cnd[0][0]
						n_cnd = cnd[1][0]
					else:
						#primero al libre
						t1 = dt2
						nxt = otros[0]
						n_cnd = cnd[1][0]
				else:
					#ninguna llave
					#como si no controlo
					td1 = self.light_dist[self.tri[tr][0][0]][cy][cx]
					td2 = self.light_dist[self.tri[tr][0][1]][cy][cx]
					td3 = self.light_dist[self.tri[tr][0][2]][cy][cx]
					n_cnd = -1
					if td1 < td2 and td1 < td3:
						t1 = td1 + self.tri[tr][3]
						nxt = self.tri[tr][0][0]
					elif td2 < td3:
						t1 = td2 + self.tri[tr][3]
						nxt = self.tri[tr][0][1]
					else:
						t1 = td3 + self.tri[tr][3]
						nxt = self.tri[tr][0][2]
				#check
				if to == -1:
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
					to = 0
				else:
					if self.check_tri(t1,self.tri[tr][2],tr):
						#comprobar si hay cruces
						if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
							continue
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
				

		else:
			#controlo 3
			cordc1 = self.get_cord(cnd[0][0])
			cordc2 = self.get_cord(cnd[1][0])
			cordc3 = self.get_cord(cnd[2][0])
			td1 = self.light_dist[cnd[0][0]][cy][cx]
			td2 = self.light_dist[cnd[1][0]][cy][cx]
			td3 = self.light_dist[cnd[2][0]][cy][cx]
			t12 = self.light_dist[cnd[0][0]][cordc2[1]][cordc2[0]]
			t23 = self.light_dist[cnd[1][0]][cordc3[1]][cordc3[0]]
			t31 = self.light_dist[cnd[2][0]][cordc1[1]][cordc1[0]]
			if not([cordc1[0],cordc1[1]] in lhs[(cordc2[0],cordc2[1])]["connections"] and [cordc2[0],cordc2[1]] in lhs[(cordc3[0],cordc3[1])]["connections"] and [cordc3[0],cordc3[1]] in lhs[(cordc1[0],cordc1[1])]["connections"]):
				#Falta alguna conexión
				if [cordc1[0],cordc1[1]] in lhs[cordc2]["connections"] and [cordc2[0],cordc2[1]] in lhs[cordc3]["connections"]:
					#Falta 3-1
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					if cnd[0][1] == 1 and cnd[2][1] == 1:
						if td1 < td3:
							t1 = td1
							nxt = cnd[0][0]
							n_cnd = cnd[2][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						else:
							t1 = td3
							nxt = cnd[2][0]
							n_cnd = cnd[0][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					elif cnd[0][1] == 1:
						t1 = td3
						nxt = cnd[2][0]
						n_cnd = cnd[0][0]
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					elif cnd[2][1] == 1:
						t1 = td1
						nxt = cnd[0][0]
						n_cnd = cnd[2][0]
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					else:
						#no tenemos ninguna de las llaves
						if td1 < td3:
							t1 = td1 + t31
							nxt = cnd[0][0]
							n_cnd = -1
						else:
							t1 = td3 + t31
							nxt = cnd[2][0]
							n_cnd = -1
						

				elif [cordc2[0],cordc2[1]] in lhs[cordc3]["connections"] and [cordc3[0],cordc3[1]] in lhs[cordc1]["connections"]:
					#Falta 1-2
					if self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][0]):
						continue
					if cnd[0][1] == 1 and cnd[1][1] == 1:
						if td1 < td2:
							t1 = td1
							nxt = cnd[0][0]
							n_cnd = cnd[1][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						else:
							t1 = td2
							nxt = cnd[1][0]
							n_cnd = cnd[0][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					elif cnd[0][1] == 1:
						t1 = td2
						nxt = cnd[1][0]
						n_cnd = cnd[0][0]
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					elif cnd[1][1] == 1:
						t1 = td1
						nxt = cnd[0][0]
						n_cnd = cnd[1][0]
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					else:
						#no tenemos ninguna de las llaves
						if td1 < td2:
							t1 = td1 + t12
							nxt = cnd[0][0]
							n_cnd = -1
						else:
							t1 = td2 + t12
							nxt = cnd[1][0]
							n_cnd = -1

				elif [cordc2[0],cordc2[1]] in lhs[cordc1]["connections"] and [cordc3[0],cordc3[1]] in lhs[cordc1]["connections"]:
					#Falta 2-3
					if self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][1]):
						continue
					if cnd[1][1] == 1 and cnd[2][1] == 1:
						if td2 < td3:
							t1 = td2
							nxt = cnd[1][0]
							n_cnd = cnd[2][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						else:
							t1 = td3
							nxt = cnd[2][0]
							n_cnd = cnd[1][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break							
					elif cnd[1][1] == 1:
						t1 = td3
						nxt = cnd[2][0]
						n_cnd = cnd[1][0]
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					elif cnd[2][1] == 1:
						t1 = td2
						nxt = cnd[1][0]
						n_cnd = cnd[2][0]
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						break
					else:
						if td2 < td3:
							t1 = td2 + t23
							nxt = cnd[1][0]
							n_cnd = cnd[2][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
						else:
							t1 = td3 + t23
							nxt = cnd[2][0]
							n_cnd = cnd[1][0]
							self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]

				elif [cordc1[0],cordc1[1]] in lhs[cordc2]["connections"]:
					#Falta 2-3 y 3-1
					if cnd[0][1] == 1 and cnd[1][1] == 1:
						nxt = cnd[2][0]
						t1 = td3
						#conectar primero el largo
						if t23 < t31:
							n_cnd = cnd[0][0]
						else:
							n_cnd = cnd[1][0]
					else:
						#si no tenemso llaves
						if cnd[0][1] != 1 and cnd[1][1] != 1 and cnd[2][1] != 1:
							if td1 < td2:
								t1 = td1 + t31 + t23
								nxt = cnd[0][0]
								n_cnd = -1
							else:
								t1 = td2 + t23 + t31
								nxt = cnd[1][0]
								n_cnd = -1
						else:
							#comprobar en order y comparando
							t1 = self.maxdist
							#Si tenemos la llave del 3 (el no conectado)
							if cnd[2][1] == 1:
								if t12 < t31:
									temp1 = td1 + t12 + t23
								else:
									temp1 = td1 + t31 + t23

								if t12 < t23:
									temp2 = td2 + t12 + t31
								else:
									temp2 = td2 + t23 + t31

								if temp1 < temp2:
									t1 = temp1
									nxt = cnd[0][0]
									n_cnd = cnd[2][0]
								else:
									t1 = temp2
									nxt = cnd[1][0]
									n_cnd = cnd[2][0]

							#Si tenemos la llave del 2
							if cnd[1][1] == 1:
								temp = td3 + t31
								if temp < t1:
									t1 = temp
									nxt = cnd[2][0]
									n_cnd = cnd[1][0]

							#Si tenemos 2 y 3
							if cnd[1][1] == 1 and cnd[2][1]:
								if td3 < td1:
									temp = td3 + t31
									if temp < t1:
										t1 = temp
										nxt = cnd[2][0]
										n_cnd = cnd[1][0]
								else:
									temp = td1 + t31
									if temp < t1:
										t1 = temp
										nxt = cnd[0][0]
										n_cnd = cnd[2][0]

							#Si tenemos el 1
							if cnd[0][1] == 1:
								temp = td3 + t23
								if temp < t1:
									t1 = temp
									nxt = cnd[2][0]
									n_cnd = cnd[0][0]

							#Si tenemos el 1 y el 3:
							if cnd[0][1] == 1 and cnd[2][1]:
								if td3 < td2:
									temp = td3 + t23
									if temp < t1:
										t1 = temp
										nxt = cnd[2][0]
										n_cnd = cnd[0][0]
								else:
									temp = td2 + t23
									if temp < t1:
										t1 = temp
										nxt = cnd[1][0]
										n_cnd = cnd[2][0]



				elif [cordc2[0],cordc2[1]] in lhs[cordc3]["connections"]:
					#Falta 1-2 y 3-1
					if cnd[1][1] == 1 and cnd[2][1] == 1:
						t1 = td1
						nxt = cnd[0][0]
						if t12 < t31:
							n_cnd = cnd[2][0]
						else:
							n_cnd = cnd[1][0]
					else:
						if cnd[0][1] != 1 and cnd[1][1] != 1 and cnd[2][1] != 1:
							if td2 < td3:
								t1 = td2 + t12 + t31
								nxt = cnd[1][0]
								n_cnd = -1
							else:
								t1 = td3 + t31 + t12
								nxt = cnd[2][0]
								n_cnd = -1
						else:
							#comprobar en order y comparando
							t1 = self.maxdist
							#tenemos la llave del 1
							if cnd[2][1] == 1:
								if t23 < t12:
									temp2 = td2 + t23 + t31
								else:
									temp2 = td2 + t12 + t31

								if t23 < t31:
									temp3 = td3 + t23 + t12
								else:
									temp3 = td3 + t31 + t12

								if temp2 < temp3:
									t1 = temp2
									nxt = cnd[1][0]
									n_cnd = [0][0]
								else:
									t1 = temp3
									nxt = cnd[2][0]
									n_cnd= [0][0]

							#tenemos 1 y 3
							if cnd[0][1] == 1 and cnd[2][1] == 1:
								if td2 < td1:
									temp = td2 + t12
									if temp < t1:
										t1 = temp
										nxt = cnd[1][0]
										n_cnd = cnd[0][0]
								else:
									temp = td1 + t12
									if temp < t1:
										t1 = temp
										nxt = cnd[0][0]
										n_cnd = cnd[2][0]

							#tenemos el 1 y el 2
							if cnd[0][1] == 1 and cnd[1][1] == 1:
								if td1 < td3:
									temp = td1 + t31
									if temp < t1:
										t1 = temp
										nxt = cnd[0][0]
										n_cnd = cnd[1][0]
								else:
									temp = td3 + t31
									if temp < t1:
										t1 = temp
										nxt = cnd[2][0]
										n_cnd = cnd[0][0]

							#tenemos la llave del 3
							if cnd[2][1] == 1:
								temp = td1 + t12
								if temp < t1:
									t1 = temp
									nxt = cnd[0][0]
									n_cnd = cnd[2][0]

							#tenemos la llave del 2
							if cnd[1][1] == 1:
								temp = td1 + t31
								if temp < t1:
									t1 = temp
									nxt = cnd[0][0]
									n_cnd = cnd[2][0]		
								
							
					

				elif [cordc3[0],cordc3[1]] in lhs[cordc1]["connections"]:
					#Falta 1-2 y 2-3
					if cnd[0][1] == 1 and cnd[2][1]:
						t1 = td2
						nxt = cnd[1][0]
						#conectar el más lejano
						if t12 < t23:
							n_cnd = cnd[2][0]
						else:
							n_cnd = cnd[0][0]
					else:
						if cnd[0][1] != 1 and cnd[1][1] != 1 and cnd[2][1] != 1:
							if td1 < td3:
								t1 = td1 + t12 + t23
								nxt = cnd[0][0]
								n_cnd = -1
							else:
								t1 = td3 + t23 + t12
								nxt = cnd[2][0]
								n_cnd = -1
						else:
							#comprobar en order y comparando
							t1 = self.maxdist
							#si tenemos la llave dle 2
							if cnd[1][1] == 1:
								if t12 < t31:
									temp1 = td1 + t12 + t23
								else:
									temp1 = td1 + t31 + t23

								if t31 < t23:
									temp3 = td3 + t31 + t12
								else:	
									temp3 = td3 + t23 + t12

								if temp1 < temp3:
									t1 = temp1
									nxt = cnd[0][0]
									n_cnd = cnd[1][0]
								else:
									t1 = temp3
									nxt = cnd[2][0]
									n_cnd = cnd[1][0]

							#tenemos la llave dle 2 y del 3
							if cnd[1][1] == 1 and cnd[2][1] == 1:
								if td1 < td2:
									temp = td1 + t12
									if temp < t1:
										t1 = temp
										nxt = cnd[0][0]
										n_cnd = cnd[1][0]
								else:
									temp = td2 + t12
									if temp < t1:
										t1 = temp
										nxt = cnd[1][0]
										n_cnd = cnd[2][0]
							#tenemos la lalve del 1
							if cnd[0][1] == 1:
								temp = td2 + t23
								if temp < t1:
									t1 = temp
									nxt = cnd[1][0]
									n_cnd = [0][0]

							#tenemos la llave del 1 y del 2
							if cnd[0][1] == 1 and cnd[1][1] == 1:
								if td3 < td2:
									temp = td3 + t23
									if temp < t1:
										t1 = temp
										nxt = cnd[2][0]
										n_cnd = cnd[1][0]
								else:
									temp = td2 + t23
									if temp < t1:
										t1 = temp
										nxt = cnd[1][0]
										n_cnd = cnd[0][0]

							#tenemos la llave del 3
							if cnd[2][1] == 1:
								temp = td2 + t12
								if temp < t1:
									t1 = temp
									nxt = cnd[1][0]
									n_cnd = cnd[2][0]

				
				
				#check
				if to == -1:
					#comprobar si hay cruces
					if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
						continue
					self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
					to = 0
				else:
					if self.check_tri(t1,self.tri[tr][2],tr):
						#comprobar si hay cruces
						if self.check_croses(lhs,self.tri[tr][0][0],self.tri[tr][0][1]) or self.check_croses(lhs,self.tri[tr][0][1],self.tri[tr][0][2]) or self.check_croses(lhs,self.tri[tr][0][2],self.tri[tr][0][0]):
							continue
						self.o2 = [tr,self.tri[tr][2],t1,0,nxt,n_cnd]
		
		
    	
    	if self.o2[0] == -1:
    		#no seleccionado por cruces. al más cercano
    		self.o2[4] = f_d
    	self.o1 = self.o2
    	self.f_mind = f_d		

   

    def check_tri(self,t1,p1,nt):
    	if self.o2[0] == -1:
		#no tenemso niguno elegido
    		return True
    	else:
		if t1 < self.o2[2]:
			#menos turnos
			return True
		elif t1 == self.o2[2]:
			pa = (self.tri[self.o2[0]][1]*1.0)/(self.t_turn*1.0)
			pn = (self.tri[nt][1]*1.0)/(self.t_turn*1.0)
			ant = pow((1-pa),self.o2[2])
			new = pow((1-pn),t1)
	    		if ant < new:
				#mismos turnos más probable
		    		return True
			elif ant == new:
				if self.o2[1] <= p1:
					return False
				else:
					#mismos turnos igual de probable más puntos
					return True
			else:
				return False
		else:
			return False

if __name__ == "__main__":
    iface = interface.Interface(Wuibo)
    iface.run()
