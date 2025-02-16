import pygame as pg
import math

class Tank(pg.sprite.Sprite):
    def __init__(self, 
                 image: pg.Surface, 
                 scale: float,
                 iniPos: tuple[int, int], 
                 velLin: int,
                 iniAng: int, 
                 velAng: int,
                 bulletQtd: int,
                 bulletCd: int,
                 name: str, 
                 color: tuple[int, int, int]):
        # Inicializando variaveis
        pg.sprite.Sprite.__init__(self)
        
        self.image = image
        self.width = self.image.get_width()*scale
        self.height = self.image.get_height()*scale
        self.image = pg.transform.scale(self.image, (self.width , self.height))
        self.org_image = self.image.copy()
        self.rect = self.image.get_rect(center=iniPos)
        
        self.angle = iniAng
        self.velAng = velAng
        self.dir = pg.Vector2((1,0))
        self.pos = pg.Vector2(self.rect.center)
        self.velLin = velLin
        
        self.bulletGroup = pg.sprite.Group() 
        self.bulletQtd = bulletQtd
        self.bulletCd = bulletCd

        self.name = name
        self.color = color
        
        self.mask = pg.mask.from_surface(self.image)
        
    def move(self, colisors: pg.sprite.Group):
        teclas = pg.key.get_pressed()

        #ANGULO
        if teclas[pg.K_a]:
            self.angle = (self.angle+self.velAng)%360
            
        if teclas[pg.K_d]:
            self.angle = (self.angle-self.velAng)%360

        self.dir = pg.Vector2(1, 0).rotate(-self.angle)
        
        rotImage = pg.transform.rotate(self.org_image, self.angle)
        newRect = rotImage.get_rect(center = self.image.get_rect(center = (self.pos.x, self.pos.y)).center)

        self.image = rotImage
        self.rect = newRect     
        self.mask = pg.mask.from_surface(self.image)   
        
        #MOVIMENTO
        if teclas[pg.K_w]:
            self.pos += self.velLin*self.dir
          
        if teclas[pg.K_s]:
            self.pos -= self.velLin*self.dir
        
        #CHECA COLISOES

        rotImage = pg.transform.rotate(self.org_image, self.angle)
        newRect = rotImage.get_rect(center = self.image.get_rect(center = (self.pos.x, self.pos.y)).center)

        self.image = rotImage
        self.rect = newRect 
        
        tr = self.rect
        
        for c in pg.sprite.spritecollide(self, colisors, False):
            if pg.sprite.spritecollide(self, colisors, False, pg.sprite.collide_mask):
                br: pg.Rect
                br = c.rect
                vet: pg.Vector2
                vet = pg.Vector2(0,0)
                
                red = 0.5
                
                #bloco dentro verticalmente
                if(tr.top <= br.centery <= tr.bottom):
                    #bloco a esquerda
                    if(tr.left >= br.centerx):
                        vet = pg.Vector2((tr.left-br.centerx, 0))                
                    #bloco a direita
                    else:
                        vet = pg.Vector2((tr.right-br.centerx, 0))                
                
                #bloco dentro horizontalmente
                elif(tr.left <= br.centerx <= tr.right):
                    #bloco a cima
                    if(tr.top >= br.centery):
                        vet = pg.Vector2((0, tr.top-br.centery))                
                    #bloco a baixo
                    else:
                        vet = pg.Vector2((0, tr.bottom-br.centery))                
                
                #bloco a cima
                elif(tr.top >= br.centery):
                    #bloco a esquerda
                    if(tr.left >= br.centerx):
                        vet = pg.Vector2(tr.topleft[0]- br.center[0], tr.topleft[1]-br.center[1])
                        #red = 0.35
                    #bloco a direita
                    elif(tr.right <= br.centerx):
                        vet = pg.Vector2(tr.topright[0]- br.center[0], tr.topright[1]-br.center[1])
                        #red = 0.35
                #bloco a baixo
                elif(tr.bottom <= br.centery):
                    #bloco a esquerda
                    if(tr.left >= br.centerx):
                        vet = pg.Vector2(tr.bottomleft[0]- br.center[0], tr.bottomleft[1] -br.center[1])
                        #red = 0.35
                    #bloco a direita
                    elif(tr.right <= br.centerx):        
                        vet = pg.Vector2(tr.bottomright[0] - br.center[0], tr.bottomright[1] -br.center[1])
                        #red = 0.35
                
                print("")
                #calcular minivetor
                print("vet: ", vet)
                ang =  vet.angle_to(pg.Vector2(1,0))
                
                print("ang: ",ang)
                
                tg = math.tan( math.radians(ang) )
                if 0.85 <= tg or -0.85 >= tg:
                    red = 0.25
                print("tg: ",tg)
                
                absX = abs(vet.x)
                absY = abs(vet.y)
                
                print("absX: ",absX)
                print("absY: ",absY)
    
                print("w: ",br.w)
                print("h: ",br.h)
                
                reductX = br.w/2 - absX 
                reductY = br.h/2 - absY 
                
                print("reductX: ",reductX)
                print("reductY: ",reductY)
                #X
                if(reductX <= reductY):
                    reductY = reductX*tg
                #Y
                else:
                    reductX = reductY/tg
                
                reductV = pg.Vector2(reductX*math.copysign(1, vet.x), reductY*math.copysign(1, vet.y))
                
                print(reductV)
                
                self.pos += reductV*red #red age como um redutor no impacto da colisao
            
          
                #MUDA POSICAO
                
                newRect = self.image.get_rect(center = self.image.get_rect(center = (self.pos.x, self.pos.y)).center)

                self.rect = newRect     
                self.mask = pg.mask.from_surface(self.image)   

  
    def draw(self, surface: pg.Surface):
        surface.blit(self.image, dest=self.rect)

class Bullet(pg.sprite.Sprite):
    
    def __init__(self,
                 image: pg.Surface,
                 scale: float,
                 vel: int,
                 tank: Tank
                 ):
         # Inicializando variaveis
        pg.sprite.Sprite.__init__(self)
        
        self.image = image
        
        self.tank = tank
        self.tank.bulletQtd -= 1
        
        self.angle = tank.angle
        
        self.image = pg.transform.scale(self.image, (self.image.get_width()*scale, self.image.get_height()*scale))
        self.image = pg.transform.rotate(self.image, self.angle)

        tcx = tank.rect.centerx
        tcy = tank.rect.centery
        tw = tank.width
        th = tank.height
        
        self.rect = self.image.get_rect(center=(tcx,tcy))

        vec = pg.Vector2(1,0).rotate(-self.angle) 
               
        self.pos = pg.Vector2(self.rect.center)
        self.vel = vel
        self.dir = vec
        
        offset = pg.Vector2()
        offset.x = (tw/2)*vec.x  
        offset.y = (th/2)*vec.y
        
        self.pos += offset
        
        self.lifeTime = pg.time.get_ticks()

        
    def update(self):
        self.pos += self.dir*self.vel
        
        novoRetangulo = self.image.get_rect(center = self.image.get_rect(center = (self.pos.x, self.pos.y)).center)

        self.rect = novoRetangulo

        if pg.time.get_ticks() - self.lifeTime >= self.tank.bulletCd:
            self.remove(self.groups())
            self.destroi()
            
    def draw(self, surface: pg.Surface):        
        surface.blit(self.image, dest=self.rect)

    def destroi(self):
        self.tank.bulletQtd += 1
        self.kill()
        del(self)
