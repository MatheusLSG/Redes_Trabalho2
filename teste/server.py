
import socket 
from  _thread import * 
from teste.player import Player
import pickle

server = "192.168.15.3"
porta = 5555 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, porta))
except socket.error as e:
    str(e)

s.listen(2)
print("Esperando conexões, Server disponivel")


players =   [
            Player(0,0,50,50,(255,0,0)),
            Player(100,100,50,50,(0,255,0))
            ]

def thrd_client(conn: socket.socket, playerAtual: int):
    conn.send(pickle.dumps(players[playerAtual]))
    resposta = ""
    while True:
        try:
            dado = pickle.loads(conn.recv(2048))
            players[playerAtual] = dado
            
            if not dado:
                print("Desconectado")
                break
            else:
                if playerAtual == 1:
                    resposta = players[0]
                else:
                    resposta = players[1]
                
                print("Recebido: ", dado)
                print("Mandando: ", resposta)
            
            conn.sendall(pickle.dumps(resposta))
        except:
            break

    print("Conexão perdida")
    conn.close()

playerAtual = 0
while True:
    conn, addr = s.accept()
    print("Conectado em: ", addr)

    start_new_thread(thrd_client, (conn, playerAtual))
    playerAtual += 1
































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