
import pygame as pg

class Botao():
    def __init__(self,x,y,imagem: pg.surface.Surface, escala):
        largura = imagem.get_width() 
        altura = imagem.get_height()
        self.image = pg.transform.scale(imagem,(int(largura*escala),int(altura*escala)))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.clicado = False

    def draw(self, tela: pg.surface.Surface):
        clicou = False

        pos = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and not self.clicado:
                self.clicado = True
                clicou = True
        
        if pg.mouse.get_pressed()[0] == 0:
                self.clicado = False

        tela.blit(self.image, (self.rect.x, self.rect.y))

        return clicou