#!/usr/bin/env python3
import math
import socket
import pygame
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
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                done=True
            if event.type==pygame.MOUSEBUTTONDOWN:
                
                bulletlist.append((x,y,1,1))
        for i in range(len(bulletlist)):
            pygame.draw.rect(screen,(255,255,255),pygame.Rect(bulletlist[i][0],bulletlist[i][1],10,10))
            bulletlist[i]=(bulletlist[i][0]+bulletlist[i][2],bulletlist[i][1]+bulletlist[i][3],1,1)
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
            print(opponent)
            ox=int(opponent[:opponent.find(",")])
            oy=int(opponent[(opponent.find(",")+1):(opponent.find("-"))])
            pygame.draw.rect(screen,(0,0,255),pygame.Rect(ox,oy,40,40))
            conn.sendall(bytes(str(x)+","+str(y)+"-"+str(bulletlist),'utf-8'))
            print(opponent)
        if not isServer:
            conn.sendall(bytes(str(x)+","+str(y)+"-"+str(bulletlist),'utf-8'))
            data = ''
            data = conn.recv(1024)
            opponent=data.decode('utf-8')
            ox=int(opponent[:opponent.find(",")])
            oy=int(opponent[(opponent.find(",")+1):(opponent.find("-"))])
            pygame.draw.rect(screen,(0,0,255),pygame.Rect(ox,oy,40,40))
            print(opponent)
        pygame.display.flip()
