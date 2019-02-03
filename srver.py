

 #!/usr/bin/env python3
import math
import socket
import time
import pygame
import json
import random

pygame.init()
isServer = True
if isServer:
    HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
else:
    HOST = '192.168.0.20'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privied ports are > 1023)
sx=800
sy=600
screen=pygame.display.set_mode((sx,sy))
if isServer:
    x=0
    y=0
else:
    x=760
    y=560
done=False
playerSpeed=25
ammo=10
pygame.font.init()
myfont=pygame.font.SysFont('Comic Sans MS',24)
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

def readData(opponent):
    global done
    if opponent=="death":
        done=True
        return
    global ebulletlist
    global ex
    global ey
    global acpu
    print(opponent)
    ox=int(opponent[:opponent.find(",")])
    oy=int(opponent[(opponent.find(",")+1):(opponent.find("?"))])
    ebl=opponent[(opponent.find("?")+1):(opponent.find("|"))]
    eacpu=opponent[(opponent.find("|")) + 1:]
    if not isServer:
        acpu = eacpu
    ebl=json.loads(ebl)
    for i in range(len(ebl)):
       ebl[i]=tuple(ebl[i])
       ebulletlist.append(ebl[i])
    ex=ox
    ey=oy
    print(len(ebulletlist))
    return (ox,oy)

def sendData():
    thatstuff=bytes(str(int(x))+","+str(int(y))+"?"+json.dumps(nb)+'|'+json.dumps(acpu),'utf-8')
    lenString = str(len(thatstuff))
    for i in range(4-len(lenString)):
        lenString+="."
    conn.sendall(bytes(lenString, 'utf-8'))
    conn.sendall(thatstuff)
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
    while True:
        if not done:
            nb = []
            hasShot=0
            currenttime=time.time()
            timePassed=(currenttime-lasttime)
            cooldown-=timePassed
            lasttime=currenttime

            screen.fill((0,0,0))
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
                pygame.draw.rect(screen,(255,255,255),pygame.Rect(b[0],b[1],10,10))
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
                pygame.draw.rect(screen,(255,255,255),pygame.Rect(ebulletlist[i][0],ebulletlist[i][1],10,10))
                ebulletlist[i]=(ebulletlist[i][0]+ebulletlist[i][2],ebulletlist[i][1]+ebulletlist[i][3],ebulletlist[i][2],ebulletlist[i][3])
                bulletrect=pygame.Rect(ebulletlist[i][0],ebulletlist[i][1],10,10)
                if usrect.colliderect(bulletrect):
                    health-=1
                    ebtr.append(i)
            for i in range(len(ebtr)):
                bulletlist.pop(ebtr[i])
            if health<=0:
                done=True

            for i in range(len(acpu)):
                rect = pygame.Rect(acpu[i][0],acpu[i][1],10,10)
                pygame.draw.rect(screen,(0,255,0),rect)
                if usrect.colliderect(bulletrect):
                    ammo += acpu[i][2]
            pressed=pygame.key.get_pressed()

            if pressed[pygame.K_UP] and y>0:
                y-=playerSpeed*timePassed
            if pressed[pygame.K_DOWN] and y<560:
                y+=playerSpeed*timePassed
            if pressed[pygame.K_LEFT] and x>0:
                x-=playerSpeed*timePassed
            if pressed[pygame.K_RIGHT] and x<760:
                x+=playerSpeed*timePassed
            pygame.draw.rect(screen,(0,255,0),pygame.Rect(x,y,40,40))

            if isServer:
                data = ''
                data = conn.recv(4)
                bytesnext=data.decode('utf-8')
                print(bytesnext)
                if '.' in bytesnext:
                    bytesnext=int(bytesnext[:bytesnext.index('.')])
                else:
                    bytesnext = int(bytesnext)
                data = conn.recv(int(bytesnext))
                opponent=data.decode('utf-8')
                epos=readData(opponent)
                if not opponent=="death":
                    pygame.draw.rect(screen,(0,0,255),pygame.Rect(epos[0],epos[1],40,40))
                sendData()

            if not isServer:
                sendData()
                data = conn.recv(4)
                bytesnext=data.decode('utf-8')
                print('recieved:' + bytesnext)
                if '.' in bytesnext:
                    bytesnext=int(bytesnext[:bytesnext.index('.')])
                else:
                    bytesnext = int(bytesnext)
                data = conn.recv(bytesnext)
                opponent=data.decode('utf-8')

                epos=readData(opponent)
                if not opponent=="death":
                    pygame.draw.rect(screen,(0,0,255),pygame.Rect(epos[0],epos[1],40,40))
            textsurface=myfont.render('Health: '+str(health),False,(255,255,255))
            screen.blit(textsurface,(5,5))
            textsurface=myfont.render('Ammo!!: '+str(ammo),False,(255,255,255))
            screen.blit(textsurface,(5,25))
            pygame.display.flip()

        if done:
            pressed=pygame.key.get_pressed()

            if isServer:
                data = conn.recv(1024)
                opponent=data.decode('utf-8')
                epos=readData(opponent)

                conn.sendall(bytes("5...death",'utf-8'))
            else:
                conn.sendall(bytes("5...death",'utf-8'))
                data = conn.recv(1024)
                opponent=data.decode('utf-8')
                epos=readData(opponent)
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
        print("great")
