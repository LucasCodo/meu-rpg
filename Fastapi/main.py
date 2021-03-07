from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import copy
import math
import numpy as np
from collections import namedtuple

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Rota Raiz
@app.get("/")
def raiz():
    return {"Ola": "Mundo"}

# Criar model
'''class Usuario(BaseModel):
    id: int
    email: str
    senha: str'''
class Cli(BaseModel):
    nome:str

class Comando(BaseModel):
    nome:str
    comando:str
class Terreno(BaseModel):
    tipo:str
    x:int
    y:int
    def add(self):
        self.x+=1
class terreno():
    def __init__(self,tipo,x,y):
        self.tipo:str=tipo
        self.x:int=x
        self.y:int=y
    def add(self):
        self.x+=1

# Criar base de dados
'''
base_de_dados = [
    Usuario(id=1, email="roger@roger.com.br", senha="roger123"),
    Usuario(id=2, email="teste@teste.com.br", senha="teste123")
]

# Rota Get All
@app.get("/usuarios")
def get_todos_os_usuarios():
    return base_de_dados

# Rota Get Id
@app.get("/usuarios/{id_usuario}")
def get_usuario_usando_id(id_usuario: int):
    for usuario in base_de_dados:
        if(usuario.id == id_usuario):
            return usuario
    
    return {"Status": 404, "Mensagem": "Não encontrou usuario"}
'''
# Rota Insere
'''@app.post("/usuarios")
def insere_usuario(usuario: Usuario):
    # criar regras de negocio
    base_de_dados.append(usuario)
    return usuario'''
class Mapa():
    def __init__(self):
        self.terrenos=[]
        self.criaturas=[]
        self.items=[]
        self.construcoes=[]
    def add_terreno(self,terreno:Terreno):
        self.terrenos.append(terreno)
        if terreno not in self.terrenos:
            self.terrenos.append(terreno)
            return {"status": 200, "message":"Item adicionado com sucesso"}
        return {"status": 404, "message":"Item já existente"}
    def delet_terreno(self,terreno:Terreno):
        if terreno in self.terrenos:
            self.terrenos.remove(terreno)
            return {"status": 200, "message":"Item removido com sucesso"}
        return {"status": 404, "message":"Item não encontrado"}
class Game_status():
    def __init__(self):
        self.mapa=[]
        self.criaturas=[]
        self.players = []

class player():
    teste="teste1"
    def __init__(self,name):
        self.name=name
        self.x=0
        self.y=0
        pass
    def up(self):
        self.y-=2
        pass
    def down(self):
        self.y+=2
        pass
    def rigth(self):
        self.x+=2
    def left(self):
        self.x-=2
    def recv(self,json_msg):
        try:
            comando = json_msg["cliente"].get("command","")
            if comando == "up":
                self.up()
            if comando == "down":
                self.down()
            if comando == "right":
                self.rigth()
            if comando == "left":
                self.left()
        except KeyError as e:
            print("command Error:",e)
            pass

clientes = {}
_mapa = Mapa()
#for a in range(10000000001):
#    _mapa.add_terreno({"tipo":"pedra","x":np.random.randint(0,1000000000),"y":np.random.randint(0,1000000000)})
#terreno = namedtuple('Terreno',['tipo','x','y'])

m = copy.deepcopy(_mapa)
list(map(lambda x : _mapa.add_terreno(terreno("pedra",np.random.randint(0,10000),np.random.randint(0,10000))),range(10001)))
@app.post("/move")
def move_player(comando:Comando):
    if comando.comando == "up":
        clientes[comando.nome].up()
    if comando.comando == "down":
        clientes[comando.nome].down()
    if comando.comando == "right":
        clientes[comando.nome].rigth()
    if comando.comando == "left":
        clientes[comando.nome].left()
    return clientes[comando.nome]
@app.post("/conect")
def conect_player(c:Cli):
    p = player(c.nome)
    clientes[c.nome]= p
    return clientes[c.nome]
@app.get("/players")
def players():
    return {"players":list(map(lambda x : x,clientes.values()))}#{"players":list(map(lambda x : x.json(),clientes.values()))}
@app.get("/mapa")
def mapa(x:int,y:int,d:int):
    m.terrenos = list(filter(lambda t: t if math.dist((x,y),(t.x,t.y))<d else "",_mapa.terrenos))
    #print(m.terrenos)
    return {"mapa":m}
@app.post("/construir/terreno")
def construir_terreno(terreno:Terreno):
    return _mapa.add_terreno(terreno)
@app.post("/destruir/terreno")
def destruir_terreno(terreno:Terreno):
    return _mapa.delet_terreno(terreno)
