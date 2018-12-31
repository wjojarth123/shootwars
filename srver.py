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
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
screen=pygame.display.set_mode((800,600))
x=0
y=0
done=False
bulletlist=[]
ebulletlist=[]
cooldown=1
lasttime=time.time()
def readData(opponent):
    global bulletlist
    ox=int(opponent[:opponent.find(",")])
    oy=int(opponent[(opponent.find(",")+1):(opponent.find("-"))])
    ebulletlist=[]
    ebl=opponent[(opponent.find("-")+1):]
    ebl=json.loads(ebl)
    for i in range(len(ebl)):
       ebl[i]=tuple(ebl[i])
       ebulletlist.append(ebl[i])
    print(ebl)
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
        print(cooldown)
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done=True
            if event.type==pygame.MOUSEBUTTONDOWN and cooldown < 0 and hasShot==0: 
                bulletlist.append((x,y,1,1))
                print("why doesn't bla bla work. this time non")
                cooldown=1
                hasShot=1
        for i in range(len(bulletlist)):
            pygame.draw.rect(screen,(255,255,255),pygame.Rect(bulletlist[i][0],bulletlist[i][1],10,10))
            bulletlist[i]=(bulletlist[i][0]+bulletlist[i][2],bulletlist[i][1]+bulletlist[i][3],1,1)
        for i in range(len(ebulletlist)):
            pygame.draw.rect(screen,(255,255,255),pygame.Rect(ebulletlist[i][0],ebulletlist[i][1],10,10))
            ebulletlist[i]=(ebulletlist[i][0]+ebulletlist[i][2],ebulletlist[i][1]+ebulletlist[i][3],1,1)
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
            data = conn.recv(1024)
            opponent=data.decode('utf-8')
            epos=readData(opponent)
            
            pygame.draw.rect(screen,(0,0,255),pygame.Rect(epos[0],epos[1],40,40))
            conn.sendall(bytes(str(x)+","+str(y)+"-"+json.dumps(bulletlist),'utf-8'))
        if not isServer:
            bls = ''
            conn.sendall(bytes(str(x)+","+str(y)+"-"+json.dumps(bulletlist),'utf-8'))
            data = ''
            data = conn.recv(1024)
            opponent=data.decode('utf-8')
            epos=readData(opponent)
            pygame.draw.rect(screen,(0,0,255),pygame.Rect(epos[0],epos[1],40,40))
            cd-=1
        pygame.display.flip()
