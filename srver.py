

#imports
import math
import socket
import time
import pygame
import json
import random
import _thread
import pdb
#Defining images
grass_image=pygame.image.load("grass.png")
greenTank_image=pygame.image.load("tankGreen_outline.png")
redTank_image=pygame.image.load("tankRed_outline.png")
bullet_image=pygame.image.load("bullet.png")
pygame.init()
isServer = False
#ports
if isServer:
	HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
else:
	HOST = '192.168.0.15'  # Standard loopback interface address (localhost)
PORT = 65432			   # Port to listen on (non-privileged ports are > 1023)
sx=800
sy=600
screen=pygame.display.set_mode((sx,sy))
#positions
if isServer:
	x=0
	y=0
else:
	x=760
	y=560
#variables
done=False
playerSpeed=25
ammo=10
pygame.font.init()
myfont=pygame.font.SysFont('Times New Roman',24)
bulletlist=[]
ebulletlist=[]
cooldown=1
lasttime=time.time()
health=5
acpu = []
ex=0
bs=10
ey=0
nb = []
#functions
def networkSystem():
	global ebulletlist
	global ex
	global ey
	global acpu
	global conn
	global done
	while True:
		if isServer:
			data = ''
			data = conn.recv(4)
			bytesnext=data.decode('utf-8')
			# print('getting length', bytesnext)
			if '.' in bytesnext:
				bytesnext=int(bytesnext[:bytesnext.index('.')])
			else:
				bytesnext = int(bytesnext)
			ox, oy = readData(bytesnext)
			ex=ox
			ey=oy
			epos = (ex, ey)

			sendData()

		if not isServer:
			sendData()
			data = conn.recv(4)
			bytesnext=data.decode('utf-8')
			# print('recieved:' + bytesnext)
			if '.' in bytesnext:
				bytesnext=int(bytesnext[:bytesnext.index('.')])
			else:
				bytesnext = int(bytesnext)
			ox, oy = readData(bytesnext)
			ex=ox
			ey=oy
			epos = (ex, ey)

def readData(bytes):
	global acpu
	data = conn.recv(int(bytes))
	opponent=data.decode('utf-8')
	if not opponent=="death":
		# print(opponent)
		ox=int(opponent[:opponent.find(",")])
		oy=int(opponent[(opponent.find(",")+1):(opponent.find("?"))])
		ebl=opponent[(opponent.find("?")+1):(opponent.find("|"))]
		eacpu=opponent[(opponent.find("|")) + 1:]
		if not isServer:
			acpu = eval(eacpu)
		ebl=json.loads(ebl)
		for i in range(len(ebl)):
		   ebl[i]=tuple(ebl[i])
		   ebulletlist.append(ebl[i])
	return (ox,oy)
def sendData():
	global nb
	if not done:
		thatstuff=bytes(str(int(x))+","+str(int(y))+"?"+json.dumps(nb)+'|'+json.dumps(acpu),'utf-8')
	else:
		thatstuff="death"
	lenString = str(len(thatstuff))
	for i in range(4-len(lenString)):
		lenString+="."
	conn.sendall(bytes(lenString, 'utf-8'))
	conn.sendall(thatstuff)
	# print("hi",thatstuff,"we need a run button in Atom ")
	nb = []
#socket connectionsa
print('initializing socket')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	print('Step 1 complete')
	conn = 0
	if isServer:
		s.bind((HOST, PORT))
		s.listen()
		conn, addr = s.accept()
	else:
		s.connect((HOST,PORT))
		conn = s
	print(PORT,conn)
	print('Finished initializing socket')
	_thread.start_new_thread(networkSystem, ())

	while True:
		if not done:
			  #rediefining variables

			hasShot=0
			currenttime=time.time()
			timePassed=(currenttime-lasttime)
			cooldown-=timePassed
			lasttime=currenttime

			screen.blit(grass_image,(0,0))

			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					done=True
				if event.type==pygame.MOUSEBUTTONDOWN and cooldown < 0 and hasShot==0 and ammo>0:
					mp=pygame.mouse.get_pos()
					xd=mp[0]-x
					yd=mp[1]-y
					ammo-=1
					dist=math.sqrt((xd*xd)+(yd*yd))
					bs=(100*timePassed)
					vy = yd/dist*bs
					vx = xd/dist*bs
					print('adding a bullet')
					bulletlist.append((x,y,vx,vy))
					nb.append((x,y,vx,vy))
					cooldown=0.5
					hasShot=1

			if isServer:
				if len(acpu) < 2:
					acpu.append((random.randint(0,800), random.randint(0,600), random.randint(0,5)))
			btr=[]
			nmerect=pygame.Rect(ex,ey,40,40)
			for i in range(len(bulletlist)):
				b = bulletlist[i]
				screen.blit(bullet_image,(b[0],b[1]))
				bulletlist[i]=(b[0]+b[2],b[1]+b[3],b[2],b[3])
				b = bulletlist[i]
				if b[0]>sx or b[0]<0 or b[1]>sy or b[1]<0:
					btr.append(b)
				bulletrect=pygame.Rect(b[0],b[1],10,10)
				if nmerect.colliderect(bulletrect):
					btr.append(bulletlist[i])
			for i in range(len(btr)):
				bulletlist.remove(btr[i])
			usrect=pygame.Rect(x,y,40,40)
			ebtr=[]
			for i in range(len(ebulletlist)):
				screen.blit(bullet_image,(ebulletlist[i][0],ebulletlist[i][1]))

				ebulletlist[i]=(ebulletlist[i][0]+ebulletlist[i][2],ebulletlist[i][1]+ebulletlist[i][3],ebulletlist[i][2],ebulletlist[i][3])
				bulletrect=pygame.Rect(ebulletlist[i][0],ebulletlist[i][1],10,10)
				if usrect.colliderect(bulletrect):
					health-=1
					ebtr.append(i)
			print(ebtr)
			for i in range(len(ebtr)):
				ebulletlist.pop(ebtr[i])
			if health<=0:
				done=True
			print(len(acpu))
			for i in range(len(acpu)):
				rect = pygame.Rect(acpu[i][0],acpu[i][1],10,10)
				pygame.draw.rect(screen,(0,255,0),rect)

				if usrect.colliderect(rect):
					ammo += acpu[i][2]
			oprect=pygame.Rect(ex,ey,40,40)
			acpu=[x for x in acpu if not usrect.colliderect(pygame.Rect(x[0],x[1],10,10))]
			acpu=[x for x in acpu if not oprect.colliderect(pygame.Rect(x[0],x[1],10,10))]
			pressed=pygame.key.get_pressed()
			angle=0
			if pressed[pygame.K_UP] and y>0:
				y-=playerSpeed*timePassed
				angle=180
			if pressed[pygame.K_DOWN] and y<560:
				y+=playerSpeed*timePassed
			if pressed[pygame.K_LEFT] and x>0:
				x-=playerSpeed*timePassed
				angle=-90
			if pressed[pygame.K_RIGHT] and x<760:
				x+=playerSpeed*timePassed
				angle=90

			# networkSystem()

			screen.blit(redTank_image,(ex,ey))

			greenTank_rotated=pygame.transform.rotate(greenTank_image, angle)
			screen.blit(greenTank_rotated,(x,y))

			textsurface=myfont.render('Health: '+str(health),False,(255,255,255))
			screen.blit(textsurface,(5,5))
			textsurface=myfont.render('Ammo!!: '+str(ammo),False,(255,255,255))
			screen.blit(textsurface,(5,25))
			pygame.display.flip()

		if done:
			pressed=pygame.key.get_pressed()
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					done=True
			if pressed[pygame.K_SPACE]:

				done=False
				health=5
				bulletlist=[]
				ebulletlist=[]
				if isServer:
					x=0

					y=0
				else:
					x=760
					y=560
