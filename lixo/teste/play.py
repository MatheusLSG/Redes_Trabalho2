import pygame as pg

class Player():
    def __init__(self, x, y, largura, altura, cor):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.cor = cor
        self.rect = (x,y,largura,altura)
        self.vel = 3

    def draw(self, tela):
        pg.draw.rect(tela, self.cor, self.rect)

    def mover(self):
        teclas = pg.key.get_pressed()

        if teclas[pg.K_a]:
            self.x -= self.vel
        
        if teclas[pg.K_d]:
            self.x += self.vel
        
        if teclas[pg.K_w]:
            self.y -= self.vel

        if teclas[pg.K_s]:
            self.y += self.vel
        
        self.update()

    def update(self): 
        self.rect = (self.x, self.y, self.largura, self.altura)