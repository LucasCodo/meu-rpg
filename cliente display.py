import pygame
import sys
import _thread
import pyautogui
import json
from datetime import datetime, timedelta
from requests import Session
import os
requests = Session()
host_port = 'http://127.0.0.1:8000'
minimap_background = "cartographypack/Textures/parchmentFoldedCrinkled.png"
pedra = "kenney_rpgurbanpack/Tiles/tile_0036.png"
width, height= pyautogui.size()
width, height = 800,600
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
            dx = self.x-abs(target.x)
            dy = self.y-abs(target.y)
            self.x = round(self.width/2)+dx
            self.y = round(self.height/2)+dy
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

class player():
    def __init__(self,name="",x=0,y=0):
        self.name=name
        self._x=x
        self._y=y
        #self.player = pygame.image.load(os.path.join(minimap_background)).convert_alpha()
        #self.player = pygame.transform.scale(self.player, (80, 80))
        pass
    def draw(self,janela,cor=(255,0,0)):
        #player.convert()
        #janela.blit(self.player, (self.x,self.y))
        pygame.draw.circle(janela, cor, (self.x, self.y), 50,1)
        pass
    def update(self,message):
        if not message:
            return
        '''try:
            json_msg = json.loads(message[0].decode())
            dados = json_msg["data"]
            for dado in dados:
                name = dado["name"]
                if name == self.name:
                    self.x = 400+dado["x"]
                    self.y = 400+dado["y"]
        except json.decoder.JSONDecodeError:
            print("Não foi possivel carregar a mensagem!")
        except KeyError:
            print("Não tem um nome!")'''
        self._x = message["x"]
        self._y = message["y"]
        pass
    @property
    def x(self):
        return self._x+cam.x
    @property
    def y(self):
        return self._y+cam.y
    
class Jogo():
    def __init__(self,nick,width, height,fps):
        pygame.init()
        #pygame.font.init()
        self._height=height
        self._width=width
        self._janela = pygame.display.set_mode((self._width,self._height),0,32)
        self._relogio = pygame.time.Clock()
        self._fps=fps
        self._lista_players=[]
        self._lista_inimigos=[]
        self._lista_projeteis=[]
        self.me=player(nick,0,0)
        
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
        r = requests.post(host_port+'/conect',json={"nome":self.me.name}).json()
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
            #pygame.draw.circle(self._janela, (255,255,255), (150, 150), 50,1)
            #pygame.draw.rect(self._janela, (255,255,255), (150,150,150, 150), 5)
            #if event.type == pygame.KEYDOWN:
            '''if comandos[pygame.K_UP]:
                self.c.send_command('up')
            if comandos[pygame.K_DOWN]:
                self.c.send_command('down')
            if comandos[pygame.K_RIGHT]:
                self.c.send_command('right')
            if comandos[pygame.K_LEFT]:
                self.c.send_command('left')
            message = self.c.msgFromServer
            #self.me.draw(self._janela)
            for player in self._lista_players:
                player.draw(self._janela,(0,255,0))
            self.is_new_player(message)
            #self.me.update(message)'''
            #r = requests.get('http://127.0.0.1:8000/players').json()
            #print(r)
            #self._janela.blit(self.pedra, (400,400))
            self.draw_map()
            self.me.draw(self._janela)
            if comandos[pygame.K_UP]:
                r = requests.post(host_port+'/move',json={"nome":self.me.name, "comando": "up"}).json()
                self.me.update(r)
                if cam.travada:
                    cam.up()
            if comandos[pygame.K_DOWN]:
                r = requests.post(host_port+'/move',json={"nome":self.me.name, "comando": "down"}).json()
                self.me.update(r)
                if cam.travada:
                    cam.down()
            if comandos[pygame.K_RIGHT]:
                r= requests.post(host_port+'/move',json={"nome":self.me.name, "comando": "right"}).json()
                self.me.update(r)
                if cam.travada:
                    cam.right()
            if comandos[pygame.K_LEFT]:
                r = requests.post(host_port+'/move',json={"nome":self.me.name, "comando": "left"}).json()
                self.me.update(r)
                if cam.travada:
                    cam.left()
            if event.type == pygame.KEYDOWN:
                if comandos[pygame.K_y]:
                    if cam.travada:
                        cam.destravar()
                    else:
                        cam.travar()
            if comandos[pygame.K_SPACE]:
                self.construir(self.me.x,self.me.y)
            if comandos[pygame.K_c]:
                cam.center_player(self.me)
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
            ##
            for player in self._lista_players:
                player.draw(self._janela,(0,255,0))
            self.other_players()
            #self.me.update(message)
            self._janela.blit(self.contador_fps,(400,0))
            self._janela.blit(self.myfont.render(str(round(self.frame_time.microseconds/1000)), False, (255, 255, 255)),(500,0))

            
            pygame.display.update()
            self._relogio.tick(self._fps)
            self.frame_time = datetime.now()-self.pre_frame
        pygame.quit()
        sys.exit()
        
        pass
    def other_players(self):
        r = requests.get(host_port+'/players').json()
        for a in r["players"]:
            #print(a)
            if a["name"] != self.me.name and a["name"] not in list(map(lambda x : x.name,self._lista_players)):
                self._lista_players.append(player(a["name"],a["x"],a["y"]))
            else:
                for p in self._lista_players:
                    if a["name"] == p.name:
                        p.update(a)
    def draw_map(self):
        i = datetime.now()
        r = requests.get(host_port+'/mapa', params = {"x":-cam.x+cam.center[0],"y":-cam.y+cam.center[1],"d":400}).json()
        f = datetime.now() - i
        #print(r)
        terrenos = r["mapa"]["terrenos"]
        #print(f.microseconds, len(terrenos))
        for t in terrenos:
            self._janela.blit(self.pedra, (cam.x+t["x"],cam.y+t["y"]))
        self.draw_mini_map(terrenos)
        pass
    def draw_mini_map(self,terrenos):
        
        self.overlay_minimap.fill((0,0,0,160))
        
        
        #self.minimap.draw(self._janela)
        for t in terrenos:
            x = self.minimap.x+round(t["x"]/8)+round(cam.x/8)
            y = self.minimap.y+round(t["y"]/8)+round(cam.y/8)
            #if x >= self.minimap.x-5 and y >= self.minimap.y-5:
            pygame.draw.rect(self.overlay_minimap, (0,0,0), (x,y,10,10))
        pygame.draw.rect(self.overlay_minimap,(255,255,255,0),[0,0,self._width-self.minimap.width,self._height])
        pygame.draw.rect(self.overlay_minimap,(255,255,255,0),[0,0,self._width,self._height-self.minimap.height])
        self.overlay_minimap.set_colorkey((255,255,255))
        self._janela.blit(self.overlay_minimap,(0,0))
        pass
    def construir(self, x, y):
        r = requests.post(host_port+'/construir/terreno',json = {"x": x-cam.x, "y": y-cam.y , "tipo": "pedra"}).json()
        return
        

if __name__=="__main__":
    #print(width, height)
    jogo = Jogo("Lucas"+str(datetime.now()),width, height,60)
    jogo.run()
    '''se = requests.Session()
    try:
        while True:
            r = se.get('http://127.0.0.1:8000/')
            #print(r.json())
    except:
        print("DEU RUIM!!!")'''
