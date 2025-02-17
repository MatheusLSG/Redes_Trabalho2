import sys
import pygame as pg
from desertwar import *
from network import Network

pg.init()
pg.font.init() 

screen = pg.display.set_mode((TELA_LARGURA, TELA_ALTURA))
fontText = pg.font.SysFont(TEXTO_FONTE, 32)
fontTitle = pg.font.SysFont(TEXTO_FONTE, 64,  bold=True, italic=True)

def draw(game: DesertWar):
    screen.fill(AREIA)
    game.map.draw(screen)  
    
    t: Tank
    for t in game.playerTanks:
        t.draw(screen)
    
    b: Bullet
    for t in game.playerTanks:
        for b in t.bulletGroup:
            b.draw(screen)
    
def victoryHandling(game: DesertWar):
    # Imprime text de vitoria
    winner = None
    
    for w in game.playerTanks:
        if w.dead == False:
            winner = w

    if winner:    
        text = winner.name + ' ganhou!'
        corT = winner.color
    else:
        text = 'Empate!'
        corT = BRANCO
        
    meiox = ((game.screenWidth)/2)
    meioy = ((game.screenHeight)/2)
    
    
    drawText(text,fontText,corT,PRETO,meiox,meioy)

    pg.display.update()
    
    game.inGame = 0
    
def drawText(text, fonte: pg.font.Font, textColor, shadowColor, x, y):
    ts =  fonte.render(text, False, shadowColor)
    t = fonte.render(text, False, textColor)

    cTx = t.get_width()/2
    cTy = t.get_height()/2

    screen.blit(ts, ( x-cTx+1, y-cTy+1 ))
    screen.blit(ts, ( x-cTx+1, y-cTy-1 ))
    screen.blit(ts, ( x-cTx-1, y-cTy+1 ))
    screen.blit(ts, ( x-cTx-1, y-cTy-1 ))
    screen.blit(t, ( x-cTx, y-cTy ))

def playMenu(game: DesertWar):
    screen.fill(AREIA)
    
    drawText("Desert War", fontTitle, VERDE, PRETO, screen.get_width()/2, 128)
    
    if game.playButton.draw(screen):
        game.gameState = 1
        
    drawText("Jogar", fontTitle, PRETO, PRETO, game.playButton.rect.centerx, game.playButton.rect.centery)
    
    pg.display.update()

def nameMenu(game: DesertWar):
    
    for event in game.eventList: 

        if event.type == pg.QUIT: 
            game.inGame = False
            game.gameState = -1
            break

        if event.type == pg.MOUSEBUTTONDOWN: 
            if game.nameBox.collidepoint(event.pos): 
                game.NBActive = True
            else: 
                game.NBActive = False

        if event.type == pg.KEYDOWN: 
            if event.key == pg.K_ESCAPE:
                game.inGame = False
                game.gameState = -1
                break
            
            if event.key == pg.K_SPACE:
                continue
            
            if event.key == pg.K_RETURN: 
                if len(game.playerName)>0:
                    game.gameState = 2
                    
                    break
                continue

            if event.key == pg.K_BACKSPACE: 
                game.playerName = game.playerName[:-1] 
            elif len(game.playerName) <= 20: 
                game.playerName += event.unicode
    
    screen.fill(AREIA) 

    if game.NBActive: 
        cor = game.NBActiveColor 
    else: 
        cor = game.NBPassiveColor

    #"digite seu nome"
    instrucao = fontText.render("Digite seu nome:", False, PRETO)
    screen.blit(instrucao, (game.nameBox.centerx-instrucao.get_width()/2, game.nameBox.y-instrucao.get_height()-8))
    #desenha retangulo
    sombra = game.nameBox.copy()
    sombra.w = sombra.w + 4
    sombra.h = sombra.h + 4
    sombra.centerx = game.nameBox.centerx
    sombra.centery = game.nameBox.centery
    pg.draw.rect(screen, PRETO, sombra)
    pg.draw.rect(screen, cor, game.nameBox) 

    text = fontText.render(game.playerName, False, PRETO)
    #desenha nome
    screen.blit(text, (game.nameBox.centerx-text.get_width()/2, game.nameBox.centery-text.get_height()/2))
    
    #"Pressione 'Enter' para selecionar"
    instrucao = fontText.render("Pressione 'Enter' para selecionar", False, PRETO)
    screen.blit(instrucao, (game.nameBox.centerx-instrucao.get_width()/2, game.nameBox.y+instrucao.get_height()+8))
    
def connectionMenu(game: DesertWar):
    screen.fill(AREIA)
    drawText("Conectando...", fontText,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
    pg.display.update()
    # pg.time.delay(1000)  
    
def failToConnectMenu(game: DesertWar):
    screen.fill(AREIA)
    drawText("Falha na conexão...", fontText,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
    pg.display.update()
    pg.time.delay(1000)  
 
def lostConnectionMenu(game: DesertWar):
    screen.fill(AREIA)
    drawText("Conexão perdida...", fontText,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
    pg.display.update()
    pg.time.delay(1000)  

def waitingMenu(game: DesertWar):
    game.playerTanks[game.playerId].name = game.playerName
    screen.fill(AREIA)
    drawText("Esperando outros jogadores (" + str(game.playersConnected) + "/" + str(PLAYERS_QTD) + ")", fontText,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
    pg.display.update()
    #pg.time.delay(4000)  

def exitHandling(game: DesertWar):
    for event in game.eventList:
        if event.type == pg.QUIT:
            game.inGame = False
            game.gameState = -1
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                game.inGame = False
                game.gameState = -1


def main():
    server = None
    try:
        server = sys.argv[1]
    except:
        print("Erro na passagem de argumentos")
        sys.exit()
    
    pg.display.set_caption('Encouraçados')
    clock = pg.time.Clock()

    appRunning = True
    
    
    game: DesertWar
    
    # Loop do jogo
    while appRunning:
        # Instancia um novo jogo    
        game = DesertWar(-1)
        
        n = Network(server)
        while  game.inGame:
            game.eventList = pg.event.get()
            #MENU
            if game.gameState == 0:
                playMenu(game)
                clock.tick(60)
            #NOME
            if game.gameState == 1:
                nameMenu(game)
                clock.tick(60)
            #CONECTANDO
            if game.gameState == 2:
                connectionMenu(game)
                
                res = n.connect()
                
                if  res != None :
                    game.playerId = int(res)
                    game.gameState = 3
                else:
                    failToConnectMenu(game)
                    game.inGame = 0
                    
                clock.tick(60)
            #ESPERANDO JOGADORES
            if game.gameState == 3:
                waitingMenu(game)
                
                res =  n.sendStr("waiting")
                
                if res != None :
                   
                    if res == "start":                
                        p = game.playerTanks[game.playerId]
            
                        #Recebe atualizacoes    
                        g = n.sendObj( (p.name, p.pos, p.angle, p.bulletDict, False, p.dead, p.connected) )
                        
                        if g != None:
                            game.playerNetInfo = g
                        else:
                            lostConnectionMenu(game)
                            game.inGame = 0
                        
                        game.gameState = 4
                        
                    elif 0 <= int(res) <= 4:
                        game.playersConnected = int(res)
                
                else:
                    lostConnectionMenu(game)
                    game.inGame = 0
                    
                clock.tick(60)
            #JOGANDO
            if game.gameState == 4:
                res =  n.sendStr("ready")
                
                game.eventHandling()
                game.update()
                
                if res != None :
                    if res == "ok":                        
                        p = game.playerTanks[game.playerId]
                        #Computa disparo
                        shot = False
                        for evento in game.eventList:           
                            if evento.type == pg.KEYDOWN:
                                if (evento.key == pg.K_SPACE and 
                                    p.bulletQtd and 
                                    p.alive()  
                                ):
                                    shot = True
                        #Recebe atualizacoes    
                        g = n.sendObj( (p.name, p.pos, p.angle, p.bulletDict, shot, p.dead, p.connected) )
                        
                        if g != None:
                            game.playerNetInfo = g
                        else:
                            lostConnectionMenu(game)
                            game.inGame = 0
                    elif res == "end":
                        p = game.playerTanks[game.playerId]
                        #Computa disparo
                        shot = False
                        for evento in game.eventList:           
                            if evento.type == pg.KEYDOWN:
                                if (evento.key == pg.K_SPACE and 
                                    p.bulletQtd and 
                                    p.alive()  
                                ):
                                    shot = True
                        #Recebe atualizacoes    
                        g = n.sendObj( (p.name, p.pos, p.angle, p.bulletDict, shot, p.dead, p.connected) )
                        
                        if g != None:
                            game.playerNetInfo = g
                            game.eventHandling()
                            game.update()
                        else:
                            lostConnectionMenu(game)
                            game.inGame = 0
                            
                        game.gameState = 5
                    else:
                        lostConnectionMenu(game)
                        game.inGame = 0
                else:
                    lostConnectionMenu(game)
                    game.inGame = 0
                
                
                
                draw(game)
                
                clock.tick(60)
                                
            if game.gameState == 5:
                game.eventHandling()
                game.update()
                
                victoryHandling(game)
                n.disconnect()
                pg.time.delay(5000) #espera por 5 segundos
            
            #update
            pg.display.update()
            exitHandling(game)
            
            
        # Checa se o game vai ser reiniciado
        if game.gameState == -1:
            appRunning = False

        # Deleta instancia passada do jogo
        del(n)
        del(game)
        gc.collect()


if __name__ == '__main__':
    main()
    pg.quit()
    sys.exit()
