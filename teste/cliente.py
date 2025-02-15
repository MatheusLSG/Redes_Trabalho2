import pygame as pg
from teste.rede import Rede
from teste.player import Player

largura = 500
altura = 500
tela = pg.display.set_mode((largura,altura))
pg.display.set_caption("Cliente")

def redesenharJanela(p: Player, p2: Player):
    tela.fill((255,255,255))
    p.draw(tela)
    p2.draw(tela)

    pg.display.update()

def main():
    rodando = True
    r = Rede()

    p:Player = r.getP()

    clock = pg.time.Clock()

    while rodando:
        clock.tick(60)

        p2 = r.enviar(p)
        
        p2.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                rodando = False
                
        p.mover()
        redesenharJanela(p, p2)
    
    pg.quit()
                
main()