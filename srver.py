#!/usr/bin/env python3
import math
import socket
import time
import pygame
import json
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
x=0
y=0
done=False
bulletlist=[]
ebulletlist=[]
cooldown=1
lasttime=time.time()
health=5
ex=0
ey=0
def readData(opponent):
    global ebulletlist
    global ex
    global ey
    ox=int(opponent[:opponent.find(",")])
    oy=int(opponent[(opponent.find(",")+1):(opponent.find("-"))])
    ebulletlist=[]
    ebl=opponent[(opponent.find("-")+1):]
    ebl=json.loads(ebl)
    for i in range(len(ebl)):
       ebl[i]=tuple(ebl[i])
       ebulletlist.append(ebl[i])
    ex=ox
    ey=oy
    return (ox,oy)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    conn = 0
    if isServer:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
    else:
        s.connect((HOST,PORT))
        conn = s
    print(PORT,conn)
    while not done:
        hasShot=0
        currenttime=time.time()
        cooldown-=(currenttime-lasttime)
        lasttime=currenttime
        
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done=True
            if event.type==pygame.MOUSEBUTTONDOWN and cooldown < 0 and hasShot==0:
                mp=pygame.mouse.get_pos()
                xd=mp[0]-x
                yd=mp[1]-y
                dist=math.sqrt((xd*xd)+(yd*yd))
                bs=4
                vy = yd/dist*bs
                vx = xd/dist*bs
                
                bulletlist.append((x,y,vx,vy))
                cooldown=1
                hasShot=1
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
        if health<=0:
            done=True
        pressed=pygame.key.get_pressed()
        
        if pressed[pygame.K_UP] and y>0:
            y-=3
        if pressed[pygame.K_DOWN] and y<560:
            y+=3
        if pressed[pygame.K_LEFT] and x>0:
            x-=3
        if pressed[pygame.K_RIGHT] and x<760:
            x+=3
        pygame.draw.rect(screen,(0,255,0),pygame.Rect(x,y,40,40))

        if isServer:
            data = ''
            data = conn.recv(2048)
            opponent=data.decode('utf-8')
            epos=readData(opponent)
            
            pygame.draw.rect(screen,(0,0,255),pygame.Rect(epos[0],epos[1],40,40))
            conn.sendall(bytes(str(x)+","+str(y)+"-"+json.dumps(bulletlist),'utf-8'))
        if not isServer:
            bls = ''
            conn.sendall(bytes(str(x)+","+str(y)+"-"+json.dumps(bulletlist),'utf-8'))
            data = ''
            data = conn.recv(2048)
            opponent=data.decode('utf-8')
            epos=readData(opponent)
            pygame.draw.rect(screen,(0,0,255),pygame.Rect(epos[0],epos[1],40,40))

        pygame.display.flip()
