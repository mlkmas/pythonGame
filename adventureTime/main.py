import random
import math
from tkinter import Image
from typing import Any
import pygame
import os
from os import listdir
from os.path import isfile, join
from PIL import Image
pygame.init()

pygame.display.set_caption("AdventureTime")

WIDTH, HEIGHT= 1000, 600
WHITE=(255,255,255)
BG_COLOR=WHITE
PLAYER_VEL=5

#to control the frame rate(speed) across different devices
FPS= 60  
window=pygame.display.set_mode((WIDTH,HEIGHT))

def flip(sprites):
    return [pygame.transform.flip( sprite, True,False) for sprite in sprites]

def loadSpriteSheets(dir1, dir2, width, height, direction=False):
    path=join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    allSprites={}

    for image in images:
        spriteSheet= pygame.image.load(join(path, image)).convert_alpha()

        sprites=[]
        for i in range( spriteSheet.get_width()// width):
            surface=pygame.Surface((width, height), pygame.SRCALPHA,32) #SRCALPHA Returns a set of current Surface features
            # rect: to tell us where in this image, an image being the sprite sheet that we want to take indevisual image from and blit it on the screen
            rect=pygame.Rect(i* width,0,width,height)
            surface.blit(spriteSheet,(0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))
            #we have stripped out all the individual frames and scaled them up double there size 

        if direction:
            allSprites[image.replace(".png","")+ "_right"]=sprites
            allSprites[image.replace(".png","")+ "_left"]=flip(sprites) 
        else:
            allSprites[image.replace(".png","")]=sprites  
    return allSprites             

def getBlock(size):
    path=join("assets", "Terrain","Terrain.png")
    image=pygame.image.load(path).convert_alpha()
    surface=pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect=pygame.Rect(96,0,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

#we used sprite.Sprite because it allows special paging methods to use those properties to handle the collision
class Player(pygame.sprite.Sprite):
   
    COLOR=(255,0,0)
    GRAVITY= 1
    ANIMATION_DELAY=3
    
   
    SPRITES= loadSpriteSheets("MainCharacters","MaskDude",32,32,True)
    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect=pygame.Rect(x,y,width,height) #rect to store the indivisual values to make it easier to handle
        self.xVel=0
        self.yVel=0
        self.mask=None
        self.direction= "left"
        self.animationCount=0
        self.fallCount=0
        self.jumpCount=0
        self.hit=False
        self.hitCount=0
    
    def jump(self):
        self.yVel= -self.GRAVITY*8 # 8 the speed of the jump
        self.animationCount=0
        self.jumpCount+=1
        if self.jumpCount==1:
           self.fallCount=0

    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y +=dy

    def makeHit(self):
        self.hit=True
        self.hitCount=0  

    def moveLeft(self,vel):
        self.xVel= -vel 
        if self.direction != "left":
            self.direction="left"
            self.animationCount=0

    def moveRight(self,vel):
        self.xVel= vel 
        if self.direction != "right":
            self.direction="right"
            self.animationCount=0

    def loop(self, fps):
        self.yVel+=min(1, (self.fallCount/fps)* self.GRAVITY)
        self.move(self.xVel,self.yVel)
        if self.hit:
            self.hitCount+=1
        if self.hitCount>fps*2  : 
           self.hit=False 
           self.hitCount=0

        self.fallCount+=1
        self.updateSprite()
    
    def landed(self):
        self.fallCount=0
        self.yVel=0
        self.jumpCount=0

    def hitHead(self):
        self.count=0
        self.yVel*= -1    

    def updateSprite(self):
        spriteSheet="idle"
        if self.hit:
            spriteSheet="hit" 
        elif self.yVel <0:
            if self.jumpCount==1:
               spriteSheet="jump"
            elif self.jumpCount==2:
                spriteSheet="double_jump"
        elif self.yVel>self.GRAVITY*2:
            spriteSheet="fall"          
        elif self.xVel!=0:
            spriteSheet="run"

        spriteSheetName= spriteSheet +"_"+ self.direction
        sprites= self.SPRITES[spriteSheetName]    
        spriteIndex=(self.animationCount//self.ANIMATION_DELAY) % len(sprites)
        self.sprite=sprites[spriteIndex]
        self.animationCount+=1
        self.update()
    
    def update(self):
        self.rect=self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        #mask tell us where there is pixels so we can overlap it with another mask and make 
        # sure that 2 objects are colliding if the pixels of the image not the rect box of the chracters
        self.mask=pygame.mask.from_surface(self.sprite)

    def draw(self, win,offsetX):
        #pygame.draw.rect(win, self.COLOR,self.rect)
        #self.sprite=self.SPRITES["idle_"+ self.direction][0]
        win.blit(self.sprite, (self.rect.x-offsetX, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__() #initialize the superClass(object)
        self.rect=pygame.Rect(x,y,width,height)
        self.image=pygame.Surface((width,height),pygame.SRCALPHA)
        self.width=width
        self.height=height
        self.name=name

    def draw(self,win,offsetX):
        win.blit(self.image,(self.rect.x-offsetX,self.rect.y))

class Block(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block=getBlock(size)
        self.image.blit(block, (0,0))
        self.mask=pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY=3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire=loadSpriteSheets("Traps","Fire",width,height)
        self.image=self.fire["off"][0]
        self.mask=pygame.mask.from_surface(self.image)
        self.animationCount=0
        self.animationName="off"

    def on(self):
        self.animationName="on"

    def off(self):
        self.animationName="off"

    def loop(self):
        sprites= self.fire[self.animationName]    
        spriteIndex=(self.animationCount//self.ANIMATION_DELAY) % len(sprites)
        self.image=sprites[spriteIndex]
        self.animationCount+=1
        self.rect=self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask=pygame.mask.from_surface(self.image)

        if self.animationCount //self.ANIMATION_DELAY >len(sprites):
            self.animationCount=0





# the name of the bg img i want to load
def getBackground(name):
    #we have to join the axact name of the files in the dir we ant to include the img from 
    image = pygame.image.load(join("assets","Background",name))
    # _,_ is that some x and y values i dont care about
    #get_rect: get the rect surface of the surface/img
    _,_, width,height=image.get_rect() 
    tiles= []
    # to get the accurate position to fill the bg tiles
    for i in range(WIDTH // width+1): 
        for j in range(HEIGHT // height +1) :
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image

def draw(window,background, bgImage,player,objects,offsetX):
    for tile in background:
        window.blit(bgImage, tile)
    for obj in objects:
        obj.draw(window,offsetX)

    player.draw(window,offsetX)
    pygame.display.update()

def handleVerticalCollision(player,objects,dy):
    collidedObjects=[]
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy>0:
                player.rect.bottom=obj.rect.top
                player.landed()
            elif dy<0:
                player.rect.top=obj.rect.bottom
                player.hitHead()

            collidedObjects.append(obj)

    return collidedObjects            

def collide(player, objects,dx):
    player.move(dx,0)
    player.update()
    collidedObject=None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collidedObject=obj
            break

    player.move(-dx,0)
    player.update()
    return collidedObject    


def handleMove(player,objects):
    keys =pygame.key.get_pressed()
    
    player.xVel=0
    collideLeft=collide(player,objects, -PLAYER_VEL*2)
    collideRight=collide(player,objects,PLAYER_VEL*2)

    if keys[pygame.K_LEFT]and not collideLeft:
        player.moveLeft(PLAYER_VEL)
    if keys[pygame.K_RIGHT]and not collideRight:
        player.moveRight(PLAYER_VEL)  

    verticalCollide=handleVerticalCollision(player,objects,player.yVel)  
    toCheck=[collideLeft,collideRight,*verticalCollide]
    for obj in toCheck:
        if obj and obj.name == "fire":
            player.makeHit()


def main(window):
    clock = pygame.time.Clock()
    background, bgImage = getBackground("blue.jpg")
    blockSize=96
    player= Player(100, 100, 50, 50) 
    fire=Fire(100,HEIGHT-blockSize-64,16,32)
    fire.on()
    floor=[Block(i*blockSize,HEIGHT-blockSize,blockSize)for i in range(-WIDTH//blockSize,WIDTH*2//blockSize)]
  
    #it breaks this floor into all its indivisual and passes theam inside of the list 
    objects=[*floor,Block(0,HEIGHT-blockSize*2,blockSize),Block(blockSize*3 ,HEIGHT-blockSize*4,blockSize),fire]

    offsetX=0
    scrollAreaWidth=200    
    run=True
   
    while run:
        clock.tick(FPS) #to control the frame rate(speed) across different devices
        for event in pygame.event.get():
            if event.type ==pygame.QUIT:
               run=False
               break
            
             #if we do the jump in handle move when the user press the jump key
             #and keep holding it down the character is going to keep jumping a 
             # bunch of times(we handled the left and right in handle move func)
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE and player.jumpCount< 2:
                    player.jump()
        
        player.loop(FPS)
        fire.loop()
        handleMove(player,objects)
        draw(window, background, bgImage, player,objects,offsetX)
        
        #when we get to the scrollAreaWidth the window start scrolling
        if((player.rect.right-offsetX >= WIDTH-scrollAreaWidth) and player.xVel>0)or(
            (player.rect.left-offsetX <= scrollAreaWidth) and player.xVel<0):
            offsetX+=player.xVel
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)




