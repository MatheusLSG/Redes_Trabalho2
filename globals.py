import pygame as pg

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

#PLayes
PLAYERS_QTD = 2

#
INI_POS_P = [
            (64,352),
            (896,352),
            (480,64),
            (480,640)
            ]

INI_ANG_P = [
            0,
            180,
            -90,
            90
            ]

SPRITE_P_PATH = [
                "sprites/jogador/tanqueJogador1.png", 
                "sprites/jogador/tanqueJogador2.png", 
                "sprites/jogador/tanqueJogador3.png", 
                "sprites/jogador/tanqueJogador4.png"
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
TANQUE_TIRO_QTD = 1
TANQUE_TIRO_CD = 1000 #em ms

SPRITE_BALA_PATH = "sprites/bala/bala.png"


SPRITE_BLOCO_PATH = "sprites/mapa/bloco.png"

BALA_SPRITE_LARGURA = 8
BALA_SPRITE_ALTURA = 16
BALA_PROPORCAO = 0.5

BALA_VEL_LIN = 5

BALA_TEMPO_DE_VIDA = 1000 #em ms

TEXTO_FONTE = 'comicsansms' 

TANQUE_SPRITE_LARGURA = 64
TANQUE_SPRITE_ALTURA = 64
TANQUE_PROPORCAO = 0.5

MAP_DATAPATH = "mapas/mapa.xlsx"

