
import pygame as pg
import sys
import pandas as pd
import gc

#DEFINES


TELA_LARGURA = 960
TELA_ALTURA = 704

MAPA_LARGURA = 960 
MAPA_ALTURA = 704 

BLOCO_SPRITE_LARGURA = 32
BLOCO_SPRITE_ALTURA = 32
BLOCO_QTD_H = int(MAPA_LARGURA/BLOCO_SPRITE_LARGURA) # 960/32 = 30
BLOCO_QTD_V = int(MAPA_ALTURA/BLOCO_SPRITE_ALTURA) # 704/32 = 22
BLOCO_SPRITE_PATH = "sprites/mapa/bloco.png"

#Cores
PRETO = (0,0,0)
BRANCO = (255,255,255)
AZUL = (0,100,255)
LARANJA = (255,100,0)
AREIA = (255, 247, 193)

PLAYERS_QTD = 3

#
INI_POS_P = [
            (64,360),
            (896,360),
            (480,64)
            ]

INI_ANG_P = [
            -90, 
            90,
            180
            ]

SPRITE_P_PATH = [
                "sprites/jogador/tanqueJogador1.png", 
                "sprites/jogador/tanqueJogador2.png", 
                "sprites/jogador/tanqueJogador2.png"
                ]

INPUTS_P = [
            (pg.K_a, pg.K_d, pg.K_w, pg.K_s, pg.K_SPACE), 
            (pg.K_KP4, pg.K_KP6, pg.K_KP8, pg.K_KP5, pg.K_KP_ENTER),
            (pg.K_a, pg.K_d, pg.K_w, pg.K_s, pg.K_SPACE)
            ]
TEXTO_VITORIA_P = [
                    'Player 1 Venceu!',
                    'Player 2 Venceu!',
                    'Player 3 Venceu!'
                    ]
COR_VITORIA_P = [
                    AZUL,
                    LARANJA,
                    BRANCO
                    ]
#
TANQUE_SPRITE_LARGURA = 64
TANQUE_SPRITE_ALTURA = 64
TANQUE_PROPORCAO = 0.5

TANQUE_VEL_LIN = 2
TANQUE_VEL_ANG = 2
TANQUE_TIRO_QTD = 2
TANQUE_TIRO_CD = 1000 #em ms

BALA_SPRITE_LARGURA = 8
BALA_SPRITE_ALTURA = 16
BALA_PROPORCAO = 0.5

BALA_VEL_LIN = 5

BALA_TEMPO_DE_VIDA = 1000 #em ms



TEXTO_FONTE = 'comicsansms'


#END

#print(pg.font.get_fonts())


class Mapa():
    def __init__(self):
        df = pd.read_excel("mapas/mapa.xlsx", sheet_name=0, header=None)
        self.data = df.to_numpy()
        
        self.blocos: list[list[Bloco]]
        self.blocos = [ [] for _ in range(BLOCO_QTD_V) ]
        for x in range(BLOCO_QTD_V):
            for y in range(BLOCO_QTD_H):
                self.blocos[x].append(None)
        #print(self.data)
               

class Bloco(pg.sprite.Sprite):
    def __init__(self, imagem: pg.Surface, iniPos: tuple[int, int]):
        pg.sprite.Sprite.__init__(self)
        self.image = imagem
        self.largura = BLOCO_SPRITE_LARGURA 
        self.altura = BLOCO_SPRITE_ALTURA
        self.image = pg.transform.scale(self.image, ( self.largura , self.altura))
        self.rect = self.image.get_rect(center=iniPos)

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

class Bala(pg.sprite.Sprite):
    
    def __init__(self, tanque: Tanque):
        # Inicializando variaveis
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/bala/bala.png")
        
        self.tanque = tanque
        self.tanque.tiroDisponivel -= 1
        
        self.angulo = tanque.angulo
        self.image = pg.transform.scale(self.image, (BALA_SPRITE_LARGURA*BALA_PROPORCAO, BALA_SPRITE_ALTURA*BALA_PROPORCAO))
        self.image = pg.transform.rotate(self.image, self.angulo)


        vetor = pg.Vector2(0,1).rotate(self.angulo)

        tcx = tanque.rect.centerx
        tcy = tanque.rect.centery
        tl = tanque.largura
        ta = tanque.altura
        
        self.rect = self.image.get_rect(center=(tcx,tcy))

        self.rect.centerx += (tl/2)*vetor.x
        self.rect.centery -= (ta/2)*vetor.y

        self.pos = pg.Vector2(self.rect.center)

        self.tempo = pg.time.get_ticks()

        

    def update(self):

        # Trata rotacao
        direcao = pg.Vector2(0,1).rotate(self.angulo)

        self.pos.x += BALA_VEL_LIN*direcao.x
        self.pos.y -= BALA_VEL_LIN*direcao.y
        
        novoRetangulo = self.image.get_rect(center = self.image.get_rect(center = (self.pos.x, self.pos.y)).center)

        self.rect = novoRetangulo

        if pg.time.get_ticks() - self.tempo >= TANQUE_TIRO_CD:
            self.destroi()
        

        # Timer de vida
        if pg.time.get_ticks() - self.tempo >= BALA_TEMPO_DE_VIDA:
            self.remove(self.groups())
            
    
    def draw(self, surface: pg.Surface):
        # blit yourself at your current position
        
        surface.blit(self.image, dest=self.rect)

    def destroi(self):
        self.tanque.tiroDisponivel += 1
        self.kill()
        del(self)


class Jogo(pg.sprite.Sprite):

    def __init__(self):
        #Inicializando variaveis
        self.rodando = True
        self.telaLargura = TELA_LARGURA 
        self.telaAltura =  TELA_ALTURA
        self.textoFont = TEXTO_FONTE
        
        self.tela = pg.display.set_mode((self.telaLargura, self.telaAltura))
        
        self.grupoSpritesTodos = pg.sprite.Group()

        #PLayers
        self.grupoBalasPlayers: list[pg.sprite.Group] = list()
        self.tanquePlayers: list[Tanque] = list()

        for i in range(PLAYERS_QTD):
            gb = pg.sprite.Group()
            self.grupoBalasPlayers.append(gb)

            imagemP1 = pg.image.load(SPRITE_P_PATH[i])
            self.tanquePlayers.append(Tanque(imagemP1, gb, INI_POS_P[i], INI_ANG_P[i], INPUTS_P[i], TEXTO_VITORIA_P[i], COR_VITORIA_P[i]))
            self.grupoSpritesTodos.add(self.tanquePlayers[i])

            
        
        #Contrucao do mapa
        self.grupoMapa = pg.sprite.Group()
        
        self.mapa = Mapa()
        
        imagemBloco = pg.image.load(BLOCO_SPRITE_PATH)
        for i in range(BLOCO_QTD_V):
            for j in range(BLOCO_QTD_H):
                if self.mapa.data[i][j] == 1:
                    bc = Bloco( imagemBloco, (BLOCO_SPRITE_LARGURA*(j+0.5),BLOCO_SPRITE_ALTURA*(i+0.5)) )
                    self.mapa.blocos[i][j] = bc
                    self.grupoMapa.add(bc)


        self.tanquesVivos = PLAYERS_QTD

        self.restart = 0
        #bala = Bala(self.tanquePlayer)
        #self.grupoSpritesTodos.add(bala)
        #self.grupoBalas.add(bala)

    def trataEventos(self):
          
        # Trata eventos dos players
        for t in self.tanquePlayers:
            if t.alive():
                t.trataEventos()
        # Trata eventos de Dispara balas
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.rodando = False
                return
            elif evento.type == pg.KEYDOWN:
                if evento.key == pg.K_ESCAPE:
                    self.rodando = False
                    return
                for t in self.tanquePlayers:
                    if (evento.key == t.comandos[4] and 
                        t.tiroDisponivel and 
                        t.alive()  
                    ):
                        bala = Bala(t)
                        t.grupoBalas.add(bala)
                        self.grupoSpritesTodos.add(bala)

        # Trata colisao de balas com balas
        b: Bala
        k: Bala
        
        for g in self.grupoBalasPlayers:
            for h in self.grupoBalasPlayers:
                if g == h:
                    continue
               
                for b in g:
                    for k in pg.sprite.spritecollide(b, h, False):
                        print("BLING")
                        k.remove(k.tanque.grupoBalas)
                        b.remove(b.tanque.grupoBalas)
                        break

        # Trata colisao de balas com paredes
        for g in self.grupoBalasPlayers:
            for b in g:
                if pg.sprite.spritecollide(b, self.grupoMapa, False) != []:
                    b.remove(b.tanque.grupoBalas)
                    break
    

        b: Bala
        
        # Trata colisao de balas com players
        for t in self.tanquePlayers:
            for g in self.grupoBalasPlayers:
                if t.grupoBalas == g:
                    continue
                for b in pg.sprite.spritecollide(t, g, False):
                    b.remove(b.tanque.grupoBalas)
                    self.tanquePlayers.remove(t)
                    t.kill()
                    self.tanquesVivos -= 1
                    break
    

    def update(self):
        self.grupoSpritesTodos.update()

    def draw(self):
        self.tela.fill(AREIA)
        self.grupoMapa.draw(self.tela)  
        
        t: Tanque
        for t in self.tanquePlayers:
            t.draw(self.tela)
        
        b: Bala
        for t in self.tanquePlayers:
            for b in t.grupoBalas:
                b.draw(self.tela)
        
        pg.display.update()

    def trataColisaoParede(self, tanque: Tanque):
        bloco: Bloco
        tanque.vaiColidirAll = 0
        tanque.vaiColidirD = 0
        tanque.vaiColidirE = 0
        tanque.vaiColidirC = 0
        tanque.vaiColidirB = 0
        teclas = pg.key.get_pressed()
        xVel = 0
        yVel = 0
        if teclas[tanque.comandos[2]]:
            xVel += TANQUE_VEL_LIN*tanque.direcao.x
            yVel -= TANQUE_VEL_LIN*tanque.direcao.y
        if teclas[tanque.comandos[3]]:
            xVel -= TANQUE_VEL_LIN*tanque.direcao.x
            yVel += TANQUE_VEL_LIN*tanque.direcao.y

       
        absXVel = abs(xVel)
        absYVel = abs(yVel)

        TkFaceDir = tanque.rect.x+tanque.rect.w+xVel 
        TkFaceEsq = tanque.rect.x+xVel
        TkFaceBai = tanque.rect.y+tanque.rect.h+yVel
        TkFaceCim = tanque.rect.y+yVel

        vaiColH = 0
        vaiColV = 0 

        rX = range(BLOCO_QTD_H)
       
        rY = range(BLOCO_QTD_V)
       
        for y in rY:
            for x in rX:
                bloco = self.mapa.blocos[y][x]
                if bloco is not None:
                    BkFaceDir = bloco.rect.x+bloco.rect.w 
                    BkFaceEsq = bloco.rect.x
                    BkFaceBai = bloco.rect.y+bloco.rect.h
                    BkFaceCim = bloco.rect.y

                    colD = (TkFaceDir>=BkFaceEsq and TkFaceDir<=BkFaceDir)
                    colE = (TkFaceEsq<=BkFaceDir and TkFaceEsq>=BkFaceEsq)
                    colC = (TkFaceCim<=BkFaceBai and TkFaceCim>=BkFaceCim)
                    colB = (TkFaceBai>=BkFaceCim and TkFaceBai<=BkFaceBai)

                    colEH = (TkFaceEsq<=BkFaceEsq and TkFaceDir>=BkFaceDir)
                    colEV = (TkFaceCim<=BkFaceCim and TkFaceBai>=BkFaceBai)
                    
                    
                    

                    if(colD and colC):

                        if not tanque.vaiColidirD:
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1

                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1
                        
                    
                    if(colD and colB):


                        if not tanque.vaiColidirD:
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1
                        
                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1
                        
                    
                    if(colE and colC):


                        if not tanque.vaiColidirE:
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1

                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1
                            
                    
                    if(colE and colB):    
            
                        
                        if not tanque.vaiColidirE:      
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1

                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1


                    #Externas
                    

                    if(colEH and colB):
                        tanque.rect.y = bloco.rect.y - tanque.rect.h
                        
                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1 

                        if not vaiColH:
                            tanque.pos.y -= absYVel/2
                            vaiColH = 1
                        
                        #tanque.vaiColidirB = 1

                        
                            
                        

                    if(colEH and colC):
                        tanque.rect.y = bloco.rect.y + bloco.rect.h
                        
                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1 

                        if not vaiColH:    
                                tanque.pos.y += absYVel/2
                                vaiColH = 1
                        
                        #tanque.vaiColidirC = 1

                        
                            

                    if(colEV and colE):
                        tanque.rect.x = bloco.rect.x + bloco.rect.w 

                        if not tanque.vaiColidirE:      
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1
                        
                        if not vaiColV:      
                                tanque.pos.x += absXVel/2
                                vaiColV = 1


                    if(colEV and colD):
                        tanque.rect.x = bloco.rect.x - tanque.rect.w 
                        
                        if not tanque.vaiColidirD:
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1

                        if not vaiColV:
                                tanque.pos.x -= absXVel/2
                                vaiColV = 1
                        
                        
        if tanque.vaiColidirB and tanque.vaiColidirC and tanque.vaiColidirE and tanque.vaiColidirD:
            tanque.vaiColidirAll = 1
        
        
        

    def trataVitoria(self):
        # Imprime texto de vitoria
        fonte = pg.font.SysFont(self.textoFont, 30)
        textoVitoriaSombra =  fonte.render('Erro', False, PRETO)
        textoVitoria =  fonte.render('Erro', False, PRETO)
        
        
        textoVitoriaSombra =  fonte.render(self.tanquePlayers[0].textoVitoria, False, PRETO)
        textoVitoria = fonte.render(self.tanquePlayers[0].textoVitoria, False, self.tanquePlayers[0].corVitoria)
        
        meiox = ((self.telaLargura-textoVitoria.get_width())/2)
        meioy = ((self.telaAltura-textoVitoria.get_height())/2)

        self.tela.blit(textoVitoriaSombra, ( meiox+1, meioy+1 ))
        self.tela.blit(textoVitoriaSombra, ( meiox+1, meioy-1 ))
        self.tela.blit(textoVitoriaSombra, ( meiox-1, meioy+1 ))
        self.tela.blit(textoVitoriaSombra, ( meiox-1, meioy-1 ))
        
        self.tela.blit(textoVitoria, ( meiox, meioy ))
        pg.display.update()
        
        # loop de checagem de eventos de termino ou reset
        done = False
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        done = True
                        self.restart = 1
                    if event.key == pg.K_ESCAPE:
                        done = True
            pg.time.Clock().tick(60)

        self.rodando = False
            
def main():
    pg.init()
    pg.font.init() 
    pg.display.set_caption('Encouraçados')
    clock = pg.time.Clock()

    restart = 1

    # Loop do app
    while restart:
        restart = 0
        # Instancia um novo jogo    
        jogo = Jogo()

        # Loop do jogo
        while jogo.rodando:
            if jogo.tanquesVivos > 1:
                for t in jogo.tanquePlayers:
                    jogo.trataColisaoParede(t)
                jogo.trataEventos()
                jogo.update()
                jogo.draw()
                clock.tick(60)
            else:
                jogo.trataVitoria()
        
        # Checa se o jogo vai ser reiniciado
        restart = jogo.restart

        # Deleta instancia passada do jogo
        del(jogo)

        gc.collect()


if __name__ == '__main__':
    main()
    pg.quit()
    sys.exit()

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