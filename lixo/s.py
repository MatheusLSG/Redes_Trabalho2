
import socket 
from  _thread import * 
import pickle
from ppt import Game
server = "192.168.15.3"
porta = 5555 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, porta))
except socket.error as e:
    str(e)

s.listen()
print("Esperando conexões, Server disponivel")

connected = set()
games:dict[int,Game] = {}
idCount = 0

def threaded_client(conn: socket.socket, p: int, gameId):
    global idCount
    conn.send(str.encode(str(p)))
    
    reply = ""
    while True:
        data = conn.recv(4096).decode()
        
        if gameId in games:
            game = games[gameId]
            
            if not data:
                break
            else:
                if data == "reset":
                    game.reset()
                elif data != "get":
                    game.play(p, data)
            
                reply = game
                conn.sendall(pickle.dumps(reply))
                

while True:
    conn, addr = s.accept()
    print("Conectado em: ", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2 # o 2 aqui controla a quantidade de pessoas por jogo
    if idCount % 2 == 1: 
        games[gameId] = Game(gameId)
        print("Criando um novo jogo...")
    else:
        games[gameId].ready = True
        p = 1
    
    start_new_thread(threaded_client, (conn, p, gameId))

































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