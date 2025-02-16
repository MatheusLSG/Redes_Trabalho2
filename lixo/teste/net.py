import socket
import pickle

class Rede:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.15.3"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.conectar()
    
    def getP(self):
        return self.p
    
    def conectar(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            print("Erro")
            pass

    def enviar(self, dado):
        try:
            self.client.send(pickle.dumps(dado))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)


