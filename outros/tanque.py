import pygame as pg

TANQUE_SPRITE_LARGURA = 64
TANQUE_SPRITE_ALTURA = 64
TANQUE_PROPORCAO = 0.5

TANQUE_VEL_LIN = 2
TANQUE_VEL_ANG = 2
TANQUE_TIRO_QTD = 2
TANQUE_TIRO_CD = 1000 #em ms

class Tanque(pg.sprite.Sprite):
    #                                                                                          (esq|dir|cima|baixo|tiro)
    def __init__(self, imagem: pg.Surface, grupoBalas: pg.sprite.Group, iniPos: tuple[int, int], iniAng: int, inputs: tuple[int, int,  int,  int, int], textoVitoria, corVitoria):
        # Inicializando variaveis
        pg.sprite.Sprite.__init__(self)
        
        self.largura = TANQUE_SPRITE_LARGURA*TANQUE_PROPORCAO
        self.altura = TANQUE_SPRITE_ALTURA*TANQUE_PROPORCAO
        
        self.image = imagem
        self.image = pg.transform.scale(self.image, ( self.largura , self.altura))
        self.org_image = self.image.copy()

        self.rect = self.image.get_rect(center=iniPos)
        self.comandos = inputs
        self.angulo = iniAng
        self.direcao = pg.Vector2((1,0))
        self.pos = pg.Vector2(self.rect.center)
        
        self.grupoBalas = grupoBalas
        
        self.textoVitoria = textoVitoria
        self.corVitoria = corVitoria



        self.vaiColidirAll = 0

        self.vaiColidirD = 0
        self.vaiColidirE = 0
        self.vaiColidirC = 0
        self.vaiColidirB = 0
        
        self.tiroDisponivel = TANQUE_TIRO_QTD

    def trataEventos(self):
        #CLIENTE MANDA
        teclas = pg.key.get_pressed()
        
        #SERVIDOR PROCESSA
        if teclas[self.comandos[0]]:
            self.angulo += TANQUE_VEL_ANG
            
        if teclas[self.comandos[1]]:
            self.angulo -= TANQUE_VEL_ANG

        self.direcao = pg.Vector2(0, 1).rotate(self.angulo)
        
        if not self.vaiColidirAll:
            if teclas[self.comandos[2]]:
                self.pos.x += TANQUE_VEL_LIN*self.direcao.x*(1 - abs(self.vaiColidirD - self.vaiColidirE)/2)
                self.pos.y -= TANQUE_VEL_LIN*self.direcao.y*(1 - abs(self.vaiColidirB - self.vaiColidirC)/2)
            if teclas[self.comandos[3]]:
                self.pos.x -= TANQUE_VEL_LIN*self.direcao.x*(1 - abs(self.vaiColidirD - self.vaiColidirE)/2)
                self.pos.y += TANQUE_VEL_LIN*self.direcao.y*(1 - abs(self.vaiColidirB - self.vaiColidirC)/2)
            
        self.vaiColidir = 0

        imagemRotacionada = pg.transform.rotate(self.org_image, self.angulo)
        novoRetangulo = imagemRotacionada.get_rect(center = self.image.get_rect(center = (self.pos.x, self.pos.y)).center)

        self.image = imagemRotacionada
        self.rect = novoRetangulo        
            

        # CLIENTE RECEBE
        # RECT, IMAGEM, DIRECAO e ANGULO / DO SERVER
  
    def draw(self, surface: pg.Surface):
        # blit yourself at your current position
        
        surface.blit(self.image, dest=self.rect)
