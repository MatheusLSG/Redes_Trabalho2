
import pygame as pg
import sys
import gc

from button import Button
from player import Tank
from player import Bullet
from map import Map, Block
from globals import *


#END

#print(pg.font.get_fonts())



class Jogo(pg.sprite.Sprite):

    def __init__(self):
        #Inicializando variaveis
        self.gameState = 0
        self.inGame = True
        self.screenWidth = TELA_LARGURA 
        self.screenHeight =  TELA_ALTURA
        self.fontText = pg.font.SysFont(TEXTO_FONTE, 30)
        
        self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight))
        
        self.allSpritesGroup = pg.sprite.Group()
        #Texto
        self.nameBox = pg.Rect(TELA_LARGURA/2-175, TELA_ALTURA/2-25, 350, 50)
        self.NBActiveColor = BRANCO
        self.NBPassiveColor = CINZA
        self.NBActive = False
        self.playerName = ''
        
        self.eventList: list[pg.event.Event] 
        self.eventList = list()
        
        #Botoes
        btImage = pg.image.load(BTJOGAR_SPRITE_PATH)
        btY = TELA_ALTURA/2
        btX = TELA_LARGURA/2
        
        self.playButton = Button(btX,btY,btImage,2)

        #PLayers
        self.playerBulletGroup: list[pg.sprite.Group] = list()
        self.playerTanks: list[Tank] = list()

        for i in range(PLAYERS_QTD):
            playerImg = pg.image.load(SPRITE_P_PATH[i])
            
            t = Tank(playerImg,
                     TANQUE_PROPORCAO, 
                     INI_POS_P[i], 
                     TANQUE_VEL_LIN, 
                     INI_ANG_P[i], 
                     TANQUE_VEL_ANG, 
                     TANQUE_TIRO_QTD,
                     TANQUE_TIRO_CD,
                     TEXTO_VITORIA_P[i],
                     COR_VITORIA_P[i])
            
            self.playerBulletGroup.append(t.bulletGroup)
            self.playerTanks.append(t)
            self.allSpritesGroup.add(t)

        #Bala
        
        self.bulletImg = pg.image.load(SPRITE_BALA_PATH)
        #Contrucao do map
        
        self.blockImg = pg.image.load(SPRITE_BLOCO_PATH)
        
        self.map = Map(self.blockImg, MAP_DATAPATH)

        self.playersAlive = PLAYERS_QTD

        #bala = Bullet(self.tanquePlayer)
        #self.allSpritesGroup.add(bala)
        #self.bulletGroup.add(bala)

    def eventHandling(self):
          
        # Trata eventos dos players
        for t in self.playerTanks:
            if t.alive():
                t.move(self.map.mapGroup)   

        # Trata eventos de Dispara balas
        for evento in self.eventList:           
            if evento.type == pg.KEYDOWN:
                for t in self.playerTanks:
                    if (evento.key == pg.K_SPACE and 
                        t.bulletQtd and 
                        t.alive()  
                    ):
                        b = Bullet(self.bulletImg,
                                      BALA_PROPORCAO,
                                      BALA_VEL_LIN,
                                      t)
                        t.bulletGroup.add(b)
                        self.allSpritesGroup.add(b)

        # Trata colisao de balas com balas
        b: Bullet
        k: Bullet
        
        for g in self.playerBulletGroup:
            for h in self.playerBulletGroup:
                if g == h:
                    continue
               
                for b in g:
                    for k in pg.sprite.spritecollide(b, h, False):
                        print("BLING")
                        k.remove(k.tank.bulletGroup)
                        b.remove(b.tank.bulletGroup)
                        break

        # Trata colisao de balas com paredes
        for g in self.playerBulletGroup:
            for b in g:
                if pg.sprite.spritecollide(b, self.map.mapGroup, False) != []:
                    b.remove(b.tank.bulletGroup)
                    break
    

        b: Bullet
        
        # Trata colisao de balas com players
        for t in self.playerTanks:
            for g in self.playerBulletGroup:
                if t.bulletGroup == g:
                    continue
                for b in pg.sprite.spritecollide(t, g, False):
                    b.remove(b.tank.bulletGroup)
                    self.playerTanks.remove(t)
                    t.kill()
                    self.playersAlive -= 1
                    break
    
    def update(self):
        self.allSpritesGroup.update()

    def draw(self):
        self.screen.fill(AREIA)
        self.map.draw(self.screen)  
        
        t: Tank
        for t in self.playerTanks:
            t.draw(self.screen)
        
        b: Bullet
        for t in self.playerTanks:
            for b in t.bulletGroup:
                b.draw(self.screen)
        

    def trataColisaoParede(self, tank: Tank):
        bloco: Block
     
        teclas = pg.key.get_pressed()
        xVel = 0
        yVel = 0
        if teclas[tank.comandos[2]]:
            xVel += TANQUE_VEL_LIN*tank.direcao.x
            yVel -= TANQUE_VEL_LIN*tank.direcao.y
        if teclas[tank.comandos[3]]:
            xVel -= TANQUE_VEL_LIN*tank.direcao.x
            yVel += TANQUE_VEL_LIN*tank.direcao.y

       
        absXVel = abs(xVel)
        absYVel = abs(yVel)

        TkFaceDir = tank.rect.x+tank.rect.w+xVel 
        TkFaceEsq = tank.rect.x+xVel
        TkFaceBai = tank.rect.y+tank.rect.h+yVel
        TkFaceCim = tank.rect.y+yVel

        vaiColH = 0
        vaiColV = 0 

        rX = range(BLOCO_QTD_H)
       
        rY = range(BLOCO_QTD_V)
       
        for y in rY:
            for x in rX:
                if tank.vaiColidirAll:
                    break
                bloco = self.map.blocos[y][x]
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
                    
                    #Externas
                    

                    if(colEH and colB):
                        tank.rect.y = bloco.rect.y - tank.rect.h
                        
                        if not tank.vaiColidirB:   
                            tank.pos.y -= absYVel/2
                            tank.vaiColidirB = 1 

                        if not vaiColH:
                            tank.pos.y -= absYVel/2
                            vaiColH = 1
                        
                        #tank.vaiColidirB = 1

                        
                            
                        

                    if(colEH and colC):
                        tank.rect.y = bloco.rect.y + bloco.rect.h
                        
                        if not tank.vaiColidirC:    
                            tank.pos.y += absYVel/2
                            tank.vaiColidirC = 1 

                        if not vaiColH:    
                                tank.pos.y += absYVel/2
                                vaiColH = 1
                        
                        #tank.vaiColidirC = 1

                        
                            

                    if(colEV and colE):
                        tank.rect.x = bloco.rect.x + bloco.rect.w 

                        if not tank.vaiColidirE:      
                            tank.pos.x += absXVel/2
                            tank.vaiColidirE = 1
                        
                        if not vaiColV:      
                                tank.pos.x += absXVel/2
                                vaiColV = 1


                    if(colEV and colD):
                        tank.rect.x = bloco.rect.x - tank.rect.w 
                        
                        if not tank.vaiColidirD:
                            tank.pos.x -= absXVel/2
                            tank.vaiColidirD = 1

                        if not vaiColV:
                                tank.pos.x -= absXVel/2
                                vaiColV = 1
                    
                    #LADOS
                    if(colB and colC and colD):#D
                        if not tank.vaiColidirD:
                                tank.pos.x -= absXVel/2
                                tank.vaiColidirD = 1
                    
                    if(colB and colC and colE):#E
                        if not tank.vaiColidirE:
                                tank.pos.x += absXVel/2
                                tank.vaiColidirE = 1

                    if(colB and colE and colD):#B
                        if not tank.vaiColidirB:
                                tank.pos.y -= absYVel/2
                                tank.vaiColidirB = 1

                    if(colC and colE and colD):#C
                        if not tank.vaiColidirC:
                                tank.pos.y += absYVel/2
                                tank.vaiColidirC = 1                    

                    #CANTOS
                    if(colD and colC):#DC
                        if not tank.vaiColidirD :
                            tank.pos.x -= absXVel/2
                            tank.vaiColidirD = 1
                        if not tank.vaiColidirC:    
                            tank.pos.y += absYVel/2
                            tank.vaiColidirC = 1
                    
                    if(colD and colB):#DB
                        if not tank.vaiColidirD:
                            tank.pos.x -= absXVel/2
                            tank.vaiColidirD = 1
                        if not tank.vaiColidirB:   
                            tank.pos.y -= absYVel/2
                            tank.vaiColidirB = 1
                    
                    if(colE and colC):#EC
                        if not tank.vaiColidirE:
                            tank.pos.x += absXVel/2
                            tank.vaiColidirE = 1
                        if not tank.vaiColidirC:    
                            tank.pos.y += absYVel/2
                            tank.vaiColidirC = 1
                            
                    if(colE and colB):#EB 
                        if not tank.vaiColidirE:      
                            tank.pos.x += absXVel/2
                            tank.vaiColidirE = 1
                        if not tank.vaiColidirB:   
                            tank.pos.y -= absYVel/2
                            tank.vaiColidirB = 1


                    
                        
                        
        if tank.vaiColidirB and tank.vaiColidirC and tank.vaiColidirE and tank.vaiColidirD:
            tank.vaiColidirAll = 1

    def victoryHandling(self):
        # Imprime text de vitoria
  
        vencedor = self.playerTanks[0]

        text = vencedor.name
        
        meiox = ((self.screenWidth)/2)
        meioy = ((self.screenHeight)/2)
        
        corT = vencedor.color

        self.drawText(text,self.fontText,corT,PRETO,meiox,meioy)

        pg.display.update()
        
        self.inGame = 0
        
    def drawText(self, text, fonte: pg.font.Font, textColor, shadowColor, x, y):
        ts =  fonte.render(text, False, shadowColor)
        t = fonte.render(text, False, textColor)

        cTx = t.get_width()/2
        cTy = t.get_height()/2

        self.screen.blit(ts, ( x-cTx+1, y-cTy+1 ))
        self.screen.blit(ts, ( x-cTx+1, y-cTy-1 ))
        self.screen.blit(ts, ( x-cTx-1, y-cTy+1 ))
        self.screen.blit(ts, ( x-cTx-1, y-cTy-1 ))
        self.screen.blit(t, ( x-cTx, y-cTy ))

    def playMenu(self):
        self.screen.fill(AREIA)
        if self.playButton.draw(self.screen):
            self.gameState = 1

    def nameMenu(self):
        
        for event in self.eventList: 
    
            if event.type == pg.QUIT: 
                self.inGame = False
                self.gameState = -1
                break

            if event.type == pg.MOUSEBUTTONDOWN: 
                if self.nameBox.collidepoint(event.pos): 
                    self.NBActive = True
                else: 
                    self.NBActive = False
    
            if event.type == pg.KEYDOWN: 
                if event.key == pg.K_ESCAPE:
                    self.inGame = False
                    self.gameState = -1
                    break
                
                if event.key == pg.K_SPACE:
                    continue
                
                if event.key == pg.K_RETURN: 
                    if len(self.playerName)>0:
                        self.gameState = 2
                        self.playerTanks[0].name = self.playerName + ' Ganhou!'
                        break
                    continue

                if event.key == pg.K_BACKSPACE: 
                    self.playerName = self.playerName[:-1] 
                elif len(self.playerName) <= 20: 
                    self.playerName += event.unicode
        
        self.screen.fill(AREIA) 
    
        if self.NBActive: 
            cor = self.NBActiveColor 
        else: 
            cor = self.NBPassiveColor

        #"digite seu nome"
        instrucao = self.fontText.render("Digite seu nome:", False, PRETO)
        self.screen.blit(instrucao, (self.nameBox.centerx-instrucao.get_width()/2, self.nameBox.y-instrucao.get_height()-8))
        #desenha retangulo
        sombra = self.nameBox.copy()
        sombra.w = sombra.w + 4
        sombra.h = sombra.h + 4
        sombra.centerx = self.nameBox.centerx
        sombra.centery = self.nameBox.centery
        pg.draw.rect(self.screen, PRETO, sombra)
        pg.draw.rect(self.screen, cor, self.nameBox) 
    
        text = self.fontText.render(self.playerName, False, PRETO)
        #desenha nome
        self.screen.blit(text, (self.nameBox.centerx-text.get_width()/2, self.nameBox.centery-text.get_height()/2))
        
        #"Pressione 'Enter' para selecionar"
        instrucao = self.fontText.render("Pressione 'Enter' para selecionar", False, PRETO)
        self.screen.blit(instrucao, (self.nameBox.centerx-instrucao.get_width()/2, self.nameBox.y+instrucao.get_height()+8))
        
    def connectionMenu(self):
        
        self.screen.fill(AREIA)
        self.drawText("Conectando...", self.fontText,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
        pg.display.update()
        # pg.time.delay(1000)  
        self.gameState = 3
    
    def waitingMenu(self):
        self.screen.fill(AREIA)
        self.drawText("Esperando outros jogadores...", self.fontText,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
        pg.display.update()
        #pg.time.delay(4000)  
        self.gameState = 4

    def exitHandling(self):
        for event in self.eventList:
            if event.type == pg.QUIT:
                self.inGame = False
                self.gameState = -1
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.inGame = False
                    self.gameState = -1

def main():
    pg.init()
    pg.font.init() 
    pg.display.set_caption('Encouraçados')
    clock = pg.time.Clock()

    appRunning = True
    # Loop do jogo
    while appRunning:
        # Instancia um novo jogo    
        jogo = Jogo()
        while jogo.inGame:
            jogo.eventList = pg.event.get()
            #MENU
            if jogo.gameState == 0:
                jogo.playMenu()
                clock.tick(60)
            #NOME
            if jogo.gameState == 1:
                jogo.nameMenu()
                clock.tick(60)
            #CONECTANDO
            if jogo.gameState == 2:
                jogo.connectionMenu()
                clock.tick(60)
            #ESPERANDO JOGADORES
            if jogo.gameState == 3:
                jogo.waitingMenu()
                clock.tick(60)
            #JOGANDO
            if jogo.gameState == 4:
                if jogo.playersAlive > 0:
                    #for t in jogo.playerTanks:
                        #jogo.trataColisaoParede(t)
                    jogo.eventHandling()
                    jogo.update()
                    jogo.draw()
                    clock.tick(60)
                else: 
                    #jogo.victoryHandling()
                    pass
                    #pg.time.delay(5000) #espera por 5 segundos
            #update
            pg.display.update()
            jogo.exitHandling()
            
            
        # Checa se o jogo vai ser reiniciado
        if jogo.gameState == -1:
            appRunning = False

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
    Thread de jogo: ao fim da partida disponibiliza screen de vitoria/derrota e um botão de proxima partida
    Thread de jogo: quando clicado no botão, a conecxão dos cliente é reiniciada pareando novamente com o Server

    
Seguimento do Client:
    Client: Serve uma screen com o menu do jogo (botão jogar)
    LOOP do Cliente:
        Client: ao pressionar o botão, o jogador tentará se conectar ao servidor
        Client: quando uma partida começar, o cliente receberá as informações sobre o jogo para visualização e enviará os comandos do player
        Client: Ao termino do jogo, servira a screen de vitoria/derrota e diponibilizara o botão de jogar novamente
        Client: Ao enviar o botão de jogar novamente, tenta se reconectar com  servidor, reiniciando o loop

"""