
import pygame as pg

class Button():
    def __init__(self,x,y,image: pg.surface.Surface, scale):
        width = image.get_width() 
        height = image.get_height()
        self.image = pg.transform.scale(image,(int(width*scale),int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.isClicked = False

    def draw(self, screen: pg.surface.Surface):
        clicked = False

        pos = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and not self.isClicked:
                self.isClicked = True
                clicked = True
        
        if pg.mouse.get_pressed()[0] == 0:
                self.isClicked = False

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return clicked