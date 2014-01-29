import pygame, math
import drawable, scripting
from constants import *

class Hitbox(pygame.Rect):
  """Basically just a rename of pygame.Rect"""
  def __init__(self, left, top, width, height):
    """Left, top is the offset from the logical center of the entity"""
    super(Hitbox, self).__init__(left, top, width, height)

class Bounds(pygame.Rect):
  """The bounds that the entity can't move out of"""
  def __init__(self, left, top, width, height):
    super(Bounds, self).__init__(left, top, width, height)    

class Entity(drawable.Drawable):
  """Base class for all entities that interact with each other via collisions"""
  def __init__(self, handler):
    super(Entity, self).__init__(60, 60)
    self.hitbox = None # TODO this should be a hitbox
    self.collidable = True # Entity can call 'collide' on others
    self.dead = False # Remove from screen on next update?
    self.xvel = 0
    self.yvel = 0
    self.angle = 0
    self.speed = 0

    # Bounds stuff
    self.boundsChecked = True # Call die() if out of bounds
    self.bounds = Bounds(GAMEOFFSET, GAMEOFFSET, GAMEXWIDTH, GAMEYWIDTH)
    self.bounds.inflate_ip(50, 50) # Default bounds for non-players
    self.handler = handler
    self.scripter = scripting.EntityScripter()
    self.scripter.setEntity(self)

  def update(self):
    self._runScript()
    self._updateMovement()
    self._special()

    # Kill on OOB
    if self.boundsChecked and not self.bounds.contains(self.hitbox):
      self.die()

  def isCollide(self, other):
    return self.collidable and other.hitbox.colliderect(self.hitbox)

  def collide(self, other):
    print "Collided!"

  def setScript(self, script):
    self.scripter = script

  def setX(self, x):
    self.x = x
    self.hitbox.x = x

  def setY(self, y):
    self.y = y
    self.hitbox.y = y

  def die(self):
    # Death logic, usually playing an animation and removing self from screen
    # TODO: Animation!
    self.collidable = False
    self.dead = True

  def _special(self):
    pass

  def _runScript(self):
    self.scripter.execute()

  def _updateMovement(self):
    # Update velocities according to angle and speed
    self.xvel = math.cos(self.angle) * self.speed
    self.yvel = -math.sin(self.angle) * self.speed

    self.x += self.xvel
    self.y += self.yvel

    # Move by X
    self.hitbox.x = math.floor(self.x)
    # Move by Y
    self.hitbox.y = math.floor(self.y)

class Player(Entity):
  def __init__(self, handler):
    super(Player, self).__init__(handler)
    self.x = 0
    self.y = 0
    self.hitbox = Hitbox(0, 0, 20, 20)
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((255,255,255))

    # Players are more strictly bounded than other entities
    self.bounds = Bounds(GAMEOFFSET, GAMEOFFSET, GAMEXWIDTH, GAMEYWIDTH)

  def _updateMovement(self):
    # Move by X
    self.x += self.xvel
    self.hitbox.x = math.floor(self.x)
    # Move by Y
    self.y += self.yvel
    self.hitbox.y = math.floor(self.y)

    if not self.bounds.contains(self.hitbox):
      # The hitbox has left the area! Put it back!
      self.hitbox.clamp_ip(self.bounds)
      (self.x, self.y) = (self.hitbox.x, self.hitbox.y)

    # Reset velocity
    self.xvel = 0
    self.yvel = 0

  def collide(self, other):
    pass

class Enemy(Entity):
  def __init__(self, handler):
    super(Enemy, self).__init__(handler)
    self.x = 60
    self.y = 60
    self.hitbox = Hitbox(self.x, self.y, 20, 20)
    self.angle = 0
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((0,255,0))

  def collide(self, other):
    print "Enemy collide!"

class Bullet(Entity):
  def __init__(self, handler):
    super(Bullet, self).__init__(handler)
    self.x = 300
    self.y = 300
    self.hitbox = Hitbox(self.x, self.y, 5, 5)
    self.angle = math.radians(1)
    self.speed = 2
    self.image = pygame.Surface((self.hitbox.w, self.hitbox.h))
    self.image.fill((0,0,255))

  def collide(self, other):
    print "Bullet collide!"

class Boss(Enemy):
  def __init__(self, handler):
    super(Boss, self).__init__(handler)

  def collide(self, other):
    "Man, don't touch the boss!"