import pygame as pg
from globals import *
import pandas as pd

class Map():
    
    def __init__(self,
                 blockImage: pg.Surface,
                 mapDataPath: str,
                 ):
        # Inicializando variaveis
        df = pd.read_excel(mapDataPath, sheet_name=0, header=None)
        self.data = df.to_numpy()
        
        linQtd = len(self.data)
        if linQtd > 0: 
            colQtd = len(self.data[0])
        
        self.mapGroup = pg.sprite.Group()    
    
        self.blocks: list[list[Block]]
        self.blocks = [ [ [ ] for __ in range(colQtd) ] for _ in range(linQtd) ]

        self.blockImg = blockImage
        
        for y in range(linQtd):
            for x in range(colQtd):
                if self.data[y][x] == 1:
                    bk = Block( self.blockImg , (x, y))
                    self.blocks[y][x] = bk
                    self.mapGroup.add(bk)
                    
        #print(self.data)
    def draw(self, surface: pg.surface):
        self.mapGroup.draw(surface)
        
class Block(pg.sprite.Sprite):
    def __init__(self, 
                 image: pg.Surface, 
                 iniPos: tuple[int, int]):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.widht = self.image.get_width() 
        self.height = self.image.get_height()
        self.image = pg.transform.scale(self.image, ( self.widht , self.height))
        self.rect = self.image.get_rect(x=(iniPos[0]*self.widht),y=iniPos[1]*self.height)
        self.mask = pg.mask.from_surface(self.image)