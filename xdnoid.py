# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 02:53:11 2017

@author: Karol
"""

import pygame, sys, math, random

WINDOW_SIZE = 800, 600
MAX_ANGLE = math.radians(75)

S_MENU = 0
S_PLAY = 1
S_LVLCMPL = 2
S_WIN = 3
S_GAMEOVER = 4

class Paddle:
    def __init__(self, image, height):
        self.image = image
        self.rect = image.get_rect()
        self.pos = self.rect.move(WINDOW_SIZE[0]/2-self.rect.centerx, 
                                   WINDOW_SIZE[1]-(height+self.rect.h))
        
    def movePad(self, xpos):
        self.pos = self.rect.move(xpos-self.rect.centerx, self.pos[1])
        
class Ball:
    def __init__(self, image, pos):
        self.image = image
        self.rect = image.get_rect()
        self.pos = self.rect.move(pos)
        
    def moveBall(self, vx, vy):
        self.pos = self.pos.move((vx, vy))
        
class Block:
    def __init__(self, image, pos, hp=1):
        self.image = image
        self.rect = image.get_rect()
        self.pos = self.rect.move(pos)
        self.hp = hp
        
class Powerup:
    def __init__(self, image, pos, action):
        self.image = image
        self.rect = image.get_rect()
        self.pos = self.rect.move((pos.centerx, pos.centery))
        self.action = action
        
    def movePowerup(self, vy):
        self.pos = self.pos.move((0, vy))
        
class Game:
    def __init__(self):
        pygame.init()
        random.seed()
        
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("xDnoid")
        
        self.clock = pygame.time.Clock()
        
        if pygame.font:
            self.font = pygame.font.Font('font/UbuntuMono-B.ttf', 30)
            self.crFont = pygame.font.Font('font/UbuntuMono-R.ttf', 18)
        else:
            self.font = None
            self.crFont = None
        
        self.paddleImage = pygame.image.load('sprites/paddle_red.png')
        self.paddleLongImage = pygame.image.load('sprites/paddle_blue_long.png')
        self.ballImage = pygame.image.load('sprites/ball.png')
        self.background = []
        self.background.append(pygame.image.load('bg/black.png').convert())
        self.background.append(pygame.image.load('bg/bglvl1.png').convert())
        self.background.append(pygame.image.load('bg/bglvl2.png').convert())
        self.background.append(pygame.image.load('bg/bglvl3.png').convert())
        self.background.append(pygame.image.load('bg/blackui.png').convert())
        self.blockImage = []
        self.blockImage.append(pygame.image.load('sprites/block_blue.png'))
        self.blockImage.append(pygame.image.load('sprites/block_green.png'))
        self.blockImage.append(pygame.image.load('sprites/block_purple.png'))
        self.blockImage.append(pygame.image.load('sprites/block_red.png'))
        self.blockImage.append(pygame.image.load('sprites/block_yellow.png'))
        self.blockImage.append(pygame.image.load('sprites/block_grey.png'))
        self.blockImage.append(pygame.image.load('sprites/block_grey_destr.png'))
        self.powerupImage = []
        self.powerupImage.append(pygame.image.load('sprites/powerup_green.png'))
        self.powerupImage.append(pygame.image.load('sprites/powerup_purple.png'))
        self.powerupImage.append(pygame.image.load('sprites/powerup_yellow.png'))
        self.powerupImage.append(pygame.image.load('sprites/powerup_red.png'))
        self.powerupImage.append(pygame.image.load('sprites/powerup_blue.png'))
        self.logoImage = pygame.image.load('ui/logo.png')
        
        self.level = 0
        self.state = S_MENU
        
    def startGame(self):
        pygame.mouse.set_pos([WINDOW_SIZE[0]/2, pygame.mouse.get_pos()[1]])
        self.paddle = Paddle(self.paddleImage, 20)
        self.magneticPaddle = True
        
        self.ballStartPos = (self.paddle.pos.centerx+self.paddle.rect.w/10, self.paddle.pos.y-self.ballImage.get_rect().h)
        self.padBallPosX = self.ballStartPos[0]
        self.padBallPosY = self.ballStartPos[1]
        self.ball = Ball(self.ballImage, self.ballStartPos)
        self.ballActive = False
        self.blockCollision = True
        self.ballSpeedX = 10
        self.ballSpeedY = -10
        
        
        if self.font:
            self.scoreString = self.font.render("WYNIK: " + str(self.score), False, (255,255,255))
            self.livesString = self.font.render("1UP: " + str(self.lives), False, (255,255,255))
        
        self.powerup = []
        self.powerupDiffCounter = [0, 0, 0, 0, 0]
        self.powerupDisable()

        self.state = S_PLAY
        self.createBlocks()
        
    def createBlocks(self):
        self.block=[]
        if self.level == 1:
            for iy in range(8):
                for ix in range(12):
                    self.block.append(Block(self.blockImage[iy%5], (16+64*ix,100+iy*self.blockImage[iy%5].get_rect().h)))
        if self.level == 2:
            for iy in range(3):
                for ix in range(12):
                    self.block.append(Block(self.blockImage[(iy+1)%5], (16+64*ix,100+iy*self.blockImage[(iy+1)%5].get_rect().h)))
            for iy in range(3,5):
                for ix in range(12):
                    if ix%2 == 0:
                        self.block.append(Block(self.blockImage[(iy+1)%5], (16+64*ix,100+iy*self.blockImage[(iy+1)%5].get_rect().h)))
                    else:
                        self.block.append(Block(self.blockImage[5], (16+64*ix,100+iy*self.blockImage[5].get_rect().h), 2))
            for iy in range(5,8):
                for ix in range(12):
                    self.block.append(Block(self.blockImage[(iy+1)%5], (16+64*ix,100+iy*self.blockImage[(iy+1)%5].get_rect().h)))
        if self.level == 3:
            for iy in range(0,5,2):
                for ix in range(12):
                    self.block.append(Block(self.blockImage[(iy+3)%5], (16+64*ix,100+iy*self.blockImage[(iy+3)%5].get_rect().h)))
            for iy in range(1,6,2):
                for ix in range(12):
                    self.block.append(Block(self.blockImage[5], (16+64*ix,100+iy*self.blockImage[5].get_rect().h), 2))
            

    def checkInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
               event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and (
                 self.state in [S_WIN, S_GAMEOVER]):
                self.state = S_MENU
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == S_MENU:
                    self.lives = 3
                    self.score = 0
                    self.level = 1
                    self.startGame()
                elif self.state == S_PLAY:
                    if self.magneticPaddle == True:
                        self.magneticPaddle = False
                        self.ballActive = True
                        if self.powerupDiffCounter[1] == 1:
                            self.magneticPaddle = True
        
    def redrawBackground(self):
        if self.level in [1,2,3]:
            bg = self.background[self.level]
            self.screen.blit(bg, (0,0))
            self.screen.blit(bg, self.paddle.pos, self.paddle.pos)
            self.screen.blit(bg, self.ball.pos, self.ball.pos)
            for j in range(len(self.block)):
                if self.block[j]:
                    self.screen.blit(bg, self.block[j].pos, self.block[j].pos)
            for jp in range(len(self.powerup)):
                if self.powerup[jp]:
                    self.screen.blit(bg, self.powerup[jp].pos, self.powerup[jp].pos)
            self.screen.blit(self.background[4], (0,0),(0,0,WINDOW_SIZE[0],40))
        else:
            bg = self.background[0]
            self.screen.blit(bg, (0,0))
        
                 
    def paddleMovement(self):
        self.paddle.movePad(pygame.mouse.get_pos()[0])
        if self.paddle.pos.left < 0:
            self.paddle.pos.x = 0
        if self.paddle.pos.right > WINDOW_SIZE[0]:
            self.paddle.pos.x = WINDOW_SIZE[0] - self.paddle.rect.w

    def ballMovement(self):
        if self.ballActive:
            self.ball.moveBall(self.ballSpeedX, self.ballSpeedY)
        else:
            self.ball.pos.x = self.paddle.pos.x + self.padBallPosX
            self.ball.pos.y = self.padBallPosY

    def checkCollisions(self):
        if self.ball.pos.left < 0:
            self.ball.pos.x = 0
            self.ballSpeedX = -self.ballSpeedX
        if self.ball.pos.right > WINDOW_SIZE[0]:
            self.ball.pos.x = WINDOW_SIZE[0] - self.ball.rect.w
            self.ballSpeedX = -self.ballSpeedX
        if self.ball.pos.top < 40:
            self.ball.pos.y = 40
            self.ballSpeedY = -self.ballSpeedY
        if self.ball.pos.centery > self.paddle.pos.y+self.paddle.pos.h:
            self.lives -= 1
            self.powerupDisable()
            if self.lives >= 0:
                pygame.mouse.set_pos([WINDOW_SIZE[0]/2, pygame.mouse.get_pos()[1]])
                self.paddleMovement()
                self.ball.pos.x = self.ballStartPos[0]
                self.ballSpeedX = 10
                self.ballSpeedY = -10
                self.magneticPaddle = True
                self.ballActive = False
            else:
                self.state = S_GAMEOVER
        if self.ball.pos.colliderect(self.paddle.pos):
            if self.magneticPaddle == True:    
                self.ballActive = False
            relativePos = self.paddle.pos.centerx - self.ball.pos.centerx
            normRelativePos = relativePos/(self.paddle.rect.w/2)
            bounceAngle = normRelativePos * MAX_ANGLE
            ballSpeedC = math.sqrt(self.ballSpeedX**2+self.ballSpeedY**2)
            self.ballSpeedX = -ballSpeedC * math.sin(bounceAngle)
            self.ballSpeedY = -ballSpeedC * math.cos(bounceAngle)
            
        for k in range(len(self.block)):
            if self.block[k] and self.ball.pos.colliderect(self.block[k].pos):
                if self.blockCollision:
                    if self.ball.pos.centerx > self.block[k].pos.right or self.ball.pos.centerx < self.block[k].pos.left:
                        self.ballSpeedX = -self.ballSpeedX
                    else:
                        self.ballSpeedY = -self.ballSpeedY
                self.powerupDrop(self.block[k].pos)
                block2hp = False
                if self.block[k].hp == 2:
                    block2hp = True
                self.block[k].hp -= 1    
                if self.block[k].hp < 2 and block2hp:
                    self.block[k] = Block(self.blockImage[6], (self.block[k].pos.x, self.block[k].pos.y))
                if self.block[k].hp == 0:
                    self.score += 10
                    self.block.remove(self.block[k])
                break
        
        if len(self.block) == 0:
            self.state = S_LVLCMPL
            
        for np in range(len(self.powerup)):
            if self.powerup[np]:
                if self.paddle.pos.colliderect(self.powerup[np].pos):
                    self.score +=20
                    self.powerupEnable(self.powerup[np].action)
                    self.powerup.remove(self.powerup[np])
                break
            
    def powerupDrop(self, pos):
        dropChance = random.randrange(15)
        if dropChance == 0:
            powerupType = random.randrange(5)
            newPowerup = Powerup(self.powerupImage[powerupType], pos, powerupType)
            self.powerup.append(newPowerup)
            
    def powerupMovement(self):
        for mp in range(len(self.powerup)):
            if self.powerup[mp]:
                self.powerup[mp].movePowerup(3)
                
    def powerupEnable(self, action):
        if action == 0:
            self.lives += 1
        elif action == 1:
            if self.powerupDiffCounter[1] == 0:
                self.magneticPaddle = True
                self.powerupDiffCounter[1] = 1
            if self.powerupDiffCounter[2] == 1:
                self.ballSpeedX *= (3/2)
                self.ballSpeedY *= (3/2)
                self.powerupDiffCounter[2] = 0
            if self.powerupDiffCounter[3] == 1:
                self.blockCollision = True
                self.powerupDiffCounter[3] = 0
            if self.powerupDiffCounter[4] == 1:
                self.paddle = Paddle(self.paddleImage, 20)
                self.powerupDiffCounter[4] = 0
        elif action == 2:
            if self.powerupDiffCounter[1] == 1:
                self.magneticPaddle == False
                self.powerupDiffCounter[1] = 0
            if self.powerupDiffCounter[2] == 0:
                self.ballSpeedX *= (2/3)
                self.ballSpeedY *= (2/3)
                self.powerupDiffCounter[2] = 1
            if self.powerupDiffCounter[3] == 1:
                self.blockCollision = True
                self.powerupDiffCounter[3] = 0
            if self.powerupDiffCounter[4] == 1:
                self.paddle = Paddle(self.paddleImage, 20)
                self.powerupDiffCounter[4] = 0
        elif action == 3:
            if self.powerupDiffCounter[1] == 1:
                self.magneticPaddle == False
                self.powerupDiffCounter[1] = 0
            if self.powerupDiffCounter[2] == 1:
                self.ballSpeedX *= (3/2)
                self.ballSpeedY *= (3/2)
                self.powerupDiffCounter[2] = 0
            if self.powerupDiffCounter[3] == 0:
                self.blockCollision = False
                self.powerupDiffCounter[3] = 1
            if self.powerupDiffCounter[4] == 1:
                self.paddle = Paddle(self.paddleImage, 20)
                self.powerupDiffCounter[4] = 0
        elif action == 4:
            if self.powerupDiffCounter[1] == 1:
                self.magneticPaddle == False
                self.powerupDiffCounter[1] = 0
            if self.powerupDiffCounter[2] == 1:
                self.ballSpeedX *= (3/2)
                self.ballSpeedY *= (3/2)
                self.powerupDiffCounter[2] = 0
            if self.powerupDiffCounter[3] == 1:
                self.blockCollision = True
                self.powerupDiffCounter[3] = 0
            if self.powerupDiffCounter[4] == 0:
                self.paddle = Paddle(self.paddleLongImage, 20)
                self.powerupDiffCounter[4] = 1

    def powerupDisable(self):
        if self.powerupDiffCounter[1] == 1:
            self.magneticPaddle == False
            self.powerupDiffCounter[1] = 0
        if self.powerupDiffCounter[2] == 1:
            self.ballSpeedX *= (3/2)
            self.ballSpeedY *= (3/2)
            self.powerupDiffCounter[2] = 0
        if self.powerupDiffCounter[3] == 1:
            self.blockCollision = True
            self.powerupDiffCounter[3] = 0
        if self.powerupDiffCounter[4] == 1:
            self.paddle = Paddle(self.paddleImage, 20)
            self.powerupDiffCounter[4] = 0
        self.powerupDiffCounter = [0, 0, 0, 0, 0]
            
            
    def drawStats(self):
        if self.font:
            self.scoreString = self.font.render("WYNIK: " + str(self.score), False, (255,255,255))
            self.livesString = self.font.render("1UP: " + str(self.lives), False, (255,255,255))
            self.screen.blit(self.scoreString, (10,5))
            self.screen.blit(self.livesString, (WINDOW_SIZE[0]-110,5))

    def drawPlayFrame(self):
        self.screen.blit(self.paddle.image, self.paddle.pos)
        self.screen.blit(self.ball.image, self.ball.pos)
        for l in range(len(self.block)):
            if self.block[l]:
                self.screen.blit(self.block[l].image, self.block[l].pos)
        for lp in range(len(self.powerup)):
            if self.powerup[lp]:
                self.screen.blit(self.powerup[lp].image, self.powerup[lp].pos)
                
    def menu(self):
        self.screen.blit(self.background[0], (0,0))
        self.screen.blit(self.logoImage, (WINDOW_SIZE[0]/2-self.logoImage.get_rect().w/2,100))
        if self.font:
            self.creditsString = self.crFont.render("v. 1.0 | Karol Stypa 2017 | grafika: kenney.nl", True, (255,255,255))
            self.startString = self.font.render("START - LEWY PRZYCISK MYSZY", True, (255,255,255))
            startStringX = WINDOW_SIZE[0]/2-self.font.size("START - LEWY PRZYCISK MYSZY")[0]/2
            self.escString = self.font.render("WYJŚCIE - ESC", True, (255,255,255))
            self.bonusyString = self.crFont.render("Bonusy:", True, (255,255,255))
            self.bonusyString0 = self.crFont.render("dodatkowe życie", True, (159,206,49))
            self.bonusyString1 = self.crFont.render("magnetyczna paletka", True, (131,29,149))
            self.bonusyString2 = self.crFont.render("wolniejsza piłka", True, (255,204,0))
            self.bonusyString3 = self.crFont.render("przebijająca piłka", True, (242,55,55))
            self.bonusyString4 = self.crFont.render("dłuższa paletka", True, (74,191,240))
            self.screen.blit(self.startString, (startStringX, 310))
            self.screen.blit(self.escString, (startStringX, 350))
            self.screen.blit(self.creditsString, (10, WINDOW_SIZE[1]-28))
            self.screen.blit(self.bonusyString, (startStringX, 405))
            self.screen.blit(self.bonusyString0, (startStringX, 430))
            self.screen.blit(self.bonusyString1, (startStringX, 450))
            self.screen.blit(self.bonusyString2, (startStringX, 470))
            self.screen.blit(self.bonusyString3, (startStringX, 490))
            self.screen.blit(self.bonusyString4, (startStringX, 510))
                
    def drawSuccessScreen(self):
        if self.font:
            self.winString = self.font.render("GRATULACJE - UKONCZYŁEŚ GRĘ!", True, (255,255,255))
            self.escString = self.font.render("ESC - WYJŚCIE", True, (255,255,255))
            self.spaceString = self.font.render("SPACJA - ZACZNIJ OD POCZĄTKU", True, (255,255,255))
            self.screen.blit(self.background[0], (0,0))
            self.screen.blit(self.winString, (75,200))
            self.screen.blit(self.scoreString, (75,240))
            self.screen.blit(self.escString, (75,440))
            self.screen.blit(self.spaceString, (75,480))
            
    def drawGameOver(self):
        if self.font:
            self.gameOverString = self.font.render("KONIEC GRY - PRZEGRAŁEŚ", True, (255,255,255))
            self.escString = self.font.render("ESC - WYJŚCIE", True, (255,255,255))
            self.spaceString = self.font.render("SPACJA - ZACZNIJ OD POCZĄTKU", True, (255,255,255))
            self.screen.blit(self.background[0], (0,0))
            self.screen.blit(self.gameOverString, (75,200))
            self.screen.blit(self.scoreString, (75,240))
            self.screen.blit(self.escString, (75,440))
            self.screen.blit(self.spaceString, (75,480))
        
        
    def runLoop(self):
        while True:
            self.clock.tick(60)
            
            if self.state == S_MENU:
                self.menu()
                
            if self.state == S_LVLCMPL:
                self.level += 1
                if self.level > 3:
                    self.state = S_WIN
                else:
                    self.redrawBackground()
                    self.startGame()
            
            self.checkInput()
            if self.state != S_MENU:
             self.redrawBackground()
            
            if self.state == S_PLAY:
                self.padBallPosX = self.ball.pos.x - self.paddle.pos.x
                self.paddleMovement()
                self.ballMovement()
                self.powerupMovement()
                self.checkCollisions()
                self.drawStats()
                self.drawPlayFrame()
            elif self.state == S_WIN:
                self.drawSuccessScreen()
            elif self.state == S_GAMEOVER:
                self.drawGameOver()
                
            pygame.display.update()
            
if __name__ == "__main__":
    game = Game()
    game.runLoop()