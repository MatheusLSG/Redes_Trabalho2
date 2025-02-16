# Importar módulo de socket

from socket import *
import sys  # Para encerrar o programa

serverSocket = socket(AF_INET, SOCK_STREAM)

# Preparar um socket de servidor
# Fill in start
serverSocket.bind(('', 6789))
serverSocket.listen(1)
# Fill in end

while 1:
    # Estabelecer a conexão
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()  # Fill in start, Fill in end

    try:
        message = connectionSocket.recv(1024)  # Fill in start, Fill in end
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()  # Fill in start, Fill in end

        # Enviar uma linha de cabeçalho HTTP para o socket
        # Fill in start
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        # Fill in end

        connectionSocket.sendall(outputdata.encode())


        connectionSocket.close()
    except IOError:
        # Enviar mensagem de resposta para arquivo não encontrado
        # Fill in start
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        # Fill in end

        # Fechar o socket do cliente
        # Fill in start
        connectionSocket.close()
        # Fill in end

serverSocket.close()
sys.exit()  # Termina o programa após enviar os dados correspondentes

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