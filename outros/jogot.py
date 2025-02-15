
import pygame as pg
import sys
import pandas as pd
import gc
import outros.botao as botao
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


BTJOGAR_SPRITE_PATH = "sprites/botoes/botaoJogar.png"

#Cores
PRETO = (0,0,0)
BRANCO = (255,255,255)

CINZA = (127,127,127)

AZUL = (0,100,255)
LARANJA = (255,100,0)
ROXO = (158, 0, 235)
VERDE = (66, 224, 0)
AREIA = (255, 247, 193)

PLAYERS_QTD = 4

#
INI_POS_P = [
            (64,352),
            (896,352),
            (480,64),
            (480,640)
            ]

INI_ANG_P = [
            -90, 
            90,
            180,
            0
            ]

SPRITE_P_PATH = [
                "sprites/jogador/tanqueJogador1.png", 
                "sprites/jogador/tanqueJogador2.png", 
                "sprites/jogador/tanqueJogador3.png", 
                "sprites/jogador/tanqueJogador4.png"
                ]

INPUTS_P = [
            (pg.K_a, pg.K_d, pg.K_w, pg.K_s, pg.K_SPACE), 
            (pg.K_KP4, pg.K_KP6, pg.K_KP8, pg.K_KP5, pg.K_KP_ENTER),
            (pg.K_f, pg.K_h, pg.K_t, pg.K_g, pg.K_n),
            (pg.K_j, pg.K_l, pg.K_i, pg.K_k, pg.K_PERIOD),
            ]
TEXTO_VITORIA_P = [
                    'Player 1 Venceu!',
                    'Player 2 Venceu!',
                    'Player 3 Venceu!',
                    'Player 4 Venceu!'
                    ]
COR_VITORIA_P = [
                    AZUL,
                    LARANJA,
                    VERDE,
                    ROXO
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
        self.estado = 0
        self.rodando = True
        self.telaLargura = TELA_LARGURA 
        self.telaAltura =  TELA_ALTURA
        self.textoFonte = pg.font.SysFont(TEXTO_FONTE, 30)
        
        self.tela = pg.display.set_mode((self.telaLargura, self.telaAltura))
        
        self.grupoSpritesTodos = pg.sprite.Group()
        #Texto
        self.caixaDeTexto = pg.Rect(TELA_LARGURA/2-175, TELA_ALTURA/2-25, 350, 50)
        self.CDTCorAtiva = BRANCO
        self.CDTCorPassiva = CINZA
        self.CDTcorAtual = BRANCO 
        self.CDTAtivo = False
        self.nomePlayer = ''
        
        #Botoes
        btImagem = pg.image.load(BTJOGAR_SPRITE_PATH)
        btY = TELA_ALTURA/2
        btX = TELA_LARGURA/2
        
        self.botaoJogar = botao.Botao(btX,btY,btImagem,2)

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
                self.estado = -1
                return
            if evento.type == pg.KEYDOWN:
                if evento.key == pg.K_ESCAPE:
                    self.rodando = False
                    self.estado = -1
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
                if tanque.vaiColidirAll:
                    break
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
                    
                    #LADOS
                    if(colB and colC and colD):#D
                        if not tanque.vaiColidirD:
                                tanque.pos.x -= absXVel/2
                                tanque.vaiColidirD = 1
                    
                    if(colB and colC and colE):#E
                        if not tanque.vaiColidirE:
                                tanque.pos.x += absXVel/2
                                tanque.vaiColidirE = 1

                    if(colB and colE and colD):#B
                        if not tanque.vaiColidirB:
                                tanque.pos.y -= absYVel/2
                                tanque.vaiColidirB = 1

                    if(colC and colE and colD):#C
                        if not tanque.vaiColidirC:
                                tanque.pos.y += absYVel/2
                                tanque.vaiColidirC = 1                    

                    #CANTOS
                    if(colD and colC):#DC
                        if not tanque.vaiColidirD :
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1
                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1
                    
                    if(colD and colB):#DB
                        if not tanque.vaiColidirD:
                            tanque.pos.x -= absXVel/2
                            tanque.vaiColidirD = 1
                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1
                    
                    if(colE and colC):#EC
                        if not tanque.vaiColidirE:
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1
                        if not tanque.vaiColidirC:    
                            tanque.pos.y += absYVel/2
                            tanque.vaiColidirC = 1
                            
                    if(colE and colB):#EB 
                        if not tanque.vaiColidirE:      
                            tanque.pos.x += absXVel/2
                            tanque.vaiColidirE = 1
                        if not tanque.vaiColidirB:   
                            tanque.pos.y -= absYVel/2
                            tanque.vaiColidirB = 1


                    
                        
                        
        if tanque.vaiColidirB and tanque.vaiColidirC and tanque.vaiColidirE and tanque.vaiColidirD:
            tanque.vaiColidirAll = 1

    def trataVitoria(self):
        # Imprime texto de vitoria
  
        vencedor = self.tanquePlayers[0]

        texto = vencedor.textoVitoria
        
        meiox = ((self.telaLargura)/2)
        meioy = ((self.telaAltura)/2)
        
        corT = vencedor.corVitoria

        self.desenhaTexto(texto,self.textoFonte,corT,PRETO,meiox,meioy)

        pg.display.update()
        
        self.rodando = 0
        
        
        
    def desenhaTexto(self, texto, fonte: pg.font.Font, corTexto, corSombra, x, y):
        ts =  fonte.render(texto, False, corSombra)
        t = fonte.render(texto, False, corTexto)

        cTx = t.get_width()/2
        cTy = t.get_height()/2

        self.tela.blit(ts, ( x-cTx+1, y-cTy+1 ))
        self.tela.blit(ts, ( x-cTx+1, y-cTy-1 ))
        self.tela.blit(ts, ( x-cTx-1, y-cTy+1 ))
        self.tela.blit(ts, ( x-cTx-1, y-cTy-1 ))
        self.tela.blit(t, ( x-cTx, y-cTy ))

    def rodaMenuJogar(self):
        self.tela.fill(AREIA)
        if self.botaoJogar.draw(self.tela):
            self.estado = 1

    def rodaMenuNome(self):
        
        for event in pg.event.get(): 
    
            if event.type == pg.QUIT: 
                self.rodando = False
                self.estado = -1
                break

            if event.type == pg.MOUSEBUTTONDOWN: 
                if self.caixaDeTexto.collidepoint(event.pos): 
                    self.CDTAtivo = True
                else: 
                    self.CDTAtivo = False
    
            if event.type == pg.KEYDOWN: 
                if event.key == pg.K_ESCAPE:
                    self.rodando = False
                    self.estado = -1
                    break
                
                if event.key == pg.K_SPACE:
                    continue
                
                if event.key == pg.K_RETURN: 
                    if len(self.nomePlayer)>0:
                        self.estado = 2
                        self.tanquePlayers[0].textoVitoria = self.nomePlayer + ' Ganhou!'
                        break
                    continue

                if event.key == pg.K_BACKSPACE: 
                    self.nomePlayer = self.nomePlayer[:-1] 
                elif len(self.nomePlayer) <= 20: 
                    self.nomePlayer += event.unicode
        
        self.tela.fill(AREIA) 
    
        if self.CDTAtivo: 
            cor = self.CDTCorAtiva 
        else: 
            cor = self.CDTCorPassiva

        #"digite seu nome"
        instrucao = self.textoFonte.render("Digite seu nome:", False, PRETO)
        self.tela.blit(instrucao, (self.caixaDeTexto.centerx-instrucao.get_width()/2, self.caixaDeTexto.y-instrucao.get_height()-8))
        #desenha retangulo
        sombra = self.caixaDeTexto.copy()
        sombra.w = sombra.w + 4
        sombra.h = sombra.h + 4
        sombra.centerx = self.caixaDeTexto.centerx
        sombra.centery = self.caixaDeTexto.centery
        pg.draw.rect(self.tela, PRETO, sombra)
        pg.draw.rect(self.tela, cor, self.caixaDeTexto) 
    
        texto = self.textoFonte.render(self.nomePlayer, False, PRETO)
        #desenha nome
        self.tela.blit(texto, (self.caixaDeTexto.centerx-texto.get_width()/2, self.caixaDeTexto.centery-texto.get_height()/2))
        
        #"Pressione 'Enter' para selecionar"
        instrucao = self.textoFonte.render("Pressione 'Enter' para selecionar", False, PRETO)
        self.tela.blit(instrucao, (self.caixaDeTexto.centerx-instrucao.get_width()/2, self.caixaDeTexto.y+instrucao.get_height()+8))
        
        
       
    def rodaMenuConectando(self):
        
        self.tela.fill(AREIA)
        self.desenhaTexto("Conectando...", self.textoFonte,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
        pg.display.update()
        pg.time.delay(1000)  
        self.estado = 3
    
    def rodaMenuEsperando(self):
        self.tela.fill(AREIA)
        self.desenhaTexto("Esperando outros jogadores...", self.textoFonte,BRANCO,PRETO,TELA_LARGURA/2,TELA_ALTURA/2)      
        pg.display.update()
        pg.time.delay(4000)  
        self.estado = 4

    def trataSaida(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.rodando = False
                self.estado = -1
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.rodando = False
                    self.estado = -1

def main():
    pg.init()
    pg.font.init() 
    pg.display.set_caption('Encouraçados')
    clock = pg.time.Clock()

    clienteRodando = True


   

    # Loop do jogo
    while clienteRodando:
        # Instancia um novo jogo    
        jogo = Jogo()
        while jogo.rodando:
            if jogo.estado == 0:#MENU
                
                jogo.rodaMenuJogar()
                jogo.trataSaida()

                clock.tick(60)

            if jogo.estado == 1:#NOME
                jogo.rodaMenuNome()

                clock.tick(60)
            
            if jogo.estado == 2:#CONECTANDO
                jogo.rodaMenuConectando()
                jogo.trataSaida()

                clock.tick(60)
            
            if jogo.estado == 3:#ESPERANDO JOGADORES

                jogo.rodaMenuEsperando()
                jogo.trataSaida()

                clock.tick(60)

            if jogo.estado == 4:#JOGANDO
                if jogo.tanquesVivos > 1:
                    for t in jogo.tanquePlayers:
                        jogo.trataColisaoParede(t)
                    jogo.trataEventos()
                    jogo.trataSaida()
                    jogo.update()
                    jogo.draw()
                    clock.tick(60)
                else: 
                    jogo.trataVitoria()
                    pg.time.delay(5000) #espera por 5 segundos

            pg.display.update()

        # Checa se o jogo vai ser reiniciado
        if jogo.estado == -1:
            clienteRodando = False

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