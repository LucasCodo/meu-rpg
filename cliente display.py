import pygame
import sys
import pyautogui
import json
from datetime import datetime, timedelta
from requests import Session
import os
import math
import time
import _thread
from pygame import font
from pygame import display
from pygame.image import load
from pygame.transform import scale
from pygame.sprite import Sprite , Group, GroupSingle, groupcollide
from pygame import event
from pygame.locals import QUIT, KEYUP, K_SPACE
from pygame.time import Clock

pygame.init()
requests = Session()
host_port = 'http://127.0.0.1:8000'
minimap_background = "cartographypack/Textures/parchmentFoldedCrinkled.png"
pedra = "kenney_rpgurbanpack/Tiles/tile_0036.png"
width, height= pyautogui.size()
#width, height = 800,600
speed_cam = 2
class Camera():
    def __init__(self,width, height):
        self.width, self.height = width, height
        self.x = round(self.width/2)
        self.y = round(self.height/2)
        self.travada = True
        self.center = [round(self.width/2),round(self.height/2)]
    def up(self):
        self.y+=2
    def down(self):
        self.y-=2
    def right(self):
        self.x-=2
    def left(self):
        self.x+=2
    def travar(self):
        self.travada = True
    def destravar(self):
        self.travada = False
    def center_player(self,target):
        if not self.travada:
            '''print(target.rect[2:])
            print(self.x,self.y)'''
            dx = self.x-target.rect.centerx
            dy = self.y-target.rect.centery
            self.x = round(self.width/2)+dx
            self.y = round(self.height/2)+dy
            '''self.x = round(self.width/2)-target.rect.center[0]
            self.y = round(self.height/2)-target.rect.center[1]'''
class Minimap():
    def __init__(self,cam,width,height):
        self.width = width
        self.height = height
        self.x = cam.width - self.width
        self.y = cam.height - self.height
        self.map = pygame.image.load(os.path.join(minimap_background)).convert_alpha()
        self.map = pygame.transform.scale(self.map, (self.width, self.height))
        pass
    def draw(self,janela):
        janela.blit(self.map, (self.x,self.y))
    def update(self):
        pass

cam = Camera(width, height)
nick = "Lucas"+str(datetime.now())
class sprite_player(Sprite):
    def __init__(self,x,y):
        super().__init__()
        
        self.image = scale(load("cartographypack/Textures/parchmentFoldedCrinkled.png"),(80,80))
        self._rect = self.image.get_rect(center=(x,y))
        self.velocidade = 2
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            message = requests.post(host_port+'/move',json={"nome":nick, "comando": "left"}).json()
            self.setpos(message)
            if cam.travada:
                cam.left()
        if keys[pygame.K_RIGHT]:
            message = requests.post(host_port+'/move',json={"nome":nick, "comando": "right"}).json()
            self.setpos(message)
            if cam.travada:
                cam.right()
        if keys[pygame.K_UP]:
            message = requests.post(host_port+'/move',json={"nome":nick, "comando": "up"}).json()
            self.setpos(message)
            if cam.travada:
                cam.up()
        if keys[pygame.K_DOWN]:
            message = requests.post(host_port+'/move',json={"nome":nick, "comando": "down"}).json()
            self.setpos(message)
            if cam.travada:
                cam.down()
    def setpos(self,message):
        self._rect = self.image.get_rect(center=(message["x"],message["y"]))
    @property
    def rect(self):
        rect = self.image.get_rect(center=(self._rect.centerx+cam.x,self._rect.centery+cam.y))
        return rect
class sprite_other_player(Sprite):
    def __init__(self,name,x,y):
        super().__init__()
        self.name = name
        self.image = scale(load("cartographypack/Textures/parchmentFoldedCrinkled.png"),(80,80))
        self._rect = self.image.get_rect(center=(x,y))
        self.velocidade = 2
    def update(self):
        if self.name not in list_name_players:
            self.kill()
        else:
            for a in players["players"]:
                if a["name"] == self.name:
                    self.setpos(a)
            
    def setpos(self,message):
        self._rect = self.image.get_rect(center=(message["x"],message["y"]))
    @property
    def rect(self):
        self._rect = self.image.get_rect(center=(self._rect.centerx+cam.x,self._rect.centery+cam.y))
        return self._rect

d = round(math.dist([0,0],[width, height])/2)
mapa = requests.get(host_port+'/mapa', params = {"x":-cam.x+cam.center[0],"y":-cam.y+cam.center[1],"d":d}).json()
me = sprite_player(cam.x,cam.y)
grupo_me = GroupSingle(me)
grupo_players = Group()
raio = d
players = requests.get(host_port+'/players', params = {"nome":nick,"x":-cam.x+cam.center[0],"y":-cam.y+cam.center[1], "r":raio}).json()
list_name_players = list(map(lambda x : x["name"],players["players"]))
def update_mapa():
    global mapa
    while True:
        #print("MAis um segundo")
        mapa = requests.get(host_port+'/mapa', params = {"x":-cam.x+cam.center[0],"y":-cam.y+cam.center[1],"d":d}).json()
        time.sleep(1)
class Jogo():
    def __init__(self,nick,width, height,fps):
        
        #pygame.font.init()
        self._height=height
        self._width=width
        self._janela = pygame.display.set_mode((self._width,self._height),0,32)
        self._relogio = pygame.time.Clock()
        self._fps=fps
        self._lista_players=[]
        self._lista_inimigos=[]
        self._lista_projeteis=[]
        #self.me=player(nick,0,0)
        
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.last_secund = datetime.now()
        self.cont_fps=0
        self.contador_fps = self.myfont.render(str(self.cont_fps), False, (255, 255, 255))
        self.frame_time = datetime.now()-datetime.now()
        self.pre_frame = datetime.now()
        self.pedra = pygame.image.load(os.path.join(pedra)).convert_alpha()
        self.pedra = pygame.transform.scale(self.pedra, (80, 80))
        self.minimap = Minimap(cam,round(width/8),round(width/8))
        #pygame.display.flip()
        self.overlay_minimap = pygame.Surface((self._width,self._height), pygame.SRCALPHA)
        pass
    def run(self):
        r = requests.post(host_port+'/conect',json={"nome":nick}).json()
        print(r)
        while True:
            self.pre_frame = datetime.now()
            event = pygame.event.poll()
            comandos = pygame.key.get_pressed()
            button = pygame.mouse.get_pressed()
            if event.type == pygame.QUIT or comandos[pygame.K_LALT] and comandos[pygame.K_F4]:
                break
            if self.last_secund+timedelta(seconds=1)<datetime.now():
                #print("mais um segundo")
                self.last_secund = datetime.now()
                self.contador_fps = self.myfont.render(str(self.cont_fps), False, (255, 255, 255))
                self.cont_fps=0
            self.cont_fps+=1
            
            self._janela.fill((200,200,200))

            self.draw_map()
            if event.type == pygame.KEYDOWN:
                if comandos[pygame.K_y]:
                    if cam.travada:
                        cam.destravar()
                    else:
                        cam.travar()
            if comandos[pygame.K_SPACE]:
                self.construir(me.rect.x,me.rect.y)
            if comandos[pygame.K_c]:
                cam.center_player(me)
            ##
            if not cam.travada:
                if comandos[pygame.K_w]:
                    cam.up()
                if comandos[pygame.K_s]:
                    cam.down()
                if comandos[pygame.K_d]:
                    cam.right()
                if comandos[pygame.K_a]:
                    cam.left()

            self.other_players()
            self._janela.blit(self.contador_fps,(400,0))
            self._janela.blit(self.myfont.render(str(round(self.frame_time.microseconds/1000)), False, (255, 255, 255)),(500,0))
            grupo_players.draw(self._janela)
            grupo_players.update()
            grupo_me.draw(self._janela)
            grupo_me.update()
            pygame.display.update()
            self.frame_time = datetime.now()-self.pre_frame
            self._relogio.tick(self._fps)
            
        pygame.quit()
        sys.exit()
        
        pass
    def other_players(self):
        players = requests.get(host_port+'/players', params = {"nome":nick,"x":-cam.x+cam.center[0],"y":-cam.y+cam.center[1], "r":raio}).json()
        list_name_players = list(map(lambda x : x["name"],players["players"]))
        list_group_players_name = list(map(lambda x : x.name,grupo_players))
        for a in players["players"]:
            #print(a)
            if a["name"] == nick:
                me.setpos(a)
            elif a["name"] not in list_group_players_name:
                #self._lista_players.append(player(a["name"],a["x"],a["y"]))
                grupo_players.add(sprite_other_player(a["name"],a["x"],a["y"]))
                
                
    def draw_map(self):
        #i = datetime.now()
        #d = round(math.dist([0,0],[width, height])/2)
        #r = requests.get(host_port+'/mapa', params = {"x":-cam.x+cam.center[0],"y":-cam.y+cam.center[1],"d":d}).json()
        
        terrenos = mapa["mapa"]["terrenos"]
        redut = 8
        for t in terrenos:
            self._janela.blit(self.pedra, (cam.x+t["x"],cam.y+t["y"]))
        
        self.draw_mini_map(terrenos)
        #f = datetime.now() - i
        #print(f.microseconds, len(terrenos))
        pass
    def draw_mini_map(self,terrenos):
        
        self.overlay_minimap.fill((0,0,0,160))
        redut = 8
        
        for t in terrenos:
            x = self.minimap.x+round(t["x"]/redut)+round(cam.x/redut)
            y = self.minimap.y+round(t["y"]/redut)+round(cam.y/redut)
            pygame.draw.rect(self.overlay_minimap, (0,0,255), (x,y,10,10))
        for p in grupo_players:
            x = self.minimap.x+round(p._rect.centerx/redut)+round(cam.x/8)
            y = self.minimap.y+round(p._rect.centery/redut)+round(cam.y/8)
            pygame.draw.rect(self.overlay_minimap, (0,255,0), (x,y,2,2))
        x = self.minimap.x+round(me._rect.centerx/redut)+round(cam.x/8)
        y = self.minimap.y+round(me._rect.centery/redut)+round(cam.y/8)
        pygame.draw.rect(self.overlay_minimap, (255,0,0), (x,y,2,2))
        pygame.draw.rect(self.overlay_minimap,(255,255,255,0),[0,0,self._width-self.minimap.width,self._height])
        pygame.draw.rect(self.overlay_minimap,(255,255,255,0),[0,0,self._width,self._height-self.minimap.height])
        self.overlay_minimap.set_colorkey((255,255,255))
        self._janela.blit(self.overlay_minimap,(0,0))
        pass
    def construir(self, x, y):
        r = requests.post(host_port+'/construir/terreno',json = {"x": x-cam.x, "y": y-cam.y , "tipo": "pedra"}).json()
        return
        

if __name__=="__main__":
    _thread.start_new_thread(update_mapa,())
    jogo = Jogo(nick,width, height,120)
    jogo.run()
    _thread.exit()
