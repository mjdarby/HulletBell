import pygame, math
import inputHandler, drawable, entity

from threading import Thread
from constants import *

from game import Game

# Helper functions
# This one sucks and will be replaced I think
def fadeToHandler(screen, speed, destinationHandler, game):
  if screen.get_alpha() > 0:
    screen.set_alpha(screen.get_alpha() - speed)
  else:
    game.crossHandlerKeys = list(pygame.key.get_pressed())
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

class TitleScreenHandler(Handler):

  class Button(drawable.Drawable):
    def __init__(self, x, y, text, func):
      super(TitleScreenHandler.Button, self).__init__(x, y)
      self.text = text
      self.selected = False
      self.func = func
      # To be replaced by an Animation?
      font = pygame.font.Font(None, 24)
      self.renderText = font.render(text, 1, (255,255,255))
      self.textPos = self.renderText.get_rect(centerx=x, centery=y)

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
        font = pygame.font.Font(None, 28)
        self.renderText = font.render(self.text, 1, (255,255,255))
        self.textPos = self.renderText.get_rect(centerx=self.x, centery=self.y)
      else:
        font = pygame.font.Font(None, 24)
        self.renderText = font.render(self.text, 1, (255,255,255))
        self.textPos = self.renderText.get_rect(centerx=self.x, centery=self.y)


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

    self.buttons = [TitleScreenHandler.Button(self.game.xRes // 2, 300, "Start Game", self._startGame),
                    TitleScreenHandler.Button(self.game.xRes // 2, 400, "Quit", self._inputQuit)]
    self.selected = 0
    self.buttons[self.selected].toggleSelect()

  def _inputQuit(self):
    self.running = False

  def _startGame(self):
    fadeToHandler(self.game.screen, 0.1, GameScreenHandler(self.game), self.game)

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

  def _drawText(self):
    for button in self.buttons:
      self.game.screen.blit(button.renderText, button.textPos)

  def _draw(self):
    self.game.screen.blit(self.background, (0,0))
    self._drawText()

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

# TODO: Finish the player stuff
# TODO: Decide if we'll end up using pygame.Sprite as the base for drawable
#       and use self.rect as the hitbox, or if we'll roll our own collision
#       and only use pygame.Sprite for drawing groups, or if we'll even
#       roll our own drawing loops.
  class Player(entity.Entity):
    def __init__(self):
      super(GameScreenHandler.Player, self).__init__()
      self.hitbox = entity.Hitbox(0, 0, 20, 20)
      self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
      self.image.fill((255,255,255))

    def _updateMovement(self):
      # Move by X
      self.hitbox.x += self.xvel
      # Move by Y
      self.hitbox.y += self.yvel

      if not self.bounds.contains(self.hitbox):
        # The hitbox has left the area! Put it back!
        self.hitbox.clamp_ip(self.bounds)
        pass

      # Reset velocity
      self.xvel = 0
      self.yvel = 0

  class Enemy(entity.Entity):
    def __init__(self):
      super(GameScreenHandler.Enemy, self).__init__()
      self.hitbox = entity.Hitbox(60, 60, 20, 20)
      self.angle = 0
      self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
      self.image.fill((0,255,0))

  class Bullet(entity.Entity):
    def __init__(self):
      super(GameScreenHandler.Bullet, self).__init__()
      self.hitbox = entity.Hitbox(60, 60, 5, 5)
      self.angle = math.radians(315)
      self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
      self.image.fill((0,0,255))

  def __init__(self, game):
    super(GameScreenHandler, self).__init__(game)
    self.inputHandler = inputHandler.InputHandler()
    self.inputHandler.addEventCallback(self._inputQuit, pygame.K_q, pygame.KEYDOWN)
    self.inputHandler.addEventCallback(self._inputQuit, pygame.K_ESCAPE, pygame.KEYDOWN)
    self.inputHandler.setQuitCallback(self._inputQuit)

#   Order matters for focus + movement, should fix this
    self.inputHandler.addPerFrameCallback(self._focus, pygame.K_LSHIFT)
#    self.inputHandler.addEventCallback(self._focus,   pygame.K_LSHIFT, pygame.KEYDOWN)
#    self.inputHandler.addEventCallback(self._unFocus, pygame.K_LSHIFT, pygame.KEYUP)


    self.inputHandler.addPerFrameCallback(self._moveRight, pygame.K_RIGHT)
    self.inputHandler.addPerFrameCallback(self._moveLeft, pygame.K_LEFT)
    self.inputHandler.addPerFrameCallback(self._moveUp, pygame.K_UP)
    self.inputHandler.addPerFrameCallback(self._moveDown, pygame.K_DOWN)

    self.ui = GameScreenHandler.Ui(self.game)

    self.gameBackground = pygame.Surface((GAMEXWIDTH, GAMEYWIDTH))
    self.gameBackground = self.gameBackground.convert()
    self.gameBackground.fill((50, 50, 50))

    self.player = GameScreenHandler.Player()
    self.enemy = GameScreenHandler.Enemy()
    self.bullet = GameScreenHandler.Bullet()

    self.focused = False

    self.running = True

  def _inputQuit(self):
    self.running = False

  def _drawText(self):
    pass

  def _draw(self):
    self.game.screen.blit(self.ui.background, (0,0))
    self.game.screen.blit(self.gameBackground, (GAMEOFFSET,GAMEOFFSET))
    self.game.screen.blit(self.player.image, (self.player.hitbox.x, self.player.hitbox.y))
    self.game.screen.blit(self.enemy.image, (self.enemy.hitbox.x, self.enemy.hitbox.y))
    self.game.screen.blit(self.bullet.image, (self.bullet.hitbox.x, self.bullet.hitbox.y))
    self._drawText()

  def _logic(self):
    # Collisions, individual entity updates, then resets
    self._checkCollisions()
    self.player.update()
    self.enemy.update()
    self.bullet.update()

  def _reset(self):
    self.focused = False

  def _checkCollisions(self):
    # Check player + enemy collisions
    # TODO: For each enemy..
    if self.enemy.isCollide(self.player):
      self.enemy.collide(self.player)
      self.player.collide(self.enemy)
    # Check player + bullet collisions
    if self.bullet.isCollide(self.player):
      self.bullet.collide(self.player)
      self.player.collide(self.bullet)
    # Check bullet + enemy collisions
    pass

  # Input stuff
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

  def _focus(self):
    self.focused = True

  def _unFocus(self):
    self.focused = False

  # Updates
  def update(self):
    self._draw()
    self._handleInput()
    self._logic()
    self._reset()
    return self.running
