
import pygame as pg
import sys
import pandas as pd

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


INI_POS_P1 = (64,360)
INI_ANG_P1 = -90
INI_POS_P2 = (896,360)
INI_ANG_P2 = 90

TANQUE_SPRITE_LARGURA = 64
TANQUE_SPRITE_ALTURA = 64
TANQUE_PROPORCAO = 0.5

TANQUE_VEL_LIN = 2
TANQUE_VEL_ANG = 2
TANQUE_TIRO_QTD = 1

BALA_SPRITE_LARGURA = 8
BALA_SPRITE_ALTURA = 16
BALA_PROPORCAO = 0.5

BALA_VEL_LIN = 5

BALA_TEMPO_DE_VIDA = 1000 #em ms

SPRITE_P1_PATH = "sprites/jogador/tanqueJogador1.png"
SPRITE_P2_PATH = "sprites/jogador/tanqueJogador2.png"

INPUTS_P1 = (pg.K_a, pg.K_d, pg.K_w, pg.K_s, pg.K_SPACE)
INPUTS_P2 = (pg.K_KP4, pg.K_KP6, pg.K_KP8, pg.K_KP5, pg.K_KP_ENTER)

TEXTO_FONTE = 'comicsansms'
TEXTO_VITORIA_P1 = 'Player 1 Venceu!'
TEXTO_VITORIA_P2 = 'Player 2 Venceu!'
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
    def __init__(self, imagem: pg.Surface, iniPos: tuple[int, int], iniAng: int, inputs: tuple[int, int,  int,  int, int]):
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

        

        # Timer de vida
        if pg.time.get_ticks() - self.tempo >= BALA_TEMPO_DE_VIDA:
            self.destroi()
    
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
        self.textoP1 = TEXTO_VITORIA_P1
        self.textoP2 = TEXTO_VITORIA_P2 
        self.tela = pg.display.set_mode((self.telaLargura, self.telaAltura))
        
        self.grupoSpritesTodos = pg.sprite.Group()

        self.grupoBalasP1 = pg.sprite.Group()
        self.grupoBalasP2 = pg.sprite.Group()
        
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


        imagemP1 = pg.image.load(SPRITE_P1_PATH)
        self.tanquePlayer1 = Tanque(imagemP1, INI_POS_P1, INI_ANG_P1, INPUTS_P1)
        self.grupoSpritesTodos.add(self.tanquePlayer1)
        
        imagemP2 = pg.image.load(SPRITE_P2_PATH)
        self.tanquePlayer2 = Tanque(imagemP2, INI_POS_P2, INI_ANG_P2, INPUTS_P2)
        self.grupoSpritesTodos.add(self.tanquePlayer2)
        
        self.vencendor = 0
        self.restart = 0
        #bala = Bala(self.tanquePlayer)
        #self.grupoSpritesTodos.add(bala)
        #self.grupoBalas.add(bala)

    def trataEventos(self):

        #keys = pg.key.get_pressed()
        

        # Trata eventos dos players
        if self.tanquePlayer1.alive():
            self.tanquePlayer1.trataEventos()
        if self.tanquePlayer2.alive():
            self.tanquePlayer2.trataEventos()
        
        # Trata eventos de teclado e saida
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.rodando = False
            elif evento.type == pg.KEYDOWN:
                if evento.key == pg.K_ESCAPE:
                    self.rodando = False
                #Dispara balas p1
                if evento.key == self.tanquePlayer1.comandos[4] and self.tanquePlayer1.tiroDisponivel and self.tanquePlayer1.alive():
                    bullet = Bala(self.tanquePlayer1)
                    self.grupoBalasP1.add(bullet)
                    self.grupoSpritesTodos.add(bullet)
                #Dispara balas p2
                if evento.key == self.tanquePlayer2.comandos[4] and self.tanquePlayer2.tiroDisponivel and self.tanquePlayer2.alive():
                    bullet = Bala(self.tanquePlayer2)
                    self.grupoBalasP2.add(bullet)
                    self.grupoSpritesTodos.add(bullet)
                
                    
        # Trata colisao de balas com balas
        b: Bala
        for b in self.grupoBalasP1:
            k: Bala
            for k in pg.sprite.spritecollide(b, self.grupoBalasP2, True):
                k.destroi()
                b.destroi()
                break
        # Trata colisao de balas com paredes
        for b in self.grupoBalasP1:
            if pg.sprite.spritecollide(b, self.grupoMapa, False) != []:
                b.destroi()
                break

        for b in self.grupoBalasP2:
            if pg.sprite.spritecollide(b, self.grupoMapa, False) != []:
                b.destroi()
                break
        # Trata colisao de balas com players
        #p1
        if pg.sprite.spritecollide(self.tanquePlayer1, self.grupoBalasP2, False) != [] and self.tanquePlayer1.alive():
    
            for b in self.grupoBalasP1.sprites():
                b.destroi()
            for b in self.grupoBalasP2.sprites():
                b.destroi()
    
            self.tanquePlayer1.kill()
            self.grupoSpritesTodos.remove(self.tanquePlayer1)
            
            self.vencendor = 2

            del(self.tanquePlayer1)
        #p2
        if pg.sprite.spritecollide(self.tanquePlayer2, self.grupoBalasP1, False ) != [] and self.tanquePlayer2.alive():        
            b : Bala
            for b in self.grupoBalasP1.sprites():
                b.destroi()
            for b in self.grupoBalasP2.sprites():
                b.destroi()
    
            self.vencendor = 1

            self.tanquePlayer2.kill()
            self.grupoSpritesTodos.remove(self.tanquePlayer2)
            del(self.tanquePlayer2)

    def update(self):
        self.grupoSpritesTodos.update()

    def draw(self):
        self.tela.fill(AREIA)
        self.grupoMapa.draw(self.tela)  
        if self.vencendor != 2:
            self.tanquePlayer1.draw(self.tela)
        if self.vencendor != 1:
            self.tanquePlayer2.draw(self.tela)
        
        b: Bala
        for b in self.grupoBalasP1:
            b.draw(self.tela)
        for b in self.grupoBalasP2:
            b.draw(self.tela)
            #self.grupoSpritesTodos.draw(self.tela)  
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
        for x in range(BLOCO_QTD_V):
            for y in range(BLOCO_QTD_H):
                bloco = self.mapa.blocos[x][y]
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
                        if absXVel>=absYVel:
                            tanque.rect.x = bloco.rect.x - tanque.rect.w
                        else:
                            tanque.rect.y = bloco.rect.y + bloco.rect.h
                        
                        if not tanque.vaiColidirD:
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1

                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1
                        
                    
                    if(colD and colB):
                        if absXVel>=absYVel:
                            tanque.rect.x = bloco.rect.x - tanque.rect.w 
                        else:
                            tanque.rect.y = bloco.rect.y - tanque.rect.h

                        if not tanque.vaiColidirD:
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1
                        
                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1
                        
                    
                    if(colE and colC):
                        if absXVel>=absYVel:
                            tanque.rect.x = bloco.rect.x + bloco.rect.w 
                        else:
                            tanque.rect.y = bloco.rect.y + bloco.rect.h

                        if not tanque.vaiColidirE:
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1

                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1
                            
                    
                    if(colE and colB):    
                        if absXVel>=absYVel:
                            tanque.rect.x = bloco.rect.x + bloco.rect.w 
                        else:
                            tanque.rect.y = bloco.rect.y - tanque.rect.h
             
                        
                        if not tanque.vaiColidirE:      
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1

                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1


                    

                    if(colEH and colB):
                        tanque.rect.y = bloco.rect.y - tanque.rect.h
                        
                        if not vaiColH:

                            tanque.pos.y -= absYVel/2
                            vaiColH = 1

                    if(colEH and colC):
                        tanque.rect.y = bloco.rect.y + bloco.rect.h
                        
                        if not vaiColH:    

                            tanque.pos.y += absYVel/2
                            vaiColH = 1

                    if(colEV and colE):
                        tanque.rect.x = bloco.rect.x + bloco.rect.w 

                        if not vaiColV:      

                            tanque.pos.x += absXVel/2
                            vaiColV = 1

                    if(colEV and colD):
                        tanque.rect.x = bloco.rect.x - tanque.rect.w 
                        
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
        
        if self.vencendor == 1:
            textoVitoriaSombra =  fonte.render(self.textoP1, False, PRETO)
            textoVitoria = fonte.render(self.textoP1, False, AZUL)
        if self.vencendor == 2:
            textoVitoriaSombra =  fonte.render(self.textoP2, False, PRETO)
            textoVitoria = fonte.render(self.textoP2, False, LARANJA)

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
            if jogo.vencendor == 0:
                jogo.trataColisaoParede(jogo.tanquePlayer1)
                jogo.trataColisaoParede(jogo.tanquePlayer2)
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