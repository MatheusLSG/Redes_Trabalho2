
import socket 
from  _thread import * 
import pickle
from encouracados import Encouracados
from globals import *

server = "192.168.15.4"
porta = 5555 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, porta))
except socket.error as e:
    str(e)
    
s.listen()
print("Esperando conexões, Server disponivel")


connected = set()
games:dict[int,Encouracados] = {}
idCount = 0                
idList = list(i for i in range(PLAYERS_QTD))

def threaded_client(conn: socket.socket, addr, p: int, gameId):
    global idCount
    conn.send(str.encode(str(p)))
    
    resp = ""
    while True:
        try:
            data = conn.recv(2048).decode()
            
            if data == "waiting":
                if games[gameId].start:
                    conn.send(str.encode("start"))
                else:
                    conn.send(str.encode(str(games[gameId].playersConnected)))
                 
                
            elif data == "ready":
                conn.send(str.encode(str("ok")))
                
                pInfo = pickle.loads(conn.recv(4096*8))
                
                if not pInfo:
                    print("Desconectado")
                    break
                else:
                    games[gameId].playerNetInfo[p] = pInfo
                    
                    resp = games[gameId].playerNetInfo
                    
                    print("Recebido: ", pInfo)
                    print("Mandando: ", resp)
                
                conn.sendall(pickle.dumps(resp))
            elif data == "disconnect":
                games[gameId].playerNetInfo[p][4] = False
                break
            else:
                break
        except:
            print("Conexão perdida")
            break
    print("Fechando conexão em: ", addr)
    conn.close()

    if idCount == 1:
        del(games[gameId])
        idCount = 0
        print("Fechando partida")
    else:
        idList.append(p)
        games[gameId].playersConnected -= 1
        idCount -= 1
    

while True:
    conn, addr = s.accept()
    
    idCount += 1
    gameId = (idCount - 1)//PLAYERS_QTD # o 2 aqui controla a quantidade de pessoas por jogo
    if idCount % PLAYERS_QTD == 1: 
        games[gameId] = Encouracados(gameId)
        print("Criando um novo jogo...")                
        idList = list(i for i in range(PLAYERS_QTD))
    elif idCount % PLAYERS_QTD == 0:
        games[gameId].start = True
        
    games[gameId].playersConnected += 1
    
    print("Conectado em: ", addr)
    start_new_thread(threaded_client, (conn, addr, idList.pop(), gameId))






















"""
--- Ideia principal ---

Seguimento do Server: 
    LOOP DO SERVER:
        Server: espera player 1 se conectar
            Server: serve uma sala vazia para player 1 com um aviso de espera de um novo jogador
        Server: espera player 2 se conectar
            Server: cria uma thread de jogo para ambos os players
        
Seguimento do Jogo:
    Thread de jogo: controla o jogo dos jogadores até o fim da partida
    Thread de jogo: ao fim da partida disponibiliza tela de vitoria/derrota e um botão de proxima partida
    Thread de jogo: quando clicado no botão, a conecxão dos cliente é reiniciada pareando novamente com o Server

    
Seguimento do Client:
    Client: Serve uma tela com o menu do jogo (botão jogar)
    LOOP do Cliente:
        Client: ao pressionar o botão, o jogador tentará se conectar ao servidor
        Client: quando uma partida começar, o cliente receberá as informações sobre o jogo para visualização e enviará os comandos do player
        Client: Ao termino do jogo, servira a tela de vitoria/derrota e diponibilizara o botão de jogar novamente
        Client: Ao enviar o botão de jogar novamente, tenta se reconectar com  servidor, reiniciando o loop

"""