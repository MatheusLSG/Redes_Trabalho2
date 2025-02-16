
import pygame as pg
import sys
import gc

from button import Button
from player import Tank, Bullet
from map import Map, Block
from globals import *


#END

#print(pg.font.get_fonts())



class Encouracados(pg.sprite.Sprite):

    def __init__(self, id):
        #Inicializando variaveis
        self.id = id
        self.start = False
        self.gameState = 0
        self.inGame = True
        self.screenWidth = TELA_LARGURA 
        self.screenHeight =  TELA_ALTURA
        self.playersConnected = 1
        
        
        self.playerNetInfo: list[
                                tuple[
                                    str,        #NAME
                                    pg.Vector2, #POS
                                    float,      #ANGLE
                                    dict[int, bool], #BALAS
                                    bool,       #SHOT
                                    bool,       #DEAD
                                    bool        #CONNECTED
                                    ]]      
        self.playerNetInfo = list()
        #self.playerNetInfo = list(tuple(pg.Rect(0,0,0,0), 0, False))
        for i in range(PLAYERS_QTD):
            self.playerNetInfo.append(("", pg.Vector2(0,0), 0, dict(), False, False, True))
        
        self.allSpritesGroup = pg.sprite.Group()
        #Texto
        self.nameBox = pg.Rect(TELA_LARGURA/2-175, TELA_ALTURA/2-25, 350, 50)
        self.NBActiveColor = BRANCO
        self.NBPassiveColor = CINZA
        self.NBActive = False
        self.playerName = ''
        self.playerId = -1
        
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
                     "",
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
        
        self.playersAlive = 0
        # Trata eventos dos players  
        for i in range(len(self.playerTanks)):
            t = self.playerTanks[i]
            t.dead = self.playerNetInfo[i][5]
            # Trata morte
            if not self.playerNetInfo[i][6] or t.dead:
                t.dead = True
                t.kill()
            if t.alive() and t.dead == False:
                #Atualiza vivos
                self.playersAlive += 1        
                #Nome
                t.name = self.playerNetInfo[i][0]
                #Atualiza pos
                t.pos = self.playerNetInfo[i][1]
                t.angle = self.playerNetInfo[i][2]   
                #Verifica balas
                t.bulletDict = self.playerNetInfo[i][3]
                
                #Move
                if i == self.playerId :
                    t.move(self.map.mapGroup, pg.key.get_pressed())
                else:
                    t.move(self.map.mapGroup, None)   
                #Atira
                if (self.playerNetInfo[i][4] and 
                    t.bulletQtd and 
                    t.alive()
                ):
                    b = Bullet( t.bulletQtd-1,
                                self.bulletImg,
                                BALA_PROPORCAO,
                                BALA_VEL_LIN,
                                t
                                )
                    print(t.bulletDict, "|", t.bulletGroup  , "|", b.id  )
                    self.allSpritesGroup.add(b)

        b: Bullet
        # Trata dicionarios
        for g in self.playerBulletGroup:
            for b in g:
                if b.tank.bulletDict[b.id] == False:
                    b.remove(b.tank.bulletGroup)

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
                    t.dead = True
                    t.kill()
                    break
    
    def update(self):
        self.allSpritesGroup.update()



"""
--- Ideia principal ---

Seguimento do Server: 
    LOOP DO SERVER:
        Server: espera player 1 se conectar
            Server: serve uma sala vazia para player 1 com um aviso de espera de um novo jogador
        Server: espera player 2 se conectar
            Server: cria uma thread de game para ambos os players
        
Seguimento do Game:
    Thread de game: controla o game dos jogadores até o fim da partida
    Thread de game: ao fim da partida disponibiliza screen de vitoria/derrota e um botão de proxima partida
    Thread de game: quando clicado no botão, a conecxão dos cliente é reiniciada pareando novamente com o Server

    
Seguimento do Client:
    Client: Serve uma screen com o menu do game (botão jogar)
    LOOP do Cliente:
        Client: ao pressionar o botão, o jogador tentará se conectar ao servidor
        Client: quando uma partida começar, o cliente receberá as informações sobre o game para visualização e enviará os comandos do player
        Client: Ao termino do game, servira a screen de vitoria/derrota e diponibilizara o botão de jogar novamente
        Client: Ao enviar o botão de jogar novamente, tenta se reconectar com  servidor, reiniciando o loop

"""