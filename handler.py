import pygame, math, time, thread
import inputHandler, drawable, entity, scripting, levels

from threading import Thread
from constants import *

from game import Game

# Helper functions
# This one sucks and will be replaced I think
def fadeToHandler(screen, speed, destinationHandler, game):
  if screen.get_alpha() > 0:
    screen.set_alpha(screen.get_alpha() - speed)
  else:
    game.handler = destinationHandler

class Handler(object):
  # Handlers are the wrappers for the more separated parts of the game,
  # like the title screen, the main game screen, the game over..
  def __init__(self, game):
    self.game = game
    self.running = True

  def update(self):
    print("Default handler")
    return True

def dummyCallback(handler):
  time.sleep(5)

# Seriously this should be moved somewhere nicer
class TextElement(drawable.Drawable):
  class Alignments:
    Left, Center = range(2)

  def __init__(self, x, y, text):
    super(TextElement, self).__init__(x, y)
    self.text = text
    font = pygame.font.Font(None, 24)
    self.renderText = font.render(text, 1, (255,255,255))
    self.textPos = self.renderText.get_rect(centerx=x, y=y)
    self.fontSize = 24
    self.alignment = TextElement.Alignments.Center

  def setText(self, text):
    self.text = text
    font = pygame.font.Font(None, self.fontSize)
    self.renderText = font.render(text, 1, (255,255,255))
    if self.alignment == TextElement.Alignments.Left:
      self.textPos = self.renderText.get_rect(x=self.x, y=self.y)
    elif self.alignment == TextElement.Alignments.Center:
      self.textPos = self.renderText.get_rect(centerx=self.x, y=self.y)

  def setFontSize(self, size):
    self.fontSize = size
    self.setText(self.text)

  def setLeftAligned(self):
    self.alignment = TextElement.Alignments.Left
    self.setText(self.text)

  def setCenterAligned(self):
    self.alignment = TextElement.Alignments.Center
    self.setText(self.text)



class LoadingScreenHandler(Handler):
  def __init__(self, game, nextHandler, assetsToLoad):
    super(LoadingScreenHandler, self).__init__(game)
    # Loading stuff
    self.nextHandler = nextHandler
    self.assetsToLoad = assetsToLoad
    self.thread = Thread(target=dummyCallback, args=(self,))
    # Start loading on initialisation, maybe this will get moved
    self.thread.start()

    # Display stuff!
    self.background = pygame.Surface(self.game.screen.get_size())
    self.background = self.background.convert()
    self.background.fill((50, 50, 50))

    self.title = TextElement(self.game.xRes // 2, 150, "Loading")
    self.title.setFontSize(42)

  def _draw(self):
    # Print background and loading text
    self.game.screen.blit(self.background, (0,0))
    self.game.screen.blit(self.title.renderText, self.title.textPos)

  def _handleInput(self):
    # Pump the event queue so we don't get any nasty surprises after loading.
    pygame.event.clear()

  def _logic(self):
    # Loading finished? Transition to next handler.
    if not self.thread.isAlive():
      fadeToHandler(self.background, 3, self.nextHandler, self.game)

  def update(self):
    self._draw()
    self._logic()
    self._handleInput()
    return True

class TitleScreenHandler(Handler):

  class Button(TextElement):
    def __init__(self, x, y, text, func):
      super(TitleScreenHandler.Button, self).__init__(x, y, text)
      self.text = text
      self.selected = False
      self.func = func

    def _draw(self): # TODO: Do we need this?
      pass

    def run(self):
      if self.func:
        self.func()
      else:
        print("No stuff!")

    def update(self):
      pass

    def toggleSelect(self):
      self.selected = not self.selected
      if (self.selected):
        self.setFontSize(28)
      else:
        self.setFontSize(24)


  def __init__(self, game):
    super(TitleScreenHandler, self).__init__(game)
    self.inputHandler = inputHandler.InputHandler()
    self.inputHandler.addEventCallback(self._inputQuit, pygame.K_q, pygame.KEYDOWN)
    self.inputHandler.addEventCallback(self._inputQuit, pygame.K_ESCAPE, pygame.KEYDOWN)
    self.inputHandler.setQuitCallback(self._inputQuit)

    self.inputHandler.addEventCallback(self._selectionUp, pygame.K_UP, pygame.KEYDOWN)
    self.inputHandler.addEventCallback(self._selectionDown, pygame.K_DOWN, pygame.KEYDOWN)
    self.inputHandler.addEventCallback(self._runSelection, pygame.K_RETURN, pygame.KEYDOWN)

    self.background = pygame.Surface(self.game.screen.get_size())
    self.background = self.background.convert()
    self.background.fill((50, 50, 50))

    self.title = TextElement(self.game.xRes // 2, 150, "The Hullet Bells")
    self.title.setFontSize(42)

    self.buttons = [TitleScreenHandler.Button(self.game.xRes // 2, 300, "Start Game", self._startGame),
                    TitleScreenHandler.Button(self.game.xRes // 2, 400, "Quit", self._inputQuit)]
    self.selected = 0
    self.buttons[self.selected].toggleSelect()

  def _inputQuit(self):
    self.running = False

  def _startGame(self):
    # Start with level one!
    gameScreenHandler = GameScreenHandler(self.game, self.game.levels[0])
    loadingScreenHandler = LoadingScreenHandler(self.game, gameScreenHandler, None)
    #fadeToHandler(self.game.screen, 0.1, loadingScreenHandler, self.game)
    fadeToHandler(self.game.screen, 0.1, gameScreenHandler, self.game)

  def _selectionUp(self):
    self.buttons[self.selected].toggleSelect()
    self.selected -= 1
    self.selected = (len(self.buttons) - 1) if (self.selected < 0) else self.selected
    self.buttons[self.selected].toggleSelect()
    print(self.selected)

  def _selectionDown(self):
    self.buttons[self.selected].toggleSelect()
    self.selected += 1
    self.selected = self.selected % len(self.buttons)
    self.buttons[self.selected].toggleSelect()
    print(self.selected)

  def _runSelection(self):
    self.buttons[self.selected].run()

  def _drawTitle(self):
    self.game.screen.blit(self.title.renderText, self.title.textPos)

  def _drawText(self):
    for button in self.buttons:
      self.game.screen.blit(button.renderText, button.textPos)

  def _draw(self):
    self.game.screen.blit(self.background, (0,0))
    self._drawText()
    self._drawTitle()

  def _logic(self):
    for button in self.buttons:
      button.update()

  def _handleInput(self):
    self.inputHandler.update()

  def update(self):
    self._draw()
    self._logic()
    self._handleInput()
    return self.running


class GameScreenHandler(Handler):
# TODO factor out the inner classes

# TODO: Write the UI
  class Ui(object):
    """Encapsulates the static and dynamic elements of the game screen's UI,
       does not include the 'action' screen itself"""
    def __init__(self, game):
      self.background = pygame.Surface(game.screen.get_size())
      self.background = self.background.convert()
      self.background.fill((0, 0, 0))
      self.game = game

      self.fpsDisplay = TextElement(game.xRes * 3 // 4, 150, "FPS: ")
      self.fpsDisplay.setFontSize(24)
      self.fpsDisplay.setLeftAligned()

    def update(self):
      self.fpsDisplay.setText("FPS: " + str(self.game.clock.get_fps()))

    def draw(self, screen):
      screen.blit(self.background, (0,0))
      screen.blit(self.fpsDisplay.renderText, self.fpsDisplay.textPos)

# TODO: Finish the player stuff
# TODO: Decide if we'll end up using pygame.Sprite as the base for drawable
#       and use self.rect as the hitbox, or if we'll roll our own collision
#       and only use pygame.Sprite for drawing groups, or if we'll even
#       roll our own drawing loops.
  def __init__(self, game, level):
    super(GameScreenHandler, self).__init__(game)
    self.inputHandler = inputHandler.InputHandler()
    self.inputHandler.addEventCallback(self._inputQuit, pygame.K_q, pygame.KEYDOWN)
    self.inputHandler.addEventCallback(self._inputQuit, pygame.K_ESCAPE, pygame.KEYDOWN)
    self.inputHandler.setQuitCallback(self._inputQuit)

#   Order matters for focus + movement, should fix this
    self.inputHandler.addPerFrameCallback(self._focus, pygame.K_LSHIFT)
    self.inputHandler.addPerFrameCallback(self._moveRight, pygame.K_RIGHT)
    self.inputHandler.addPerFrameCallback(self._moveLeft, pygame.K_LEFT)
    self.inputHandler.addPerFrameCallback(self._moveUp, pygame.K_UP)
    self.inputHandler.addPerFrameCallback(self._moveDown, pygame.K_DOWN)
    self.inputHandler.addPerFrameCallback(self._shootBullet, pygame.K_z)

    self.ui = GameScreenHandler.Ui(self.game)

    self.gameBackground = pygame.Surface((GAMEXWIDTH, GAMEYWIDTH))
    self.gameBackground = self.gameBackground.convert()
    self.gameBackground.fill((50, 50, 50))

    (self.levelScripter, _) = level()
    self.levelScripter.setHandler(self)

    self.player = entity.Player(self)
    self.player.setX(50)
    self.player.setY(50)
    self.enemies = []
    self.bullets = []
    self.playerBullets = []

    # Hack:
    self.cooldown = 0

    self.focused = False

    self.running = True

  def _inputQuit(self):
    self.running = False

  def _drawText(self):
    pass

  def _draw(self):
    self.ui.draw(self.game.screen)
    self.game.screen.blit(self.gameBackground, (GAMEOFFSET,GAMEOFFSET))
    self.game.screen.blit(self.player.image, (self.player.hitbox.x, self.player.hitbox.y))

    for enemy in self.enemies:
      self.game.screen.blit(enemy.image, (enemy.hitbox.x, enemy.hitbox.y))
    for bullet in self.bullets:
      self.game.screen.blit(bullet.image, (bullet.hitbox.x, bullet.hitbox.y))
    for playerBullet in self.playerBullets:
       self.game.screen.blit(playerBullet.image, (playerBullet.hitbox.x, playerBullet.hitbox.y))

    self._drawText()

  def _logic(self):
    # Collisions, individual entity updates, then resets
    self._checkCollisions()
    self.player.update()
    for enemy in self.enemies:
      enemy.update()
    for bullet in self.bullets:
      bullet.update()
    for playerBullet in self.playerBullets:
      playerBullet.update()

    # Clean up the dead
    self.enemies = [enemy for enemy in self.enemies if not enemy.dead]
    self.bullets = [bullets for bullets in self.bullets if not bullets.dead]
    self.playerBullets = [playerBullets for playerBullets in self.playerBullets if not playerBullets.dead]

  def _updateUi(self):
    self.ui.update()

  def _reset(self):
    self.focused = False

  def _checkCollisions(self):
    # Check player + enemy collisions
    for enemy in self.enemies:
      if enemy.isCollide(self.player):
        enemy.collide(self.player)
        self.player.collide(enemy)

    # Check player + bullet collisions
    for bullet in self.bullets:
      if bullet.isCollide(self.player):
        bullet.collide(self.player)
        self.player.collide(bullet)

    # Check bullet + enemy collisions
    # This is going to be expensive and should be optimised, maybe using
    # subgrids
    for playerBullet in self.playerBullets:
      for enemy in self.enemies:
        if playerBullet.isCollide(enemy):
          playerBullet.collide(enemy)
          enemy.collide(playerBullet)

  # Input stuff
  # TODO: These should probably be more like self.player.setXVel() etc
  def _handleInput(self):
    self.inputHandler.update()
    # Adjust velocities if diagonal movement (or not, this seems to suck)
    if ADJUSTDIAGONAL:
      if (self.player.xvel != 0 and self.player.yvel != 0):
        self.player.xvel = math.copysign(math.sqrt(math.fabs(self.player.xvel) * 2), self.player.xvel)
        self.player.yvel = math.copysign(math.fabs(self.player.xvel), self.player.yvel)

  def _moveUp(self):
    # Replace by constants
    if (self.focused):
      self.player.yvel += -2
    else:
      self.player.yvel += -6

  def _moveDown(self):
    if (self.focused):
      self.player.yvel += 2
    else:
      self.player.yvel += 6

  def _moveLeft(self):
    if (self.focused):
      self.player.xvel += -2
    else:
      self.player.xvel += -6

  def _moveRight(self):
    if (self.focused):
      self.player.xvel += 2
    else:
      self.player.xvel += 6

  def _shootBullet(self):
    # Shoot dah bullet!
    # In reality, the player should have a script like enemies do
    # and this function will just perform a frame of the script
    if self.cooldown >= 5:
      bullet = self.createPlayerBullet()
      bullet.angle = math.pi / 2
      bullet.speed = 10
      bullet.hitbox.centerx = self.player.hitbox.centerx
      bullet.hitbox.centery = self.player.hitbox.centery
      bullet.x = bullet.hitbox.x
      bullet.y = bullet.hitbox.y
      self.cooldown = 0
    self.cooldown += 1
  # 'Clever' hack so this half-finished function doesn't look super dumb

  def _focus(self):
    self.focused = True

  def _unFocus(self):
    self.focused = False

  # Script stuff

  def _runScript(self):
    self.levelScripter.execute()

  def createEnemy(self):
    enemy = entity.Enemy(self)
    self.enemies.append(enemy)
    return enemy

  def createBullet(self):
    bullet = entity.Bullet(self)
    self.bullets.append(bullet)
    return bullet

  def createPlayerBullet(self):
    bullet = entity.Bullet(self)
    self.playerBullets.append(bullet)
    return bullet

  # Updates
  def update(self):
    self._draw()
    self._runScript()
    self._handleInput()
    self._logic()
    self._updateUi()
    self._reset()
    return self.running
