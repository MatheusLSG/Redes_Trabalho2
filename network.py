import socket
import pickle

from globals import PLAYERS_QTD

class Network:
    def __init__(self, server):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = 5555
        self.addr = (self.server, self.port)
      
    
    def getP(self):
        return self.p
    
    def disconnect(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)        
            self.client.close() 
        except:
            print("Erro durante desligamento ao servidor")
            pass
        
    def connect(self):
        try:
            self.client.connect(self.addr)          #Se conecta ao server
            return self.client.recv(2048).decode()  #Recebe resposta string do server
        except:
            print("Erro durante conexão com servidor")
            pass

    def sendObj(self, data):
        try:
            self.client.send(pickle.dumps(data))        #manda player
            rec = self.client.recv(4096*4*PLAYERS_QTD)
            if rec:
                return pickle.loads(rec)        #recebe players
            else:
                return None
        except socket.error as e:
            print(e)

    def sendStr(self, data: str):
        try:
            self.client.send(str.encode(data))          #manda str
            return (self.client.recv(2048)).decode()  #recebe str
        except socket.error as e:
            print(e)


